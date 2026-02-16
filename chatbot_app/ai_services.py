"""
Abstracted AI service layer for multiple providers.
Supports Gemini, OpenRouter, and easy switching between providers.
"""

import time
import logging
import httpx
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union
from django.conf import settings
from google import genai
from google.genai import errors
from .observability import observability

logger = logging.getLogger(__name__)


class AIServiceBase(ABC):
    """Base class for all AI services."""

    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.timeout = kwargs.get("timeout", 30.0)
        self.max_retries = kwargs.get("max_retries", 3)
        self.retry_delay = kwargs.get("retry_delay", 1.0)

    @abstractmethod
    async def generate_response(
        self,
        message: Union[str, List[Dict[str, Any]]],
        tools: list[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate AI response.
        Returns a dict with:
        - 'content': str (The text response)
        - 'tool_calls': list (Optional tool calls)
        """
        pass

    @abstractmethod
    def validate_api_key(self) -> bool:
        """Validate the API key is working."""
        pass

    def _retry_with_backoff(self, func, *args, **kwargs):
        """Implement exponential backoff retry logic."""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.NetworkError) as e:
                if attempt == self.max_retries - 1:
                    raise e

                delay = self.retry_delay * (2**attempt)  # Exponential backoff
                logger.warning(
                    f"Attempt {attempt + 1} failed, retrying in {delay}s: {str(e)}"
                )
                time.sleep(delay)
            except Exception as e:
                # Don't retry on non-timeout errors
                raise e


class GeminiService(AIServiceBase):
    """Google Gemini AI service."""

    def __init__(self, api_key: str, model: str = "models/gemini-2.5-flash", **kwargs):
        super().__init__(api_key, **kwargs)
        self.model = model
        self.client = genai.Client(
            api_key=api_key, http_options={"timeout": self.timeout}
        )

    async def generate_response(
        self,
        message: Union[str, List[Dict[str, Any]]],
        tools: list[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate response using Gemini API."""

        def _call_api():
            # Note: Gemini native tools implementation omitted for brevity in this phase
            # fallback to text only for now if tools provided, or implement later
            response = self.client.models.generate_content(
                model=self.model, contents=message
            )
            return {"content": response.text, "tool_calls": None}

        try:
            return self._retry_with_backoff(_call_api)
        except (httpx.ConnectTimeout, httpx.ReadTimeout) as e:
            logger.error(f"Gemini API timeout: {str(e)}")
            raise
        except errors.ClientError as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Gemini unexpected error: {str(e)}")
            raise

    def validate_api_key(self) -> bool:
        """Validate Gemini API key."""
        try:
            # Use a shorter timeout for validation
            client = genai.Client(
                api_key=self.api_key,
                http_options={"timeout": 5.0},  # Shorter timeout for validation
            )
            response = client.models.generate_content(
                model=self.model, contents="Hello"
            )
            return True
        except Exception as e:
            # Don't fail validation on timeout - let it try at runtime
            error_msg = str(e).lower()
            if "timeout" in error_msg or "timed out" in error_msg:
                logger.warning(
                    f"Gemini API key validation timed out (will try at runtime): {str(e)}"
                )
                return True  # Assume valid if it's just a timeout
            else:
                logger.error(f"Gemini API key validation failed: {str(e)}")
                return False


class OpenRouterService(AIServiceBase):
    """OpenRouter AI service (supports multiple models)."""

    def __init__(self, api_key: str, model: str = "anthropic/claude-3-haiku", **kwargs):
        super().__init__(api_key, **kwargs)
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"

    async def generate_response(
        self,
        message: Union[str, List[Dict[str, Any]]],
        tools: list[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate response using OpenRouter API."""

        def _call_api():
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://127.0.0.1:8000",
                "X-Title": "Chatbot Application",
            }

            data = {
                "model": self.model,
                "messages": message
                if isinstance(message, list)
                else [{"role": "user", "content": message}],
                "max_tokens": 1000,
                "temperature": 0.7,
            }
            if tools:
                data["tools"] = tools

            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions", headers=headers, json=data
                )
                response.raise_for_status()

                result = response.json()
                try:
                    msg = result["choices"][0]["message"]
                    return {
                        "content": msg.get("content", ""),
                        "tool_calls": msg.get("tool_calls"),
                    }
                except (KeyError, IndexError, TypeError) as parse_err:
                    raise ValueError(
                        f"Unexpected response format: {parse_err}. Response keys: {list(result.keys()) if isinstance(result, dict) else 'non-dict'}"
                    )

        try:
            return self._retry_with_backoff(_call_api)
        except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.NetworkError) as e:
            logger.error(f"OpenRouter API timeout: {str(e)}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(
                f"OpenRouter API error ({e.response.status_code}): {e.response.text}"
            )
            raise
        except Exception as e:
            logger.error(f"OpenRouter unexpected error: {str(e)}")
            raise

    def validate_api_key(self) -> bool:
        """Validate OpenRouter API key."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10,
            }

            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions", headers=headers, json=data
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"OpenRouter API key validation failed: {str(e)}")
            return False


class GroqService(AIServiceBase):
    """Groq Cloud API service for ultra-fast Llama 3 models."""

    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant", **kwargs):
        super().__init__(api_key, **kwargs)
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1"

    async def generate_response(
        self,
        message: Union[str, List[Dict[str, Any]]],
        tools: list[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate response using Groq API.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": message
            if isinstance(message, list)
            else [{"role": "user", "content": message}],
            "temperature": 0.7,
            "max_tokens": 1024,
        }
        if tools:
            data["tools"] = tools
            data["tool_choice"] = "auto"

        def make_request():
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions", headers=headers, json=data
                )
                response.raise_for_status()
                result = response.json()
                try:
                    msg = result["choices"][0]["message"]
                    return {
                        "content": msg.get("content", ""),
                        "tool_calls": msg.get("tool_calls"),
                    }
                except (KeyError, IndexError, TypeError) as parse_err:
                    raise ValueError(
                        f"Unexpected response format: {parse_err}. Response keys: {list(result.keys()) if isinstance(result, dict) else 'non-dict'}"
                    )

        return self._retry_with_backoff(make_request)

    async def transcribe_audio(self, audio_file) -> str:
        """
        Transcribe audio using Groq's Whisper API.
        """
        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        # Read file content safely
        content = audio_file.read()
        files = {"file": ("audio.webm", content, "audio/webm")}
        data = {"model": "distil-whisper-large-v3-en", "response_format": "json"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, headers=headers, files=files, data=data, timeout=30.0
                )

            if response.status_code == 200:
                result = response.json()
                return result.get("text", "")
            else:
                logger.error(f"Groq Transcription error: {response.text}")
                return ""

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""

    def validate_api_key(self) -> bool:
        """Validate Groq API key."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5,
            }

            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions", headers=headers, json=data
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Groq API key validation failed: {str(e)}")
            return False


class AIServiceManager:
    """Manages multiple AI services with fallback support."""

    def __init__(self):
        self.services = []
        self.current_service_index = 0
        self._initialize_services()

    def _initialize_services(self):
        """Initialize available AI services based on configuration."""

        # Get primary service preference
        primary_service = getattr(settings, "AI_PRIMARY_SERVICE", "groq")

        # Groq Service (Primary - Global Access)
        groq_key = getattr(settings, "GROQ_API_KEY", None) or os.getenv("GROQ_API_KEY")
        if groq_key:
            try:
                groq_service = GroqService(
                    api_key=groq_key,
                    model=getattr(settings, "GROQ_MODEL", "llama3-8b-8192"),
                    timeout=getattr(settings, "AI_TIMEOUT", 30.0),
                    max_retries=getattr(settings, "AI_MAX_RETRIES", 3),
                )
                if groq_service.validate_api_key():
                    self.services.append(groq_service)
                    logger.info("Groq service initialized successfully (Primary)")
                    # Set as primary if it's the preferred service
                    if primary_service == "groq":
                        self.current_service_index = 0
                else:
                    logger.warning("Groq API key validation failed")
            except Exception as e:
                logger.error(f"Failed to initialize Groq service: {str(e)}")

        # OpenRouter Service (Backup - Global Access)
        openrouter_key = getattr(settings, "OPENROUTER_API_KEY", None)
        if openrouter_key:
            try:
                openrouter_service = OpenRouterService(
                    api_key=openrouter_key,
                    model=getattr(
                        settings, "OPENROUTER_MODEL", "anthropic/claude-3-haiku"
                    ),
                    timeout=getattr(settings, "AI_TIMEOUT", 30.0),
                    max_retries=getattr(settings, "AI_MAX_RETRIES", 3),
                )
                if openrouter_service.validate_api_key():
                    self.services.append(openrouter_service)
                    logger.info("OpenRouter service initialized successfully (Backup)")
                    # Set as primary if it's the preferred service
                    if primary_service == "openrouter":
                        self.current_service_index = len(self.services) - 1
                else:
                    logger.warning("OpenRouter API key validation failed")
            except Exception as e:
                logger.error(f"Failed to initialize OpenRouter service: {str(e)}")

        # Gemini Service (Regional - May Not Be Available)
        gemini_key = getattr(settings, "GEMINI_API_KEY", None)
        if gemini_key:
            try:
                gemini_service = GeminiService(
                    api_key=gemini_key,
                    model=getattr(settings, "GEMINI_MODEL", "models/gemini-2.5-flash"),
                    timeout=getattr(settings, "AI_TIMEOUT", 30.0),
                    max_retries=getattr(settings, "AI_MAX_RETRIES", 3),
                )
                if gemini_service.validate_api_key():
                    self.services.append(gemini_service)
                    logger.info("Gemini service initialized successfully (Regional)")
                    # Set as primary if it's the preferred service
                    if primary_service == "gemini":
                        self.current_service_index = len(self.services) - 1
                else:
                    logger.warning("Gemini API key validation failed")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini service: {str(e)}")

        if not self.services:
            logger.error("No AI services are available!")

    @observability.trace(name="ai_manager_generate")
    async def generate_response(
        self,
        message: Union[str, List[Dict[str, Any]]],
        tools: list[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate response using available AI services with fallback."""
        if not self.services:
            raise Exception("No AI services available")

        # Try current service first
        for attempt in range(len(self.services)):
            service_index = (self.current_service_index + attempt) % len(self.services)
            service = self.services[service_index]

            try:
                logger.info(
                    f"Attempting to generate response using {service.__class__.__name__}"
                )
                response = await service.generate_response(message, tools=tools)

                # Update current service if we successfully used a different one
                if service_index != self.current_service_index:
                    self.current_service_index = service_index
                    logger.info(
                        f"Switched to {service.__class__.__name__} as primary service"
                    )

                return response

            except Exception as e:
                logger.warning(f"Service {service.__class__.__name__} failed: {str(e)}")

                # Try next service if available
                if attempt < len(self.services) - 1:
                    logger.info(f"Falling back to next service...")
                    continue
                else:
                    # All services failed
                    raise Exception(f"All AI services failed. Last error: {str(e)}")

    async def transcribe_audio(self, audio_file) -> str:
        """
        Try to transcribe audio using any service that supports it (e.g., Groq).
        """
        for service in self.services:
            if hasattr(service, "transcribe_audio"):
                try:
                    return await service.transcribe_audio(audio_file)
                except Exception as e:
                    logger.error(
                        f"Transcription failed with {service.__class__.__name__}: {e}"
                    )

        raise Exception("No service available for audio transcription")

    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all configured services."""
        return {
            "total_services": len(self.services),
            "current_service": self.services[
                self.current_service_index
            ].__class__.__name__
            if self.services
            else None,
            "services": [
                {
                    "name": service.__class__.__name__,
                    "model": getattr(service, "model", "unknown"),
                    "timeout": service.timeout,
                    "max_retries": service.max_retries,
                }
                for service in self.services
            ],
        }


# Global AI service manager instance
ai_manager = AIServiceManager()

from .agents import AGENTS, ORCHESTRATOR_PROMPT, AgentType
from .memory import memory_manager
from .tools import tool_registry
from .pii_masking import pii_masker
from .graph_memory import graph_memory
import json
import re


class AgentOrchestrator:
    """
    Manages the multi-agent system.
    1. Receives user input.
    2. Uses a 'Router' (Orchestrator) to decide which agent should handle it.
    3. Invokes the selected agent with its specific persona.
    4. Integrates Long-Term Memory (RAG).
    """

    def __init__(self, service_manager: AIServiceManager):
        self.service_manager = service_manager

    async def _extract_entities_for_graph(self, text: str) -> List[str]:
        """
        Use LLM to extract key entities for graph traversal.
        """
        try:
            prompt = f"""Extract the 3 most important entities (nouns/subjects/objects) from the following text. 
            Return them as a simple comma-separated list.
            Text: "{text}"
            Entities:"""
            res = await self.service_manager.generate_response(prompt)
            entities = [
                e.strip() for e in res.get("content", "").split(",") if e.strip()
            ]
            return entities
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []

    async def _multi_hop_graph_search(
        self, message: str, initial_context: List[str]
    ) -> str:
        """
        Follow graph relationships to find hidden context.
        """
        graph_facts = []

        # 1. Extract entities from the user message
        entities = await self._extract_entities_for_graph(message)

        # 2. Extract entities from initial RAG context (first few docs)
        if initial_context:
            context_entities = await self._extract_entities_for_graph(
                "\n".join(initial_context[:2])
            )
            entities.extend(context_entities)

        # 3. Query Graph for relationships (Deduplicate)
        seen_triplets = set()
        for entity in set(entities):
            triplets = graph_memory.get_related_entities(entity, depth=2)
            for u, r, v in triplets:
                triplet_str = f"{u} --({r})--> {v}"
                if triplet_str not in seen_triplets:
                    graph_facts.append(triplet_str)
                    seen_triplets.add(triplet_str)

        if graph_facts:
            return "\n- ".join(graph_facts)
        return ""

    async def _extract_and_store_graph_triplets(self, text: str):
        """
        Extract (Entity1, Relation, Entity2) triplets and store in Graph.
        """
        try:
            prompt = f"""Identify key factual relationships in the following text. 
            Extract them as triplets in the format: Entity1 | Relation | Entity2
            Use one per line. Keep entities short (1-3 words).
            Text: "{text}"
            Triplets:"""
            res = await self.service_manager.generate_response(prompt)
            lines = res.get("content", "").strip().split("\n")
            for line in lines:
                if "|" in line:
                    parts = line.split("|")
                    if len(parts) == 3:
                        e1, r, e2 = parts
                        graph_memory.add_relationship(e1, r, e2)

            logger.info(
                f"Enriched Knowledge Graph with {len(lines)} potential relationships."
            )
        except Exception as e:
            logger.error(f"Graph enrichment failed: {e}")

    @observability.trace(name="orchestrator_route_and_generate")
    async def route_and_generate(
        self, message: str, draft_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Main entry point for the multi-agent system.
        Returns a dictionary with 'response', 'agent', and optional 'tool'.
        """
        # --- PII MASKING (Security) ---
        message = pii_masker.mask(message)
        # ... (lines 497-599 remain same, need to be careful with context)
        # Actually I need to replace the signature and the tool execution block

        # ...

        # 0. MEMORY: Retrieve relevant context
        try:
            # 0.1 Semantic RAG
            context_docs = memory_manager.search_memory(message)

            # 0.2 Multi-hop Graph RAG (New Phase 13)
            graph_context = await self._multi_hop_graph_search(message, context_docs)

            context_str = "\n- ".join(context_docs) if context_docs else ""
            if graph_context:
                context_str += f"\n\nCONNECTED KNOWLEDGE (Graph):\n- {graph_context}"

            if context_str:
                logger.info(f"Retrieved {len(context_docs)} memories and graph facts")
        except Exception as e:
            logger.error(f"Memory retrieval failed: {e}")
            context_str = ""

        # 1. ORCHESTRATION: Decide which agent to use
        try:
            # We use the primary service (Groq) for fast routing
            routing_prompt = (
                f'{ORCHESTRATOR_PROMPT}\n\nInput: "{message}"\n\nOutput JSON:'
            )
            router_response_dict = await self.service_manager.generate_response(
                routing_prompt
            )
            router_response = router_response_dict.get("content", "")

            clean_json = (
                router_response.replace("```json", "").replace("```", "").strip()
            )
            decision = json.loads(clean_json)

            agent_name = decision.get("agent", "generalist").lower()
            reason = decision.get("reason", "Defaulting to generalist")

            logger.info(f"Orchestrator routed to '{agent_name}' because: {reason}")

        except Exception as e:
            logger.error(f"Orchestration failed, falling back to Generalist: {e}")
            agent_name = "generalist"

        # 2. EXECUTION: Call the selected agent with Tool Loop
        selected_agent = AGENTS.get(agent_name, AGENTS[AgentType.GENERALIST.value])

        # Initialize conversation history with System Prompt and Context
        system_content = selected_agent.system_prompt
        if context_str:
            system_content += f"\n\nRELEVANT CONTEXT FROM MEMORY:\n{context_str}\n\nUse the above context to answer if relevant."

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": message},
        ]

        available_tools = tool_registry.get_schemas()

        final_response_text = ""
        tool_used = None
        tool_output = None

        # Max turns to prevent infinite loops (e.g., agent keeps calling tools)
        MAX_TURNS = 5

        for turn in range(MAX_TURNS):
            try:
                # Call AI Service
                response_dict = await self.service_manager.generate_response(
                    messages, tools=available_tools
                )

                response_content = response_dict.get("content")
                tool_calls = response_dict.get("tool_calls")

                # Append Assistant Message
                if tool_calls:
                    # If tools are called, content might be null or explanation
                    messages.append(
                        {
                            "role": "assistant",
                            "content": response_content,
                            "tool_calls": tool_calls,
                        }
                    )
                else:
                    # Final text response
                    messages.append({"role": "assistant", "content": response_content})
                    final_response_text = response_content
                    break  # Exit loop if no tools called

                # Execute Tools
                if tool_calls:
                    # DRAFT MODE CHECK
                    if draft_mode:
                        plans = []
                        for tc in tool_calls:
                            plans.append(
                                f"- Tool: {tc['function']['name']}, Args: {tc['function']['arguments']}"
                            )

                        final_response_text = (
                            f"DRAFT MODE: I plan to execute the following:\n"
                            + "\n".join(plans)
                            + "\n\nDo you approve?"
                        )
                        break  # Exit loop without executing

                    logger.info(
                        f"Executing {len(tool_calls)} tool calls (Turn {turn + 1})"
                    )

                    for tool_call in tool_calls:
                        function_name = tool_call["function"]["name"]
                        function_args_str = tool_call["function"]["arguments"]
                        tool_call_id = tool_call.get(
                            "id", f"call_{function_name}_{turn}"
                        )  # ID is required for tool role

                        tool_used = function_name
                        tool_result = f"Error: Tool {function_name} not found"

                        tool = tool_registry.get_tool(function_name)
                        if tool:
                            try:
                                # Parse args
                                try:
                                    kwargs = json.loads(function_args_str)
                                except json.JSONDecodeError:
                                    # Fallback hacks for bad JSON
                                    kwargs = (
                                        {"expression": function_args_str}
                                        if function_name == "calculator"
                                        else {"query": function_args_str}
                                    )

                                # Execute
                                try:
                                    tool_result = tool.execute(**kwargs)
                                except TypeError:
                                    if kwargs:
                                        tool_result = tool.execute(
                                            list(kwargs.values())[0]
                                        )
                                    else:
                                        tool_result = tool.execute()
                            except Exception as e:
                                tool_result = f"Error executing tool: {e}"

                        # Append Tool Output
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "name": function_name,
                                "content": str(tool_result),
                            }
                        )

                        tool_output = tool_result  # Store last output for return dict
                        logger.info(
                            f"Tool '{function_name}' output: {str(tool_result)[:50]}..."
                        )

            except Exception as e:
                logger.error(f"Error in execution loop: {e}")
                final_response_text = (
                    f"I encountered an error while processing your request: {e}"
                )
                break

        # 2.6 STRUICTURED UI EXTRACTION (Generative UI)
        suggestions = []
        charts = []

        if final_response_text:
            # Extract suggestions
            try:
                import re

                sugg_match = re.search(
                    r"```json-suggestions\n(.*?)\n```", final_response_text, re.DOTALL
                )
                if sugg_match:
                    suggestions = json.loads(sugg_match.group(1))
                    # Remove the block from the text to keep it clean
                    final_response_text = final_response_text.replace(
                        sugg_match.group(0), ""
                    ).strip()
            except Exception as e:
                logger.error(f"Failed to extract suggestions: {e}")

            # Extract charts
            try:
                chart_matches = re.finditer(
                    r"```json-chart\n(.*?)\n```", final_response_text, re.DOTALL
                )
                for match in chart_matches:
                    charts.append(json.loads(match.group(1)))
                    final_response_text = final_response_text.replace(
                        match.group(0), ""
                    ).strip()
            except Exception as e:
                logger.error(f"Failed to extract charts: {e}")

        # 3. MEMORY: Store the interaction
        try:
            # We store the final User/Assistant pair
            memory_manager.add_memory(message, {"role": "user", "agent": agent_name})

            # --- GRAPH ENRICHMENT (New Phase 13) ---
            # Try to learn new relationships from the interaction
            import asyncio

            asyncio.create_task(
                self._extract_and_store_graph_triplets(
                    f"User: {message}\nAssistant: {final_response_text}"
                )
            )
        except Exception as e:
            logger.error(f"Failed to store memory or enrich graph: {e}")

        return {
            "response": final_response_text,
            "agent": agent_name,
            "tool": tool_used,
            "tool_output": tool_output,
            "suggestions": suggestions,
            "charts": charts,
        }


# Global Orchestrator instance
# We need to initialize this *after* ai_manager is created
orchestrator = AgentOrchestrator(ai_manager)

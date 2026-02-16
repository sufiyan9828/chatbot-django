import streamlit as st
import requests
import time
import json

# --- Configuration ---
st.set_page_config(
    page_title="Enterprise Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for SaaS look
st.markdown(
    """
<style>
    /* Global Font */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Chat Message Container */
    .stChatMessage {
        background-color: transparent;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    
    .stChatMessage:hover {
        background-color: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    /* User Message Bubble */
    div[data-testid="stChatMessageContent"] {
        background-color: transparent;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0e1117;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Input Box */
    .stChatInputContainer {
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Buttons */
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        transition: transform 0.1s ease;
    }
    .stButton button:active {
        transform: scale(0.98);
    }
    
    /* Suggestion Buttons Styling */
    .suggestion-btn {
        margin-right: 10px;
        margin-bottom: 10px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- Constants ---
API_URL = "http://127.0.0.1:8000/api/webhook/"

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "next_prompt" not in st.session_state:
    st.session_state.next_prompt = None
if "is_typing" not in st.session_state:
    st.session_state.is_typing = False

# --- Top-Level Functions ---


def login():
    st.title("🔐 Enterprise Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In")
        if submitted:
            if username and password:
                st.session_state.user_id = username
                st.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.error("Please enter valid credentials.")


def sidebar():
    with st.sidebar:
        st.title("🤖 Chat Settings")
        st.write(f"Logged in as: **{st.session_state.user_id}**")
        if st.button("Clear History"):
            st.session_state.messages = []
            st.rerun()
        if st.button("Log Out"):
            st.session_state.user_id = None
            st.session_state.messages = []
            st.rerun()
        st.markdown("---")
        st.markdown("### 📊 Agent Status")
        st.success("● Online: Generalist")
        st.success("● Online: Coder")
        st.success("● Online: Researcher")
        st.success("● Online: Reviewer")


def chat_interface():
    st.title("💬 Enterprise Assistant")

    # Display chat history
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"], avatar=message.get("avatar")):
            st.markdown(message["content"])

            # --- RENDER CHARTS (Generative UI) ---
            if message.get("charts"):
                for chart in message["charts"]:
                    with st.expander(
                        f"📊 {chart.get('title', 'Data View')}", expanded=True
                    ):
                        if chart.get("type") == "bar":
                            st.bar_chart(chart["data"])
                        elif chart.get("type") == "line":
                            st.line_chart(chart["data"])
                        elif chart.get("type") == "metric":
                            cols = st.columns(len(chart["data"]))
                            for i, (label, value) in enumerate(chart["data"].items()):
                                cols[i].metric(label, value)

    # Render Suggestions (only for the very last assistant message)
    if (
        st.session_state.messages
        and st.session_state.messages[-1]["role"] == "assistant"
    ):
        last_msg = st.session_state.messages[-1]
        if last_msg.get("suggestions"):
            st.write("---")
            st.caption("✨ Smart Suggestions")
            cols = st.columns(len(last_msg["suggestions"]))
            for i, suggestion in enumerate(last_msg["suggestions"]):
                if cols[i].button(suggestion, key=f"sugg_btn_{i}"):
                    st.session_state.next_prompt = suggestion
                    st.rerun()

    # Handle Input or Suggestion
    prompt = st.chat_input("How can I help you today?")
    if st.session_state.next_prompt:
        prompt = st.session_state.next_prompt
        st.session_state.next_prompt = None

    if prompt:
        # Add user message to history
        st.session_state.messages.append(
            {"role": "user", "content": prompt, "avatar": "👤"}
        )
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Get bot response
        with st.chat_message("assistant", avatar="🤖"):
            message_placeholder = st.empty()
            full_response = ""

            # Show a loading spinner while waiting for the backend
            with st.spinner("Processing..."):
                try:
                    payload = {
                        "message": prompt,
                        "user_id": st.session_state.user_id,
                        "platform": "streamlit",
                    }
                    response = requests.post(API_URL, json=payload, timeout=60)

                    if response.status_code == 200:
                        data = response.json()
                        bot_text = data.get("response", "I didn't get a response.")
                        agent = data.get("agent", "generalist")

                        # Avatar mapping
                        avatar_map = {
                            "coder": "👨‍💻",
                            "researcher": "🔍",
                            "reviewer": "🛡️",
                        }
                        avatar = avatar_map.get(agent, "🤖")

                        # Streaming loop with STOP support
                        stop_col = st.columns([0.1, 0.9])
                        stop_gen = stop_col[0].button("🛑 Stop")

                        for chunk in bot_text.split(" "):
                            if stop_gen:
                                full_response += " ... [Stopped]"
                                break
                            full_response += chunk + " "
                            time.sleep(0.02)
                            message_placeholder.markdown(full_response + "▌")

                        message_placeholder.markdown(full_response)
                        st.caption(f"Agent: **{agent.title()}**")

                        # Save Assistant response
                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": full_response,
                                "avatar": avatar,
                                "agent": agent,
                                "suggestions": data.get("suggestions", []),
                                "charts": data.get("charts", []),
                            }
                        )
                        st.rerun()
                    else:
                        st.error(f"Error: {response.status_code}")
                except Exception as e:
                    st.error(f"Connection Failed: {e}")


# --- Main App Logic ---
def main():
    if not st.session_state.user_id:
        login()
    else:
        sidebar()
        chat_interface()


if __name__ == "__main__":
    main()

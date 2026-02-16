import networkx as nx
import logging
import json
import os
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)


class GraphManager:
    """
    Manages a Knowledge Graph to store entities and relationships.
    Enables Multi-hop reasoning and relationship-aware retrieval.
    """

    def __init__(self, persistence_path="graph_db.json"):
        self.persistence_path = persistence_path
        self.graph = nx.MultiDiGraph()
        self._load_graph()

    def _load_graph(self):
        """Load graph from a JSON file."""
        if os.path.exists(self.persistence_path):
            try:
                with open(self.persistence_path, "r") as f:
                    data = json.load(f)
                    # Simple node/edge reconstruction
                    for node in data.get("nodes", []):
                        self.graph.add_node(node["id"], **node.get("data", {}))
                    for edge in data.get("edges", []):
                        self.graph.add_edge(
                            edge["source"],
                            edge["target"],
                            key=edge.get("relation"),
                            **edge.get("data", {}),
                        )
                logger.info(
                    f"Graph loaded from {self.persistence_path} with {self.graph.number_of_nodes()} nodes."
                )
            except Exception as e:
                logger.error(f"Failed to load graph: {e}")

    def save_graph(self):
        """Save graph to a JSON file."""
        try:
            data = {
                "nodes": [
                    {"id": node, "data": self.graph.nodes[node]}
                    for node in self.graph.nodes()
                ],
                "edges": [
                    {"source": u, "target": v, "relation": key, "data": data}
                    for u, v, key, data in self.graph.edges(keys=True, data=True)
                ],
            }
            with open(self.persistence_path, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Graph saved to {self.persistence_path}")
        except Exception as e:
            logger.error(f"Failed to save graph: {e}")

    def add_relationship(
        self, entity1: str, relation: str, entity2: str, metadata: Dict[str, Any] = None
    ):
        """
        Add a triplet (entity1, relation, entity2) to the graph.
        """
        entity1 = entity1.strip().title()
        entity2 = entity2.strip().title()
        relation = relation.strip().lower()

        self.graph.add_node(entity1)
        self.graph.add_node(entity2)
        self.graph.add_edge(entity1, entity2, key=relation, **(metadata or {}))

        # Proactive: Also save on every significant update for persistence
        self.save_graph()

    def get_related_entities(
        self, entity: str, depth: int = 1
    ) -> List[Tuple[str, str, str]]:
        """
        Find entities related to the given entity up to a certain depth.
        Returns a list of (entity1, relation, entity2) triplets.
        """
        entity = entity.strip().title()
        if not self.graph.has_node(entity):
            return []

        triplets = []
        # Use Breadth-First Search to find neighbors
        edges = nx.bfs_edges(self.graph, entity, depth_limit=depth)
        for u, v in edges:
            # MultiDiGraph might have multiple edges between nodes
            edge_data = self.graph.get_edge_data(u, v)
            for relation in edge_data:
                triplets.append((u, relation, v))

        return triplets

    def search_graph(self, query: str) -> List[str]:
        """
        Simple keyword-based search in the graph's nodes/edges.
        """
        query_lower = query.lower()
        results = []
        for node in self.graph.nodes():
            if query_lower in node.lower():
                results.append(f"Entity: {node}")

        for u, v, key in self.graph.edges(keys=True):
            if query_lower in key.lower():
                results.append(f"Relationship: {u} --({key})--> {v}")

        return results


# Global instance
graph_memory = GraphManager()

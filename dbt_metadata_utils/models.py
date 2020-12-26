import json
from typing import Dict, List, Optional, Set
from pathlib import Path
from enum import Enum

from pydantic import BaseModel, validator
import networkx as nx


class DbtResourceType(str, Enum):
    model = "model"
    analysis = "analysis"
    test = "test"
    operation = "operation"
    seed = "seed"
    source = "source"


class DbtMaterializationType(str, Enum):
    table = "table"
    view = "view"
    incremental = "incremental"
    ephemeral = "ephemeral"
    seed = "seed"


class NodeDeps(BaseModel):
    nodes: List[str]
    # macros


class NodeConfig(BaseModel):
    materialized: Optional[DbtMaterializationType]


class Column(BaseModel):
    name: str
    description: str


class Node(BaseModel):
    unique_id: str
    path: Path
    resource_type: DbtResourceType
    description: str
    depends_on: Optional[NodeDeps]
    config: NodeConfig
    name: str
    tags: List[str]
    sources: Optional[List[List[str]]]
    columns: Dict[str, Column]
    fqn: List[str]
    # raw_sql
    # refs


class Manifest(BaseModel):
    nodes: Dict[str, Node]
    sources: Dict[str, Node]

    @validator("nodes", "sources")
    def filter(cls, val):
        return {
            k: v
            for k, v in val.items()
            if v.resource_type.value in ("model", "seed", "source")
        }


class GraphManifest(Manifest):
    """A parser for manifest.json, augmented with Graph logic."""

    @property
    def node_list(self):
        return list(self.nodes.keys()) + list(self.sources.keys())

    @property
    def edge_list(self):
        return [(d, k) for k, v in self.nodes.items() for d in v.depends_on.nodes]

    def build_graph(self) -> nx.Graph:
        """Build an Undirected Graph of the dbt DAG."""
        G = nx.Graph()
        G.add_nodes_from(self.node_list)
        G.add_edges_from(self.edge_list)
        return G

    def build_directed_graph(self) -> nx.DiGraph:
        """Build a Directed Graph of the dbt DAG."""
        G = nx.DiGraph()
        G.add_edges_from(self.edge_list)
        return G

    @staticmethod
    def get_ancestors_sources(node_id: str, G: nx.DiGraph) -> Optional[List[str]]:
        """Get all ancestors sources of a dbt node.

        Arguments:
            node_id: node id as defined in the dbt artifacts
            G: directed networkx graph of the dbt project

        Returns:
            sources and seeds that the node descend from, if any.
        """
        sources = None
        if node_id in G:
            ancestors: Set[str] = nx.ancestors(G, node_id)
            sources = list(
                set(
                    [
                        GraphManifest.get_folder_from_node_id(s)
                        for s in ancestors
                        if s.startswith("source") or s.startswith("seed")
                    ]
                )
            )
        return sources

    @staticmethod
    def get_folder_from_node_id(node_id: str) -> str:
        """Extract the folder from the node id.

        Arguments:
            node_id: node id as defined in the dbt artifacts.
                Assumes 'model.jaffle_shop.folder_name.model_name'.

        Returns:
            folder of the node.
        """
        return node_id.split(".")[2]


if __name__ == "__main__":
    with open("data/manifest.json") as fh:
        data = json.load(fh)

    m = GraphManifest(**data)

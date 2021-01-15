"""Data models for parsing dbt artifacts into graphs."""
import json

from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import networkx as nx

from pydantic import BaseModel, Field, validator


class DbtResourceType(str, Enum):
    """Different types of dbt resources."""

    model = "model"
    analysis = "analysis"
    test = "test"
    operation = "operation"
    seed = "seed"
    source = "source"


class DbtMaterializationType(str, Enum):
    """Different types of dbt materialization."""

    table = "table"
    view = "view"
    incremental = "incremental"
    ephemeral = "ephemeral"
    seed = "seed"


class NodeDeps(BaseModel):
    """Dbt node dependencies of another node in manifest.json."""

    nodes: List[str]
    # macros


class NodeConfig(BaseModel):
    """Config key of a dbt node in manifest.json."""

    enabled: bool
    materialized: Optional[DbtMaterializationType]
    bind: Optional[bool]


class Column(BaseModel):
    """Model for column of a node in manifest.json."""

    name: str
    description: str


class BaseNode(BaseModel):
    """Model for node and source in manifest.json."""

    columns: Dict[str, Column]
    config: NodeConfig
    # database: str
    description: str
    fqn: List[str]
    # meta: Dict
    name: str
    original_file_path: Path
    # package_name: str  # might be useful for faceting if you use many submodules
    # patch_path: Path  # .yml file
    path: Path
    resource_type: DbtResourceType
    # root_path: Path
    schema_: str = Field(..., alias="schema")
    tags: List[str]
    unique_id: str


class Node(BaseNode):
    """Node specific model in manifest.json."""

    # alias: str  # duplicate from name
    # checksum.checksum: str  # git commit sha256
    # deferred: bool
    depends_on: NodeDeps
    # docs.show: bool
    # raw_sql: str  # contains jinja
    # refs: List[List[str]]  # duplicates of subset of depends_on
    sources: List[List[str]]  # duplicates of subset of depends_on


class Source(BaseNode):
    """Source specific model in manifest.json."""

    # external: Optional[bool]
    # freshness: Dict
    identifier: str
    # loaded_at_field: str
    loader: str
    # quoting: Dict
    # source_description: str
    # source_meta: Dict
    # source_name: str


class Manifest(BaseModel):
    """Model for manifest.json."""

    nodes: Dict[str, Node]
    sources: Dict[str, Source]
    # macros
    # docs
    # exposures

    @validator("*")
    def filter(cls, val):  # noqa:ANN201,ANN001
        """Filter nodes and sources by resource_type."""
        return {
            k: v for k, v in val.items() if v.resource_type.value in ("model", "seed", "source")
        }


class GraphManifest(Manifest):
    """A parser for manifest.json, augmented with Graph logic."""

    @property
    def node_list(self) -> List[str]:
        """List of nodes required by networkx."""
        return list(self.nodes.keys()) + list(self.sources.keys())

    @property
    def edge_list(self) -> List[Tuple[str, str]]:
        """List of edges required by networkx."""
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

    def get_ancestors_loaders(self, node_id: str, G: nx.DiGraph) -> Optional[List[str]]:
        """Get all ancestors loaders of a dbt node.

        Arguments:
            node_id: node id as defined in the dbt artifacts
            G: directed networkx graph of the dbt project

        Returns:
            loaders that impact the node, if any.
        """
        loaders = None
        if node_id in G:
            ancestors: Set[str] = nx.ancestors(G, node_id)
            loaders = list(
                set([self.sources[s].loader for s in ancestors if s.startswith("source")])
            )
        return loaders

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

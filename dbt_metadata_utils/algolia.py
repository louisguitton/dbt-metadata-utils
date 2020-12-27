import json
from typing import Dict, List, Optional, Set

from algoliasearch.search_client import SearchClient
from pydantic import BaseModel, validator, root_validator
import networkx as nx

from dbt_metadata_utils.models import (
    GraphManifest,
    DbtMaterializationType,
    DbtResourceType,
)
from dbt_metadata_utils.config import Settings


class NodeSearch(BaseModel):
    # unique id
    objectID: str
    # attributes for search
    name: str
    description: str
    # attributes for displaying
    # TODO: add URL https://dbt-models.onefootball.com/#!/model/model.of_models.dim_countries
    # attributes for filtering
    resource_type: DbtResourceType
    materialized: Optional[DbtMaterializationType]
    sources: Optional[List[str]]
    folder: str
    # attributes for ranking
    degree_centrality: float
    is_in_mart: bool
    has_description: bool
    # TODO: add other score as customRank
    # score could be based on lastmod, number of users/views

    @root_validator(pre=True)
    def parse(cls, values):
        values["objectID"] = values.get("unique_id")
        values["materialized"] = values.get("config").get("materialized")
        values["folder"] = "/".join(values.get("fqn")[1:3])
        values["is_in_mart"] = values.get("fqn")[1] == "marts"
        values["has_description"] = len(values.get("description")) > 20
        return values

    @validator("degree_centrality")
    def round(cls, v):
        return round(v, 4)

    class Config:
        use_enum_values = True


def get_es_records(manifest: GraphManifest) -> List[Dict[str, str]]:
    """Generate ElasticSearch records from the manifest.json data."""
    # Build directed graph from manifest.json data
    G = manifest.build_directed_graph()

    # Get centrality of nodes
    # some keys that would have had centrality=0 with a Graph go missing with a DiGraph
    centrality = nx.degree_centrality(G)

    # Parse the nodes data for ElasticSearch and enrich it
    # with centrality and ancestor sources
    es_records = [
        NodeSearch(
            **node.dict(exclude={"sources"}),
            degree_centrality=centrality.get(node_id, 0.0),
            sources=GraphManifest.get_ancestors_sources(node_id, G)
        ).dict()
        for node_id, node in manifest.nodes.items()
    ]
    es_records += [
        NodeSearch(
            **node.dict(exclude={"sources"}),
            degree_centrality=centrality.get(node_id, 0.0),
            sources=[GraphManifest.get_folder_from_node_id(node_id)]
        ).dict()
        for node_id, node in manifest.sources.items()
    ]
    return es_records


if __name__ == "__main__":
    settings = Settings()

    client = SearchClient.create(
        app_id=settings.algolia_app_id, api_key=settings.algolia_admin_api_key
    )

    index = client.init_index(settings.algolia_index_name)

    with settings.dbt_manifest_path.open() as fh:
        data = json.load(fh)

    m = GraphManifest(**data)
    es_records = get_es_records(m)

    index.save_objects(es_records)

    index.set_settings(
        # https://www.algolia.com/doc/api-reference/settings-api-parameters/
        {
            "searchableAttributes": [
                # Here we want name and description to have the same importance
                # so we group them with a comma-separated list.
                "name,description",
            ],
            "attributesForFaceting": [
                "resource_type",
                "materialized",
                "folder",
                "sources",
            ],
            "ranking": [
                # we use centrality as a sorting attribute instead of a custom rank
                "desc(degree_centrality)",
                "typo",
                "words",
                "filters",
                "proximity",
                "attribute",
                "exact",
                "custom",
            ],
            "customRanking": ["desc(is_in_mart)", "desc(has_description)"],
        }
    )

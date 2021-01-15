"""Architecture diagram.

Ref:
    * https://diagrams.mingrammer.com/docs/getting-started/installation
    * http://www.graphviz.org/doc/info/attrs.html
"""
from diagrams import Cluster, Diagram
from diagrams.aws.analytics import Redshift
from diagrams.custom import Custom
from diagrams.onprem.analytics import Metabase
from diagrams.onprem.client import Users
from diagrams.onprem.vcs import Git
from diagrams.programming.language import NodeJS, Python


light_blue = "#d2e5f4"
hype_green = "#e1ff57"

with Diagram("dbt Metadata Utils", filename="docs/architecture"):

    with Cluster("Metadata Sources", graph_attr=dict(bgcolor="", style="dotted")):
        with Cluster("Supported", graph_attr=dict(bgcolor=light_blue)):
            dbt_repo = Git("Git metadata\nfrom source files")
            dbt = Custom("dbt artifacts", "./dbt.png")

        with Cluster("Other"):
            dwh = Redshift("Redshift metadata")
            metabase = Metabase("Metabase metadata")

    with Cluster("Backend Services", graph_attr=dict(bgcolor="", style="dotted")):

        with Cluster("Metadata Builders"):
            git_parser = Python("Git parser")
            dbt_repo >> git_parser

            dbt_parser = Python("dbt parser")
            dbt >> dbt_parser

        # Ingestion / Indexer / Publisher
        publisher = Python("Publisher")
        [git_parser, dbt_parser] >> publisher

        with Cluster("Search Service", graph_attr=dict(bgcolor=hype_green)):
            algolia = Custom("Algolia", "./algolia.png")
            publisher >> algolia

    with Cluster("Frontend Service", graph_attr=dict(bgcolor="", style="dotted")):
        ui = NodeJS("InstantSearch.js UI")
        algolia << ui

    users = Users("Users")
    ui << users

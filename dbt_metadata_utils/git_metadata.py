"""Parse git metadata from the dbt repository we want to index."""
import json
import os

from datetime import datetime
from typing import List, Optional, Tuple

import pandas as pd

from git import Commit, GitCommandError, Repo
from pydantic import BaseModel
from tqdm import tqdm

from dbt_metadata_utils.config import Settings
from dbt_metadata_utils.models import GraphManifest, Node


class GitCommit(BaseModel):
    """Model for git commit metadata."""

    authored_datetime: datetime
    commit: str
    author: str
    line_count_today: int


class FileGitHistory(BaseModel):
    """Model for file git history metadata."""

    owner: str
    created_at: datetime
    last_modified_at: datetime
    commits: List[GitCommit]


def get_git_metadata(repo: Repo, node: Node) -> Optional[FileGitHistory]:
    """Return git metadata for a file in the git repo."""
    metadata = None
    try:
        # https://gitpython.readthedocs.io/en/stable/reference.html#git.repo.base.Repo.blame
        blame_raw: List[Tuple[Commit, List[str]]] = repo.blame(
            rev=None, file=str(node.original_file_path)
        )

        # https://gitpython.readthedocs.io/en/stable/reference.html#module-git.objects.commit
        blame_clean = (
            pd.DataFrame.from_records(
                [
                    GitCommit(
                        authored_datetime=c.authored_datetime,
                        commit=c.name_rev,
                        author=c.author.name,
                        line_count_today=len(lines),
                    ).dict()
                    for c, lines in blame_raw
                ]
            )
            # the groupby implicitly sorts by commit date asc, which is what we want
            .groupby(["authored_datetime", "commit", "author"])
            .sum()
            .reset_index()
        )

        # WARNING: Assumes one node per filepath. For sources, multiple sources are in 1 .yml file, so this will not be useful data
        metadata = FileGitHistory(
            owner=blame_clean.loc[0, "author"],
            created_at=blame_clean.iloc[0]["authored_datetime"],
            last_modified_at=blame_clean.iloc[-1]["authored_datetime"],
            commits=blame_clean.to_dict(orient="records"),
        )
    except GitCommandError:
        # e.g.: 'fatal: no such path in HEAD' for local non-commited changes
        metadata = None

    return metadata


if __name__ == "__main__":
    settings = Settings()

    # Get git repo object for git metadata
    repo: Repo = Repo(settings.dbt_repo_local_path)

    with settings.dbt_manifest_path.open() as fh:
        data = json.load(fh)

    m = GraphManifest(**data)

    folder = settings.git_metadata_cache_path
    if not os.path.exists(folder):
        os.mkdir(folder)

    for node_id, node in tqdm(m.nodes.items()):
        file_path = f"{folder}/{node_id}.json"
        if not os.path.exists(file_path):
            node_git_metadata = get_git_metadata(repo, node)
            if node_git_metadata:
                with open(file_path, "w") as fh:
                    fh.write(node_git_metadata.json())

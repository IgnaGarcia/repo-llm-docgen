import logging
import re
import git
from pathlib import Path

from util import file_reader


class GitService:
    def __init__(self, path: str):
        try:
            self.path = path
            self.repo = git.Repo(path)
        except git.InvalidGitRepositoryError:
            logging.error(f"Error: route '{path}' is not a valid Git repository.")
            return None
        except Exception as e:
            logging.error(f"Unexpected error loading repository: {e}")
            return None

    def repo_info(self, settings):
        base = settings.get("base_branch", "main")

        context = {}
        context["name"] = Path(self.repo.working_dir).name
        context["path"] = self.path
        context["remotes"] = []
        for remote in self.repo.remotes:
            context["remotes"].append(
                {
                    "name": remote.name,
                    "url": remote.url,
                }
            )
        context["contributors"] = self.get_last_contributors(base)[:5]
        context["last_tag"] = (
            max(self.repo.tags, key=lambda t: t.commit.committed_date).name
            if self.repo.tags
            else "N/A"
        )

        return context

    def get_last_contributors(self, base):
        try:
            commits = list(self.repo.iter_commits(base, max_count=100))
            contributors = {}
            for commit in commits:
                author = commit.author
                if author.email not in contributors:
                    contributors[author.email] = {
                        "name": author.name,
                        "email": author.email,
                        "commits": 0,
                    }
                contributors[author.email]["commits"] += 1

            sorted_contributors = sorted(
                contributors.values(), key=lambda x: x["commits"], reverse=True
            )
            return sorted_contributors
        except Exception as e:
            logging.error(f"Error getting contributors: {e}")
            return []

    def get_diff(self, settings):
        base = settings.get("base_branch", "main")
        if self.repo.active_branch.name == base:
            return None

        unique_authors = set()
        for commit in self.repo.iter_commits(f"{base}..{self.repo.active_branch.name}"):
            unique_authors.add(commit.author.name)

        diffs = self.repo.index.diff(base, R=True)
        changed_files = []
        for diff in diffs:
            if diff.change_type in ["A", "M"]:
                if file_reader.should_ignore(
                    diff.a_path, diff.a_path.split("/")[-1], settings
                ):
                    continue
                is_new_file = diff.change_type == "A"

                if is_new_file:
                    changed_files.append(
                        {
                            "file_path": diff.a_path,
                            "is_new_file": is_new_file,
                            "new_lines": diff.b_blob.data_stream.read().decode(
                                "utf-8", errors="ignore"
                            ),
                        }
                    )
                    continue

                changes = self.repo.git.diff(base, diff.a_path).splitlines()

                changed_lines = {"added": [], "removed": []}
                line_number_current = 0
                line_number_change = 0

                for line in changes:
                    line_number_info = re.match(r"@@ \-(\d+),\d+ \+(\d+),\d+ @@", line)
                    if line_number_info:
                        line_number_current = int(line_number_info.group(1))
                        line_number_change = int(line_number_info.group(2))
                        continue

                    if line.startswith("+") and not line.startswith("+++"):
                        changed_lines["added"].append((line_number_change, line[1:]))
                        line_number_change += 1
                    elif line.startswith("-") and not line.startswith("---"):
                        changed_lines["removed"].append((line_number_current, line[1:]))
                        line_number_current += 1
                    else:
                        line_number_current += 1
                        line_number_change += 1

                changed_files.append(
                    {
                        "file_path": diff.a_path,
                        "is_new_file": is_new_file,
                        "changed_lines": changed_lines,
                    }
                )

        return {"changes": changed_files, "contributtors": list(unique_authors)}

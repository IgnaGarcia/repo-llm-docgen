import re
import git
from pathlib import Path

import repo_reader


def initialize_repo(path: str) -> git.Repo | None:
    try:
        repo = git.Repo(path)
        return repo
    except git.InvalidGitRepositoryError:
        print(f"Error: La ruta '{path}' no es un repositorio Git válido.")
        return None
    except Exception as e:
        print(f"Error inesperado al cargar el repositorio: {e}")
        return None


def repo_info(settings, path):
    repo = initialize_repo(path)
    base = settings["base_branch"]
    if repo is None:
        return []

    context = {}
    context["name"] = Path(repo.working_dir).name
    context["remotes"] = []
    for remote in repo.remotes:
        context["remotes"].append(
            {
                "name": remote.name,
                "url": remote.url,
            }
        )
    context["contributors"] = get_last_contributors(repo, base)

    context["latest_tags"] = []
    for tag in reversed(repo.tags):
        if tag.object.type != "tag":
            continue
        context["latest_tags"].append(
            {
                "name": tag.name,
                "commit": tag.commit.__str__()[0:7],
                "date": tag.commit.committed_datetime.strftime("%Y-%m-%d"),
                "tagger": {
                    "name": tag.tag.tagger.name,
                    "email": tag.tag.tagger.email,
                },
                "author": {
                    "name": tag.commit.author.name,
                    "email": tag.commit.author.email,
                },
            }
        )
        if len(context["latest_tags"]) >= 5:
            break

    description_path = Path(repo.git_dir) / "description"
    if description_path.exists():
        context["about"] = description_path.read_text(encoding="utf-8").strip()
    else:
        context["about"] = "Sin descripción disponible"

    return context


def get_last_contributors(repo, base):
    try:
        commits = list(repo.iter_commits(base, max_count=100))
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
        print(f"Error al obtener los contribuidores: {e}")
        return []


def get_diff(settings, path):
    repo = initialize_repo(path)
    base = settings["base_branch"]
    if repo is None:
        return None
    if repo.active_branch.name == base:
        print(
            f"Rama activa es la Rama base, omitiendo comparacion: {repo.active_branch.name}"
        )
        return

    diffs = repo.index.diff(base, R=True)
    changed_files = []
    for diff in diffs:
        if diff.change_type in ["A", "M"]:
            if repo_reader.should_ignore(diff.a_path.split("/")[-1], settings):
                continue
            is_new_file = diff.change_type == "A"
            changes = repo.git.diff(base, diff.a_path).splitlines()

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

            oldLines = ""
            if diff.a_blob is not None and diff.a_blob.data_stream is not None:
                oldLines = diff.a_blob.data_stream.read().decode(
                    "utf-8", errors="ignore"
                )

            changed_files.append(
                {
                    "file_path": diff.a_path,
                    "is_new_file": is_new_file,
                    "old_lines": oldLines,
                    "new_lines": diff.b_blob.data_stream.read().decode(
                        "utf-8", errors="ignore"
                    ),
                    "changed_lines": changed_lines,
                }
            )

    return changed_files

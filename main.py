import logging
from service import GitService
from util import repo_reader, settings
from orchestrator import Orchestrator
import json
import sys
from datetime import datetime


def main():
    json_settings = settings.load_settings()
    path = json_settings.get("repo_dir", "./")

    if json_settings.get("debug", False):
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logging.debug("Getting project structure")
    project_structure = repo_reader.get_project_structure(json_settings, path)

    logging.debug("Getting repo info")
    git_service = GitService(path)
    repo_info = git_service.repo_info(json_settings)
    # README -- FUERA DE ALCANCE
    # should update documentation? -- FUERA DE ALCANCE

    should_generate_rn = False
    if len(sys.argv) > 1:
        first_arg = sys.argv[1]
        should_generate_rn = first_arg == "-r" or first_arg == "--release-notes"

    if should_generate_rn:
        logging.debug("Getting diffs")
        diffs = git_service.get_diff(json_settings)

        logging.debug("Generating release notes")
        output_path = (
            f'{json_settings.get("output_path", "./out")}/RN-{datetime.now().date()}.md'
        )
        doc = Orchestrator(json_settings).generate_release_notes(diffs, path, repo_info)
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(doc)
    else:
        logging.debug("Generating documentation")
        output_path = f'{json_settings.get("output_path", "./out")}/doc.md'
        doc = Orchestrator(json_settings).generate_documentation(
            project_structure, path, repo_info
        )
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(doc)

    if json_settings.get("debug", False):
        save_debug(project_structure, repo_info)


def save_debug(project_structure, repo_info):
    with open("out/tmp/repo_struct.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(project_structure))
    with open("out/tmp/repo_info.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(repo_info))


main()

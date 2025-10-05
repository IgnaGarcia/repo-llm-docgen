import git_service
from settings import load_settings
import repo_reader
import json
import sys

DEBUG = True


def main():
    # load config file
    json_settings = load_settings()
    path = json_settings["repo_dir"]

    # context retrieval
    project_structure = repo_reader.get_project_structure(json_settings, path)
    readme = repo_reader.get_readme_content(path)
    repo_info = git_service.repo_info(json_settings, path)
    # repoAST -- FUERA DE ALCANCE

    # should update documentation? -- FUERA DE ALCANCE

    # 7 generate documentation
    # 7.1 set info to llm
    # 7.2 set template
    # 7.3 request new documentation
    # 7.4 save documentation

    # should generate release notes?
    generate_release_notes = False
    if len(sys.argv) > 1:
        first_arg = sys.argv[1]
        generate_release_notes = first_arg == "-r" or first_arg == "--release-notes"

    diffs = []
    if generate_release_notes:
        diffs = git_service.get_diff(json_settings, path)
    # 5.2 set info to llm
    # 5.4 set release notes template

    # load base promt
    # load info to llm
    # load release notes template
    # request documentation
    # save documentation

    if DEBUG:
        save_debug(project_structure, readme, repo_info, diffs)
    print("main ok")


def save_debug(project_structure, readme, repo_info, diffs):
    with open("out/repo_struct.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(project_structure))
    with open("out/readme.md", "w", encoding="utf-8") as file:
        file.write(readme)
    with open("out/tmp.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(repo_info))
    with open("out/diffs.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(diffs))


main()

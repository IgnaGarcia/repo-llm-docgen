import git_service
from llm_service import LLMManager
import prompter
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

    # should generate release notes?
    generate_release_notes = False
    if len(sys.argv) > 1:
        first_arg = sys.argv[1]
        generate_release_notes = first_arg == "-r" or first_arg == "--release-notes"

    doc = ""
    output_path = ""
    # connect LLM
    if generate_release_notes:
        # GENERATE RELEASE NOTES
        diffs = git_service.get_diff(json_settings, path)
        output_path = json_settings["rn_output_path"]
        template = repo_reader.get_file_content(json_settings["rn_template_path"])

        prompt = prompter.generate_release_notes_prompt(
            project_structure,
            repo_info,
            template,
            json_settings["output_language"],
            diffs,
        )
    else:
        # GENERATE GENERAL DOCUMENTATION
        print("Skipping release notes generation")
        output_path = json_settings["output_path"]
        template = repo_reader.get_file_content(json_settings["template_path"])

        prompt = prompter.generate_doc_prompt(
            project_structure,
            repo_info,
            template,
            json_settings["output_language"],
            readme,
        )

    # send prompt to LLM
    llm_manager = LLMManager(api_key=json_settings["model_api_key"])
    doc = llm_manager.process_request(prompt)

    if DEBUG:
        save_debug(project_structure, readme, repo_info, diffs, prompt)

    # save documentation to file
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(doc)


def save_debug(project_structure, readme, repo_info, diffs, prompt):
    with open("out/tmp/repo_struct.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(project_structure))
    with open("out/tmp/readme.md", "w", encoding="utf-8") as file:
        file.write(readme)
    with open("out/tmp/repo_info.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(repo_info))
    with open("out/tmp/diffs.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(diffs))
    with open("out/tmp/prompt.md", "w", encoding="utf-8") as file:
        file.write(prompt)


main()

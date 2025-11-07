import git_service
from llm_service import LLMManager
import prompter
from settings import load_settings
import repo_reader
import json
import sys
from datetime import datetime

DEBUG = True


def main():
    # load config file
    json_settings = load_settings()
    path = json_settings["repo_dir"]

    # context retrieval
    project_structure = repo_reader.get_project_structure(json_settings, path)
    repo_info = git_service.repo_info(json_settings, path)
    # repoAST -- FUERA DE ALCANCE
    # README -- FUERA DE ALCANCE

    # should update documentation? -- FUERA DE ALCANCE

    # should generate release notes?
    should_generate_rn = False
    if len(sys.argv) > 1:
        first_arg = sys.argv[1]
        should_generate_rn = first_arg == "-r" or first_arg == "--release-notes"

    if should_generate_rn:
        generate_release_notes(json_settings, path, repo_info)
    else:
        generate_docs(json_settings, path, project_structure, repo_info)

    if DEBUG:
        save_debug(project_structure, repo_info)


def generate_release_notes(json_settings, path, repo_info):
    diffs = git_service.get_diff(json_settings, path)
    output_path = f'{json_settings["output_path"]}/RN-{datetime.now().date()}.md'
    template = repo_reader.get_file_content(json_settings["rn_template_path"])

    prompt = prompter.generate_release_notes_prompt(
        repo_info,
        template,
        json_settings["output_language"],
        diffs,
    )

    if DEBUG:
        with open("out/tmp/diffs.json", "w", encoding="utf-8") as file:
            file.write(json.dumps(diffs))
        with open("out/tmp/prompt.md", "w", encoding="utf-8") as file:
            file.write(prompt)

    llm_manager = LLMManager(
        api_key=json_settings["model_api_key"], model_name=json_settings["model_name"]
    )
    doc = llm_manager.process_request(prompt=prompt)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(doc)
    return


def generate_docs(json_settings, path, project_structure, repo_info):
    output_path = f'{json_settings["output_path"]}/doc.md'
    template = repo_reader.get_file_content(json_settings["template_path"])
    """  # TODO
    primero, por cada archivo generar el min_content:
    - dependencies: [listado de dependencias internas, unicamente path relativo]
    - code: [listado de objetos donde se define nombre, tipo y contenido]
        clase/struct
            nombre
            contenido(atributos): [{nombre, tipo}]
        metodo/funcion
            firma(llamador, nombre, parametros, return)
            contenido(descripcion de la tarea muy brevemente)
    """

    project_content = repo_reader.get_project_content(project_structure, path)

    prompt = prompter.generate_doc_prompt(
        project_content,
        repo_info,
        template,
        json_settings["output_language"],
    )

    if DEBUG:
        with open("out/tmp/prompt.md", "w", encoding="utf-8") as file:
            file.write(prompt)

    llm_manager = LLMManager(api_key=json_settings["model_api_key"])
    doc = llm_manager.process_request(prompt)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(doc)


def save_debug(project_structure, repo_info):
    with open("out/tmp/repo_struct.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(project_structure))
    with open("out/tmp/repo_info.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(repo_info))


main()

prefix_prompt = "You are an AI documentation assistant, your task is to generate documentation based on the given code of an object. Your audience is technically savvy, so you need to be precise, dont let them know you're provided with code snippet and documents, AVOID ANY SPECULATION and inaccurate descriptions."
release_notes_prompt = "The purpose of the documentation is summarize the changes, focusing on the impact of the changes on users and developers, and highlighting any important modifications or new features."
general_doc_prompt = "The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code."
sufix_prompt = "Please write in {language}, but dont translate function or variable names, if necessary, you can write with some English words to enhance the readability"


def generate_doc_prompt(project_structure, repo_info, template, lang):
    """
    Solicitud de Documentacion General:
    1. Instrucciones (Prompt Base + Prompt de Documentacion General)
    2. Contexto del Proyecto(repo_info)
    3. Protocolo de comunicacion(Tool read_file)
    4. Formato de salida esperado(template)
    """
    return f"""The project info is:
{repo_info}

The project structure is:
{project_structure}

{prefix_prompt}
{general_doc_prompt}
{sufix_prompt.format(language=lang)}

The output format is: 
{template}"""


def generate_release_notes_prompt(repo_info, template, lang, diffs):
    """
    Solicitud de Resumen de Cambios:
    1. Instrucciones (Prompt Base + Prompt de Release Notes)
    2. Contexto del Proyecto(project_structure, repo_info)
    3. Cambios de codigo(archivos viejos + nuevos, con listado de lineas modificadas)
    4. Formato de salida esperado(template)
    """
    return f"""The project info is: 
{repo_info}

The code changes are: 
{diffs}

{prefix_prompt}
{release_notes_prompt}
{sufix_prompt.format(language=lang)}

The output format is: 
{template}"""


# TODO stringnify repo_info
# TODO prompt resumidor de codigo

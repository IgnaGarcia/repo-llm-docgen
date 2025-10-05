import os
from pathlib import Path


def get_project_structure(settings, base_path):
    project_structure = []

    def walk_dir(root):
        for name in sorted(os.listdir(root)):
            path = os.path.join(root, name)
            if should_ignore(path, name, settings):
                continue

            if os.path.isdir(path):
                walk_dir(path)
            elif os.path.isfile(path):
                project_structure.append(path.replace(base_path + "/", ""))

    walk_dir(base_path)
    return project_structure


def get_file_content(file_path):
    with open(file_path, "r") as file:
        return file.read()


def get_readme_content(repo_path):
    readme_names = ["README.md", "readme.md", "README.txt", "README"]

    for name in readme_names:
        readme_path = Path(repo_path) / name
        if readme_path.exists():
            return get_file_content(readme_path)[:10240]

    return "Sin README disponible"


def should_ignore(path, name, settings):
    if name.startswith(".") or name in settings.get("ingore_paths", []):
        # ignore basado en .gitignore -- FUERA DE ALCANCE
        return True
    if not os.path.isdir(path) and name.split(".")[-1] not in settings.get(
        "code_extensions", []
    ):
        return True
    return False

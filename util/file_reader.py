import os


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


# TODO: legacy - delete
def get_project_content(project_structure, base_path):
    proj_content = []
    for name in project_structure:
        with open(f"{base_path}/{name}", "r", encoding="utf-8") as f:
            content = f.read()
        proj_content.append({"file": name, "len": len(content), "raw": content})

    return proj_content


def get_file_content(file_path):
    with open(file_path, "r") as file:
        return file.read()


def should_ignore(path, name, settings):
    if name.startswith(".") or name in settings.get("ignore_paths", []):
        # ignore basado en .gitignore -- FUERA DE ALCANCE
        return True
    if not os.path.isdir(path) and name.split(".")[-1] not in settings.get(
        "code_extensions", []
    ):
        return True
    return False

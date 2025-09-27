import os


def build_node(name, node_type, content=None):
    node = {
        "type": node_type,
        "name": name,
    }
    if content is not None:
        node["content"] = content
    return node


def clear_empty_dirs(node):
    if node["type"] == "directory":
        node["content"] = [clear_empty_dirs(child) for child in node["content"]]
        node["content"] = [child for child in node["content"] if child is not None]
        if not node["content"]:
            return None
    return node


def get_project_structure(settings, path):
    project_structure = build_node(path, "directory", [])

    def walk_dir(root, content):
        for name in sorted(os.listdir(root)):
            if name.startswith(".") or name in settings.get("ingore_paths", []):
                # TODO ignore basado en .gitignore -- descartado
                continue

            path = os.path.join(root, name)

            if os.path.isdir(path):
                sub = build_node(name, "directory", [])
                content.append(sub)
                walk_dir(path, sub["content"])
            elif os.path.isfile(path) and name.split(".")[-1] in settings.get(
                "code_extensions", []
            ):
                sub = build_node(name, "file", "")
                content.append(sub)

    walk_dir(path, project_structure["content"])
    clear_empty_dirs(project_structure)
    return project_structure


def get_file_content(file_path):
    with open(file_path, "r") as file:
        return file.read()

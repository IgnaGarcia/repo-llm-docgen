import os


def build_node(name, path, node_type, content=None):
    node = {
        "type": node_type,
        "name": name,
        "path": path,
    }
    if content is not None:
        node["content"] = content
    return node


def get_project_structure(settings, path):
    project_structure = build_node(path, path, "directory", [])

    def walk_dir(root, content):
        for name in sorted(os.listdir(root)):
            if name.startswith(".") or name in settings.get("ingore_paths", []):
                continue

            path = os.path.join(root, name)

            if os.path.isdir(path):
                sub = build_node(name, path, "directory", [])
                content.append(sub)
                walk_dir(path, sub["content"])
            elif os.path.isfile(path):
                sub = build_node(name, path, "file", "")
                content.append(sub)

    walk_dir(path, project_structure["content"])
    return project_structure


def get_file_content(file_path):
    with open(file_path, "r") as file:
        return file.read()

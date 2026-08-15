import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from util.file_reader import should_ignore

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "..", "config", "doc-general")


def collect_files(settings, base_path):
    files = []

    def walk_dir(root):
        for name in sorted(os.listdir(root)):
            path = os.path.join(root, name)
            if should_ignore(path, name, settings):
                continue
            if os.path.isdir(path):
                walk_dir(path)
            elif os.path.isfile(path):
                files.append(path)

    walk_dir(base_path)
    return files


def main():
    for config_path in sorted(glob.glob(os.path.join(CONFIG_DIR, "*_config.json"))):
        with open(config_path, "r", encoding="utf-8") as f:
            settings = json.load(f)

        repo_dir = settings["repo_dir"]
        name = os.path.basename(config_path)

        if not os.path.isdir(repo_dir):
            print(f"{name}: repo_dir no encontrado: {repo_dir}")
            continue

        files = collect_files(settings, repo_dir)

        total_lines = 0
        total_chars = 0
        for path in files:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            total_chars += len(content)
            total_lines += content.count("\n") + (1 if content and not content.endswith("\n") else 0)

        n = len(files)
        print(f"\n== {name} ({repo_dir}) ==")
        print(f"code_extensions: {settings.get('code_extensions')}")
        print(f"archivos: {n}")
        print(f"lineas totales: {total_lines}")
        print(f"caracteres totales: {total_chars}")
        if n:
            print(f"promedio lineas/archivo: {total_lines / n:.2f}")
            print(f"promedio caracteres/archivo: {total_chars / n:.2f}")


if __name__ == "__main__":
    main()

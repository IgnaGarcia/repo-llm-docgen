import os
import logging


class Batcher:
    def __init__(self, max_chars_per_batch: int = 75000):
        self.max_chars = max_chars_per_batch

    def create_batches(self, file_paths, base_path):
        logging.debug(f"Creating batches from {len(file_paths)} files...")

        file_sizes = self._get_file_sizes(file_paths, base_path)
        total_chars = sum(file_sizes.values())

        logging.debug(f"Total chars: {total_chars:,}")

        if total_chars <= self.max_chars:
            logging.debug("All files fit in one batch")
            return self._create_single_batch(file_sizes, base_path)

        logging.debug("Building tree structure...")
        tree = self._build_tree(file_sizes)

        logging.debug("Creating batches from tree...")
        batches = self._create_batches_from_tree(tree, base_path)

        logging.debug(f"Created {len(batches)} batches")
        return batches

    def _get_file_sizes(self, file_paths, base_path):
        file_sizes = {}

        for file_path in file_paths:
            full_path = os.path.join(base_path, file_path)
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    file_sizes[file_path] = len(content)
            except Exception as e:
                logging.warning(f"Could not read {file_path}: {e}")
                continue

        return file_sizes

    def _create_single_batch(self, file_sizes, base_path):
        files = []
        contents = []
        total_chars = 0

        for file_path, size in file_sizes.items():
            full_path = os.path.join(base_path, file_path)
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            files.append(file_path)
            contents.append({"file": file_path, "content": content, "size": size})
            total_chars += size

        return [
            {
                "path_prefix": "all",
                "files": files,
                "contents": contents,
                "total_chars": total_chars,
            }
        ]

    def _build_tree(self, file_sizes):
        root = {"path": "./", "content": [], "chars": 0}

        for file_path, size in file_sizes.items():
            self._insert_into_tree(root, file_path, size)

        self._calculate_tree_sizes(root)

        return root

    def _insert_into_tree(self, root, file_path, size):
        parts = file_path.split("/")
        current = root

        for i, part in enumerate(parts[:-1]):
            found = False
            for child in current["content"]:
                if child["path"] == part and "content" in child:
                    current = child
                    found = True
                    break

            if not found:
                new_dir = {"path": part, "content": [], "chars": 0}
                current["content"].append(new_dir)
                current = new_dir

        current["content"].append({"path": parts[-1], "chars": size})

    def _calculate_tree_sizes(self, node):
        if "content" not in node:
            return node["chars"]

        total = 0
        for child in node["content"]:
            total += self._calculate_tree_sizes(child)

        node["chars"] = total
        return total

    def _create_batches_from_tree(self, tree, base_path):
        batches = []
        current_batch = {
            "path_prefix": "",
            "files": [],
            "contents": [],
            "total_chars": 0,
        }

        for child in tree["content"]:
            self._add_node_to_batches(
                child, batches, current_batch, base_path, prefix=""
            )

        if current_batch["files"]:
            batches.append(current_batch)

        return batches

    def _add_node_to_batches(
        self,
        node,
        batches,
        current_batch,
        base_path,
        prefix,
    ):
        node_path = f"{prefix}/{node['path']}" if prefix else node["path"]

        if "content" not in node:
            file_size = node["chars"]

            if (
                current_batch["total_chars"] + file_size > self.max_chars
                and current_batch["files"]
            ):
                batches.append(current_batch.copy())
                current_batch["path_prefix"] = ""
                current_batch["files"] = []
                current_batch["contents"] = []
                current_batch["total_chars"] = 0

            full_path = os.path.join(base_path, node_path)
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            if not current_batch["path_prefix"]:
                current_batch["path_prefix"] = os.path.dirname(node_path) or "root"

            current_batch["files"].append(node_path)
            current_batch["contents"].append(
                {"file": node_path, "content": content, "size": file_size}
            )
            current_batch["total_chars"] += file_size

        else:
            dir_size = node["chars"]

            if current_batch["total_chars"] + dir_size <= self.max_chars:
                self._add_entire_subtree(node, current_batch, base_path, node_path)

            elif not current_batch["files"]:
                for child in node["content"]:
                    self._add_node_to_batches(
                        child, batches, current_batch, base_path, node_path
                    )

            else:
                batches.append(current_batch.copy())
                current_batch["path_prefix"] = node_path
                current_batch["files"] = []
                current_batch["contents"] = []
                current_batch["total_chars"] = 0

                if dir_size <= self.max_chars:
                    self._add_entire_subtree(node, current_batch, base_path, node_path)
                else:
                    for child in node["content"]:
                        self._add_node_to_batches(
                            child, batches, current_batch, base_path, node_path
                        )

    def _add_entire_subtree(self, node, batch, base_path, prefix):
        if "content" not in node:
            full_path = os.path.join(base_path, prefix)
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            if not batch["path_prefix"]:
                batch["path_prefix"] = os.path.dirname(prefix) or "root"

            batch["files"].append(prefix)
            batch["contents"].append(
                {"file": prefix, "content": content, "size": node["chars"]}
            )
            batch["total_chars"] += node["chars"]
        else:
            for child in node["content"]:
                child_path = f"{prefix}/{child['path']}"
                self._add_entire_subtree(child, batch, base_path, child_path)

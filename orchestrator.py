import json
import logging
from service import Batcher
from agents import Condenser, Documenter


class Orchestrator:
    def __init__(self, settings):
        self.settings = settings
        self.debug = settings.get("debug", True)

        self.batcher = Batcher(75000)
        self.condenser = Condenser(settings)
        self.documenter = Documenter(settings)

    def generate_documentation(self, project_structure, base_path, repo_info):
        logging.debug(f"Batching files...")
        batches = self.batcher.create_batches(project_structure, base_path)

        if self.debug:
            self._save_debug(
                "/batches.json",
                [
                    {
                        "path_prefix": b["path_prefix"],
                        "files": b["files"],
                        "total_chars": b["total_chars"],
                    }
                    for b in batches
                ],
            )

        logging.debug(f"Condensing batches...")
        condensed_batches = self.condenser.condense_batches(
            batches=batches,
            template=self.settings["template_content"],
            objective="documentation",
        )

        if self.debug:
            self._save_debug("condensed_batches.json", condensed_batches)

        logging.debug(f"Generating documentation...")
        documentation = self.documenter.generate_doc(
            condensed_batches,
            repo_info,
            self.settings["template_content"],
            self.settings["output_language"],
        )

        logging.debug(f"Generated documentation")
        return documentation

    def generate_release_notes(self, diffs, base_path, repo_info):
        logging.debug(f"Extracting modified files...")
        modified_files = self._extract_modified_files(diffs)
        logging.debug(f"Extracted {len(modified_files)} modified files")

        if not modified_files:
            logging.warning("No modified files found")
            return "# Release Notes\n\nNo changes detected."

        logging.debug(f"Batching modified files...")
        batches = self.batcher.create_batches(modified_files, base_path)

        if self.debug:
            self._save_debug(
                "batches_rn.json",
                [
                    {
                        "path_prefix": b["path_prefix"],
                        "files": b["files"],
                        "total_chars": b["total_chars"],
                    }
                    for b in batches
                ],
            )

        logging.debug(f"Condensing batches...")
        condensed_batches = self.condenser.condense_batches(
            batches,
            self.settings["rn_template_content"],
            "release_notes",
        )

        if self.debug:
            self._save_debug("condensed_batches_rn.json", condensed_batches)

        logging.debug(f"Generating release notes...")
        release_notes = self.documenter.generate_release_notes(
            condensed_batches,
            diffs,
            repo_info,
            self.settings["rn_template_content"],
            self.settings["output_language"],
        )
        logging.debug(f"Generated release notes")
        return release_notes

    def _extract_modified_files(self, diffs):
        modified_files = []
        for change in diffs["changes"]:
            modified_files.append(change["file_path"])
        return modified_files

    def _save_debug(self, filename, data):
        debug_path = f"{self.settings.get('output_path', './out')}/tmp/{filename}"
        with open(debug_path, "w", encoding="utf-8") as f:
            if isinstance(data, (dict, list)):
                f.write(json.dumps(data, indent=2))
            else:
                f.write(str(data))

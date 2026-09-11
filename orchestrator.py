import json
import logging
import os
import shutil
from datetime import datetime

from service import Batcher
from service import Extractor
from agents import Condenser, Documenter


class Orchestrator:
    def __init__(self, settings):
        self.settings = settings
        self.base_path = settings.get("repo_dir", "./")
        self.debug = settings.get("debug", True)

        self.batcher = Batcher(75000)
        self.extractor = Extractor(settings)
        self.condenser = Condenser(settings)
        self.documenter = Documenter(settings)

    def generate_documentation(self, use_condensed_cache=False):
        project_structure, repo_info = self.extractor.get_documentation_context()

        cache_path = f"{self.settings.get('output_path', './out')}/condensed_batches.json"

        if use_condensed_cache and os.path.exists(cache_path):
            logging.info(f"Reusing condensed batches from cache: {cache_path}")
            with open(cache_path, "r", encoding="utf-8") as f:
                condensed_batches = json.load(f)
            self._abort_on_condensation_errors(condensed_batches)
        else:
            logging.debug("Batching files...")
            batches = self.batcher.create_batches(project_structure, self.base_path)

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
            self._abort_on_condensation_errors(condensed_batches)

            if self.debug:
                self._save_debug("condensed_batches.json", condensed_batches)

            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(condensed_batches, f, indent=2)
            logging.info(f"Saved condensed batches cache: {cache_path}")

        logging.debug(f"Generating documentation...")
        documentation = self.documenter.generate_doc(
            condensed_batches,
            repo_info,
            self.settings["template_content"],
            self.settings["output_language"],
        )

        logging.debug("Generated documentation")
        self._write_file("doc", documentation)
        self._copy_template_stylesheet()
        return

    def generate_release_notes(self, use_condensed_cache=False):
        repo_info, diffs = self.extractor.get_release_notes_context()

        cache_path = f"{self.settings.get('output_path', './out')}/condensed_cache_rn.json"

        if use_condensed_cache and os.path.exists(cache_path):
            logging.info(f"Reusing condensed batches from cache: {cache_path}")
            with open(cache_path, "r", encoding="utf-8") as f:
                condensed_batches = json.load(f)
            self._abort_on_condensation_errors(condensed_batches)
        else:
            logging.debug("Extracting modified files...")
            modified_files = self._extract_modified_files(diffs)
            logging.debug(f"Extracted {len(modified_files)} modified files")

            if not modified_files:
                logging.warning("No modified files found")
                self._write_file(
                    f"RN-{datetime.now().date()}",
                    "# Release Notes\n\nNo changes detected.",
                )
                return

            logging.debug(f"Batching modified files...")
            batches = self.batcher.create_batches(modified_files, self.base_path)

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
            self._abort_on_condensation_errors(condensed_batches)

            if self.debug:
                self._save_debug("condensed_batches_rn.json", condensed_batches)

            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(condensed_batches, f, indent=2)
            logging.info(f"Saved condensed batches cache: {cache_path}")

        logging.debug(f"Generating release notes...")
        release_notes = self.documenter.generate_release_notes(
            condensed_batches,
            diffs,
            repo_info,
            self.settings["rn_template_content"],
            self.settings["output_language"],
        )
        logging.debug("Generated release notes")
        self._write_file(f"RN-{datetime.now().date()}", release_notes)

    def _write_file(self, filename, content):
        output_path = self._build_output_path(filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _copy_template_stylesheet(self):
        template_path = self.settings.get("template_path", "")
        if not template_path.endswith(".html"):
            return

        stylesheet_path = f"{template_path[:-len('.html')]}_styles.css"
        if not os.path.isfile(stylesheet_path):
            return

        out_dir = self.settings.get("output_path", "./out")
        os.makedirs(out_dir, exist_ok=True)
        shutil.copy(stylesheet_path, f"{out_dir}/{os.path.basename(stylesheet_path)}")

    def _build_output_path(self, filename_without_ext):
        out_dir = self.settings.get("output_path", "./out")
        ext = self.settings.get("output_extension", "md")
        if not ext.startswith("."):
            ext = "." + ext
        return f"{out_dir}/{filename_without_ext}{ext}"

    def _abort_on_condensation_errors(self, condensed_batches):
        error_batches = [
            b for b in condensed_batches if isinstance(b, dict) and "error" in b
        ]
        if error_batches:
            prefixes = [b.get("path_prefix", "unknown") for b in error_batches]
            raise RuntimeError(
                f"Condensation failed for {len(error_batches)} batch(es) {prefixes}. "
                "Aborting before generating documentation to avoid feeding broken "
                "context to the documenter."
            )

    def _extract_modified_files(self, diffs):
        modified_files = []
        for change in diffs["changes"]:
            modified_files.append(change["file_path"])
        return modified_files

    def _save_debug(self, filename, data):
        debug_path = f"{self.settings.get('output_path', './out')}/tmp/{filename}"
        os.makedirs(os.path.dirname(debug_path), exist_ok=True)
        with open(debug_path, "w", encoding="utf-8") as f:
            if isinstance(data, (dict, list)):
                f.write(json.dumps(data, indent=2))
            else:
                f.write(str(data))

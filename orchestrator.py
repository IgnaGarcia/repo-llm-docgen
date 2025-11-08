import json
import logging
from agents import Analyzer, Synthesizer, Documenter


class Orchestrator:

    def __init__(self, settings):
        self.settings = settings
        self.debug = settings.get("debug", False)

        self.analyzer = Analyzer(settings)
        self.synthesizer = Synthesizer(settings)
        self.documenter = Documenter(settings)

    def generate_documentation(self, project_structure, base_path, repo_info):
        logging.info(f"Generating documentation for {len(project_structure)} files")

        logging.debug(f"Analyzing files...")
        analyzed_files = self.analyzer.analyze_files(
            project_structure, base_path, "documentation"
        )
        logging.debug(f"Analyzed {len(analyzed_files)} files")
        if self.debug:
            self._save_debug("analyzed_files.json", analyzed_files)

        logging.debug(f"Synthesizing context...")
        synthesized_context = self.synthesizer.synthesize(
            analyzed_files,
            self.settings["template_content"],
            "documentation",
        )
        logging.debug(f"Synthesized context")
        if self.debug:
            self._save_debug("synthesized_context.json", synthesized_context)

        logging.debug(f"Generating documentation...")
        documentation = self.documenter.generate_doc(
            synthesized_context,
            repo_info,
            self.settings["template_content"],
            self.settings["output_language"],
        )
        logging.debug(f"Generated documentation")
        return documentation

    def generate_release_notes(self, diffs, base_path, repo_info):
        logging.info(f"Generating release notes for {len(diffs)} changes")

        logging.debug(f"Extracting modified files...")
        modified_files = self._extract_modified_files(diffs)
        logging.debug(f"Extracted {len(modified_files)} modified files")

        logging.debug(f"Analyzing files...")
        analyzed_files = self.analyzer.analyze_files(
            modified_files, base_path, "release_notes"
        )
        logging.debug(f"Analyzed {len(analyzed_files)} files")
        if self.debug:
            self._save_debug("analyzed_files_rn.json", analyzed_files)

        logging.debug(f"Synthesizing context...")
        synthesized_context = self.synthesizer.synthesize(
            analyzed_files,
            self.settings["rn_template_content"],
            "release_notes",
            diffs,
        )
        logging.debug(f"Synthesized context")
        if self.debug:
            self._save_debug("synthesized_context_rn.json", synthesized_context)

        logging.debug(f"Generating release notes...")
        release_notes = self.documenter.generate_release_notes(
            synthesized_context,
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

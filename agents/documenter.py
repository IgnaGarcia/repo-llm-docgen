import json
import logging
from service import LlmService


class Documenter:
    def __init__(self, settings):
        self.settings = settings
        self.debug = settings.get("debug", False)
        agent_config = settings.get("agents", {}).get("documenter", {})

        self.model_name = agent_config.get("model", "gemini-2.5-flash")

        self.llm = LlmService(
            api_key=settings["model_api_key"], model_name=self.model_name
        )

        with open("./prompts/documenter_prompt.txt", "r", encoding="utf-8") as f:
            self.doc_prompt_template = f.read()

        with open("./prompts/rn_documenter_prompt.txt", "r", encoding="utf-8") as f:
            self.rn_prompt_template = f.read()

    def generate_doc(
        self,
        synthesized_context,
        repo_info,
        template,
        language,
    ):

        context_json = json.dumps(synthesized_context, indent=2)
        repo_info_str = json.dumps(repo_info, indent=2)

        prompt = self.doc_prompt_template.format(
            synthesized_context=context_json,
            repo_info=repo_info_str,
            template=template,
            language=language,
        )

        try:
            response = self.llm.process_request(prompt, "text/plain")
            return response

        except Exception as e:
            logging.debug(f"[ERROR] Error generating documentation: {e}")
            return f"# Error Generating Documentation\n\n{str(e)}"

    def generate_release_notes(
        self,
        synthesized_context,
        diffs,
        repo_info,
        template,
        language,
    ):
        context_json = json.dumps(synthesized_context, indent=2)
        diffs_json = json.dumps(diffs, indent=2)
        repo_info_str = json.dumps(repo_info, indent=2)

        prompt = self.rn_prompt_template.format(
            synthesized_context=context_json,
            diffs=diffs_json,
            repo_info=repo_info_str,
            template=template,
            language=language,
        )

        if self.debug:
            debug_path = f"{self.settings.get('output_path', './out')}/tmp/prompt"
            with open(
                f"{debug_path}/documenter_prompt.txt", "w", encoding="utf-8"
            ) as f:
                f.write(prompt)

        try:
            response = self.llm.process_request(prompt, "text/plain")
            return response

        except Exception as e:
            logging.debug(f"[ERROR] Error generating release notes: {e}")
            return f"# Error Generating Release Notes\n\n{str(e)}"

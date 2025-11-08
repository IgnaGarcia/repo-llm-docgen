import json
from service import LlmService
import logging


class Synthesizer:
    def __init__(self, settings):
        self.settings = settings
        self.debug = settings.get("debug", False)
        agent_config = settings.get("agents", {}).get("synthesizer", {})

        self.model_name = agent_config.get("model", "gemini-2.5-flash")

        self.llm = LlmService(
            api_key=settings["model_api_key"], model_name=self.model_name
        )

        with open("./prompts/synthesizer_prompt.txt", "r", encoding="utf-8") as f:
            self.prompt_template = f.read()

    def synthesize(
        self, analyzed_files, template, objective="documentation", diffs=None
    ):
        analysis_json = json.dumps(analyzed_files, indent=2)

        additional_context = ""
        if objective == "release_notes":
            additional_context = f"\n\nGIT DIFFS:\n{json.dumps(diffs, indent=2)}"

        prompt = self.prompt_template.format(
            objective=objective,
            num_files=len(analyzed_files),
            analyzed_files=analysis_json,
            template=template,
            additional_context=additional_context,
        )

        if self.debug:
            debug_path = f"{self.settings.get('output_path', './out')}/tmp/prompt"
            with open(
                f"{debug_path}/synthesizer_prompt.txt", "w", encoding="utf-8"
            ) as f:
                f.write(prompt)

        try:
            response = self.llm.process_request(prompt)

            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            result = json.loads(response)

            return result

        except json.JSONDecodeError as e:
            logging.debug(f"[ERROR] Failed to parse synthesizer response as JSON: {e}")
            logging.debug(f"Response preview: {response[:300]}...")
            return {
                "error": "Failed to parse synthesizer response",
                "raw_response": response[:500],
                "analyzed_files_summary": f"{len(analyzed_files)} files analyzed",
            }
        except Exception as e:
            logging.debug(f"[ERROR] Error during synthesis: {e}")
            return {
                "error": str(e),
                "analyzed_files_summary": f"{len(analyzed_files)} files analyzed",
            }

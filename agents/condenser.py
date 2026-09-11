import json
import logging
import os
from typing import List, Dict, Any
from service.llm_service import LlmService


class Condenser:
    def __init__(self, settings: Dict[str, Any]):
        self.settings = settings
        agent_config = settings.get("agents", {}).get("condenser", {})

        self.model_name = agent_config.get("model", "gemini-2.5-flash")
        self.llm = LlmService(
            api_key=settings["model_api_key"],
            model_name=self.model_name,
            thinking_level=agent_config.get("thinking_level"),
        )

        with open("./prompts/condenser_prompt.txt", "r", encoding="utf-8") as f:
            self.prompt_template = f.read()

        self.debug = settings.get("debug", False)

    def condense_batches(
        self,
        batches,
        template,
        objective="documentation",
    ):
        logging.debug(f"Condensing {len(batches)} batches...")

        condensed_batches = []
        for i, batch in enumerate(batches):
            logging.debug(
                f"Condensing batch {i+1}/{len(batches)}: {batch['path_prefix']}, {batch['total_chars']:,} chars, {len(batch['files'])} files"
            )
            condensed = self._condense_batch(i, batch, template, objective)
            logging.debug(f"Output: {len(json.dumps(condensed)):,} chars")
            condensed_batches.append(condensed)

        total_input = sum(b["total_chars"] for b in batches)
        total_output = sum(len(json.dumps(b)) for b in condensed_batches)
        logging.debug(
            f"Total reduction: {total_input:,} {total_output:,} chars ({total_input/total_output:.1f}x)"
        )

        return condensed_batches

    def _condense_batch(self, batch_number, batch, template, objective):

        prompt = self._build_prompt(
            batch_number,
            batch["path_prefix"],
            batch["contents"],
            template,
            objective,
        )

        if self.debug:
            debug_path = f"{self.settings.get('output_path', './out')}/tmp/prompt"
            os.makedirs(debug_path, exist_ok=True)
            with open(
                f"{debug_path}/{batch_number}_condenser_prompt.txt",
                "w",
                encoding="utf-8",
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

            if self.debug:
                debug_path = f"{self.settings.get('output_path', './out')}/tmp/response"
                os.makedirs(debug_path, exist_ok=True)
                with open(
                    f"{debug_path}/{batch_number}_condenser_response.txt",
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(response)

            result = json.loads(response, strict=False)
            return result

        except json.JSONDecodeError as e:
            logging.debug(f"Response preview: {response[:300]}...")
            return {
                "path_prefix": batch["path_prefix"],
                "error": "Failed to parse response",
            }
        except Exception as e:
            logging.error(f"Error condensing batch: {e}")
            return {
                "path_prefix": batch["path_prefix"],
                "error": str(e),
            }

    def _build_prompt(
        self,
        batch_number,
        path_prefix,
        files,
        template,
        objective,
    ):
        content = "\n"
        for file_info in files:
            content += f"FILE: {file_info['file']}\n"
            content += file_info["content"]

        prompt = self.prompt_template.format(
            batch_number=batch_number + 1,
            path_prefix=path_prefix,
            objective=objective,
            template_preview=(
                template[:500] + "..." if len(template) > 500 else template
            ),
            files_content=content,
        )

        return prompt

import json
import logging
from service import LlmService
from util import repo_reader


class Analyzer:
    def __init__(self, settings):
        self.settings = settings
        self.debug = settings.get("debug", False)
        agent_config = settings.get("agents", {}).get("analyzer", {})

        self.model_name = agent_config.get("model", "gemini-2.0-flash-exp")

        self.llm = LlmService(
            api_key=settings["model_api_key"], model_name=self.model_name
        )

        with open("./prompts/analyzer_prompt.txt", "r", encoding="utf-8") as f:
            self.prompt_template = f.read()

    def analyze_files(self, file_paths, base_path, objective="documentation"):
        batches = self._create_batches(file_paths, base_path)

        all_results = []
        for i, batch in enumerate(batches):
            logging.debug(
                f"  Processing batch {i+1}/{len(batches)} ({len(batch['files'])} files)..."
            )
            result = self._analyze_batch(i, batch, objective)
            all_results.extend(result)

        return all_results

    def _create_batches(self, file_paths, base_path):
        MAX_CHARS_PER_BATCH = 75000
        batches = []
        current_batch = {"files": [], "contents": []}
        current_char_count = 0

        for file_path in file_paths:
            full_path = f"{base_path}/{file_path}"
            try:
                content = repo_reader.get_file_content(full_path)
                content_length = len(content)

                if (
                    current_char_count + content_length > MAX_CHARS_PER_BATCH
                    and current_batch["files"]
                ):
                    batches.append(current_batch)
                    current_batch = {"files": [], "contents": []}
                    current_char_count = 0

                current_batch["files"].append(file_path)
                current_batch["contents"].append(
                    {"file": file_path, "content": content}
                )
                current_char_count += content_length

            except Exception as e:
                logging.debug(f"[WARNING] Could not read {file_path}: {e}")
                continue

        if current_batch["files"]:
            batches.append(current_batch)

        return batches

    def _analyze_batch(self, batch_number, batch, objective):
        files_content = ""
        for item in batch["contents"]:
            files_content += f"\n\n{'='*5}\n"
            files_content += f"FILE: {item['file']}\n"
            files_content += item["content"]

        prompt = self.prompt_template.format(
            objective=objective,
            num_files=len(batch["files"]),
            files_list="\n".join([f"- {f}" for f in batch["files"]]),
            files_content=files_content,
        )

        if self.debug:
            debug_path = f"{self.settings.get('output_path', './out')}/tmp/prompt"
            with open(
                f"{debug_path}/{batch_number}_analyzer_prompt.txt",
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
                with open(
                    f"{debug_path}/{batch_number}_analyzer_response.txt",
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(response)

            result = json.loads(response)

            if isinstance(result, dict) and "files" in result:
                return result["files"]
            elif isinstance(result, list):
                return result
            else:
                logging.debug(f"[WARNING] Unexpected response format, wrapping in list")
                return [result]

        except json.JSONDecodeError as e:
            logging.debug(f"[ERROR] Failed to parse LLM response as JSON: {e}")
            logging.debug(f"Response preview: {response[:200]}...")
            return [
                {
                    "file": f,
                    "error": "Failed to parse LLM response",
                    "relevance": "unknown",
                }
                for f in batch["files"]
            ]
        except Exception as e:
            logging.debug(f"[ERROR] Error analyzing batch: {e}")
            return [
                {"file": f, "error": str(e), "relevance": "unknown"}
                for f in batch["files"]
            ]

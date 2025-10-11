import json
import os
from dotenv import load_dotenv

from repo_reader import get_file_content


def load_settings():
    load_dotenv("./config/.env")

    with open("./config/config.json", "r") as file:
        content = file.read()
        json_content = json.loads(content)

    json_content["rn_template_content"] = get_file_content(
        json_content["rn_template_path"]
    )
    json_content["template_content"] = get_file_content(
        json_content["artifacts"][0]["template_path"]
    )

    json_content["model_api_key"] = os.getenv("API_KEY")
    return json_content

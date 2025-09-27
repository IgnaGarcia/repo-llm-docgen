import json
import os
from dotenv import load_dotenv


def load_settings():
    load_dotenv("./config/.env")

    with open("./config/config.json", "r") as file:
        content = file.read()
        json_content = json.loads(content)

    json_content["rn_template_content"] = load_template(
        json_content["rn_template_path"]
    )
    json_content["template_content"] = load_template(json_content["template_path"])

    json_content["model_api_key"] = os.getenv("API_KEY")
    return json_content


def load_template(template_path):
    with open(template_path, "r") as file:
        content = file.read()
    return content

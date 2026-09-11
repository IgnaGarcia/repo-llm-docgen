import logging
import sys

from util import settings
from orchestrator import Orchestrator


def main():
    args = sys.argv[1:]

    config_path = "./config/config.json"
    if "--config" in args:
        idx = args.index("--config")
        config_path = args[idx + 1]
        del args[idx : idx + 2]

    json_settings = settings.load_settings(config_path)

    if json_settings.get("debug", False):
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    should_generate_rn = any(arg in ("-r", "--release-notes") for arg in args)
    use_condensed_cache = any(arg in ("-c", "--use-cache") for arg in args)

    orchestrator = Orchestrator(json_settings)
    if should_generate_rn:
        orchestrator.generate_release_notes(use_condensed_cache=use_condensed_cache)
    else:
        orchestrator.generate_documentation(use_condensed_cache=use_condensed_cache)


if __name__ == "__main__":
    main()

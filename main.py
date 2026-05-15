"""
main.py — Entry point for the Krkn Doc Sync Bot GitHub Action.

Reads the GitHub event from GITHUB_EVENT_PATH and routes to the appropriate handler.
"""
import json
import sys

from src.config import Config
from src.github_client import GitHubClient
from src.llm_client import LLMClient
from src.doc_generator import handle_pr_merged, handle_issue_comment


def main():
    try:
        config = Config()
    except EnvironmentError as e:
        print(f"[DocBot] Configuration error: {e}")
        sys.exit(1)

    gh = GitHubClient(config.github_token)
    llm = LLMClient(config.groq_api_key, config.groq_model)

    # Load the GitHub event payload
    try:
        with open(config.github_event_path, "r") as f:
            event = json.load(f)
    except Exception as e:
        print(f"[DocBot] Failed to read event payload from {config.github_event_path}: {e}")
        sys.exit(1)

    event_name = config.github_event_name
    print(f"[DocBot] Handling event: {event_name}")

    if event_name == "pull_request":
        action = event.get("action")
        is_merged = event.get("pull_request", {}).get("merged", False)
        if action == "closed" and is_merged:
            handle_pr_merged(event, config, gh, llm)
        else:
            print(f"[DocBot] Skipping pull_request action='{action}', merged={is_merged}.")

    elif event_name == "issue_comment":
        action = event.get("action")
        # Only act on newly created comments on PRs
        if action == "created" and event.get("issue", {}).get("pull_request"):
            handle_issue_comment(event, config, gh, llm)
        else:
            print(f"[DocBot] Skipping issue_comment action='{action}' (not a PR comment or not 'created').")

    else:
        print(f"[DocBot] Unsupported event: {event_name}. Skipping.")


if __name__ == "__main__":
    main()

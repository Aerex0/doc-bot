"""
config.py — Reads all configuration from environment variables set by action.yml.
"""
import os


class Config:
    def __init__(self):
        self.github_token: str = self._require("GITHUB_TOKEN")
        self.groq_api_key: str = self._require("GROQ_API_KEY")
        self.website_repo: str = self._require("WEBSITE_REPO")
        self.website_docs_base_path: str = os.environ.get(
            "WEBSITE_DOCS_BASE_PATH", "content/en/docs"
        )
        self.groq_model: str = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
        self.github_event_name: str = os.environ.get("GITHUB_EVENT_NAME", "")
        self.github_event_path: str = os.environ.get("GITHUB_EVENT_PATH", "")
        self.github_repository: str = os.environ.get("GITHUB_REPOSITORY", "")

    @staticmethod
    def _require(key: str) -> str:
        value = os.environ.get(key)
        if not value:
            raise EnvironmentError(f"Required environment variable '{key}' is not set.")
        return value

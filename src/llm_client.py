"""
llm_client.py — Interfaces with Groq to analyze diffs and generate Hugo/Docsy markdown.
"""
from groq import Groq

ANALYZE_DIFF_SYSTEM_PROMPT = """You are an expert technical writer for the krkn-chaos open source project.
Your job is to analyze a git diff from an upstream repository and determine whether
it contains changes that would require documentation updates on the project website.

Documentation-impacting changes include:
- New or modified configuration fields (e.g., in YAML config files)
- New or changed CLI flags or commands
- New chaos scenarios or changes to existing scenario parameters
- New or changed API parameters or return values
- Any change to public-facing behavior described in user docs

Respond ONLY with a valid JSON object with the following fields:
- "needs_update": boolean — true if documentation needs to be updated
- "reason": string — a brief explanation of why
- "change_summary": string — a concise, human-readable summary of what changed (used as the PR body)
- "affected_doc_hint": string — the most likely doc section to update (e.g., "scenarios", "configuration", "cli")
"""

GENERATE_DOC_SYSTEM_PROMPT = """You are an expert technical writer for the krkn-chaos open source project.
The project website uses Hugo with the Docsy theme. Documentation files are written in Markdown.

You will be given:
1. A summary of what changed upstream
2. The current content of a documentation file

Your task is to update the documentation file to reflect the upstream changes.
Follow these rules:
- Preserve all existing content structure, headings, and Hugo front matter
- Only add or modify content that directly reflects the upstream change
- Use tables for parameters/config fields if a table already exists
- Do NOT add any commentary, preamble, or explanation — return ONLY the updated file content
- Keep the tone consistent with the existing docs
"""


class LLMClient:
    def __init__(self, api_key: str, model: str):
        self.client = Groq(api_key=api_key)
        self.model = model

    def _chat(self, system: str, user: str) -> str:
        """Send a message to Groq and return the text response."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()

    def analyze_diff(self, diff: str, pr_title: str, pr_body: str) -> dict:
        """
        Analyze a PR diff to determine if documentation updates are needed.
        Returns a dict with: needs_update, reason, change_summary, affected_doc_hint
        """
        import json

        user_message = f"""PR Title: {pr_title}

PR Description:
{pr_body or "(no description provided)"}

Git Diff:
```diff
{diff[:12000]}
```
"""
        raw = self._chat(ANALYZE_DIFF_SYSTEM_PROMPT, user_message)

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = "\n".join(raw.split("\n")[1:-1])

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Fallback: treat as needing update with raw reason
            return {
                "needs_update": True,
                "reason": raw,
                "change_summary": f"Changes from PR: {pr_title}",
                "affected_doc_hint": "general",
            }

    def generate_doc_update(self, change_summary: str, current_doc_content: str) -> str:
        """
        Given a change summary and existing doc content, return updated doc content.
        """
        user_message = f"""Change Summary:
{change_summary}

Current Documentation Content:
```markdown
{current_doc_content[:8000]}
```

Please return the full updated documentation file content.
"""
        return self._chat(GENERATE_DOC_SYSTEM_PROMPT, user_message)

    def refine_doc_update(self, instruction: str, current_doc_content: str) -> str:
        """
        Refine a doc update based on a human comment/instruction.
        """
        user_message = f"""Refinement Instruction from reviewer:
{instruction}

Current Documentation Content:
```markdown
{current_doc_content[:8000]}
```

Please return the full updated documentation file content incorporating the instruction.
"""
        return self._chat(GENERATE_DOC_SYSTEM_PROMPT, user_message)

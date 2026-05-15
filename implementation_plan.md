# Implementation Plan

## Goal Description
Implement an Automated Documentation Sync Bot for the Krkn-Chaos ecosystem to resolve issue #320. The bot will automatically detect documentation-impacting changes (e.g., new config fields, CLI flags, scenarios) merged into upstream repositories (krkn, krkn-hub, krknctl, krkn-ai). It will then generate a draft PR on the `krkn-chaos/website` repository with the required Hugo/Docsy documentation updates and allow refinement through PR comments.

## User Review Required
This plan has been updated to reflect your preferences. We will build a **standalone GitHub Action** using **Groq** as the LLM provider. Since this is an MVP for your LFX application, we will scaffold the action in the current workspace (`/home/aerex/Documents/LFX/2026-Term2/krkn-doc-bot`). You can then push this to your own GitHub repository and test it across your own mock upstream and website repositories to demonstrate its functionality.

> [!IMPORTANT]
> Please review the updated plan. If you approve, I will begin generating the core Action files (`action.yml`, `main.py`, etc.) in the current workspace.

## Proposed Changes
We will create a new Python project containing the bot logic in the workspace.

### Python Bot Application

#### [NEW] `action.yml`
Defines the GitHub Action interface (inputs like `github-token`, `llm-api-key`, `target-website-repo`).

#### [NEW] `main.py`
The main entry point for the bot logic. Handles incoming GitHub events (e.g., `pull_request` closed/merged, `issue_comment` created).

#### [NEW] `src/config.py`
Configuration management (parsing environment variables and Action inputs).

#### [NEW] `src/github_client.py`
Functions to interact with the GitHub API (fetching PR diffs, creating branches, committing files, creating draft PRs, reading/writing comments).

#### [NEW] `src/llm_client.py`
Logic to interact with the Groq API. Contains prompts for analyzing diffs to determine if docs are impacted, and generating the specific Hugo/Docsy markdown content.

#### [NEW] `src/doc_generator.py`
Core logic coordinating between `github_client` and `llm_client`. Determines which files in the website repository need updates based on the LLM's analysis.

#### [NEW] `requirements.txt` / `pyproject.toml`
Python dependencies (e.g., `PyGithub`, `langchain` or direct LLM SDKs).

## Verification Plan

### Automated Tests
- Unit tests for GitHub API interaction (using mocked responses).
- Unit tests for LLM prompt generation and response parsing.

### Manual Verification (Your Setup)
- To demonstrate this for your LFX application, you will need to create two dummy repositories:
  1. `mock-upstream-repo` (simulating `krkn` or `krkn-hub`)
  2. `mock-website-repo` (simulating `krkn-chaos/website`)
- We will set up the GitHub Action in `mock-upstream-repo` to trigger on PR merges, using a Groq API key and a GitHub PAT with repository access.
- We will verify that it successfully creates and updates documentation PRs on `mock-website-repo`.

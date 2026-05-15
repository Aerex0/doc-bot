"""
github_client.py — Wraps PyGithub to interact with the GitHub API.
Handles: fetching PR diffs, creating branches, committing files,
opening draft PRs, reading/posting comments.
"""
import re
from github import Github, GithubException
from github.Repository import Repository
from github.PullRequest import PullRequest


class GitHubClient:
    def __init__(self, token: str):
        self.gh = Github(token)

    def get_repo(self, repo_full_name: str) -> Repository:
        return self.gh.get_repo(repo_full_name)

    # -------------------------------------------------------------------------
    # Upstream PR helpers
    # -------------------------------------------------------------------------

    def get_pr_diff(self, repo: Repository, pr_number: int) -> str:
        """Fetch the unified diff of a pull request as a string."""
        pr = repo.get_pull(pr_number)
        files = pr.get_files()
        diff_parts = []
        for f in files:
            diff_parts.append(f"--- a/{f.filename}\n+++ b/{f.filename}")
            if f.patch:
                diff_parts.append(f.patch)
        return "\n".join(diff_parts)

    def get_pr(self, repo: Repository, pr_number: int) -> PullRequest:
        return repo.get_pull(pr_number)

    # -------------------------------------------------------------------------
    # Website repo helpers
    # -------------------------------------------------------------------------

    def get_file_content(self, repo: Repository, path: str, ref: str = "main") -> tuple[str, str]:
        """
        Returns (decoded_content, sha) for a file in the repo.
        Returns ("", "") if the file does not exist.
        """
        try:
            file_obj = repo.get_contents(path, ref=ref)
            return file_obj.decoded_content.decode("utf-8"), file_obj.sha
        except GithubException:
            return "", ""

    def create_branch(self, repo: Repository, branch_name: str, base_branch: str = "main") -> None:
        """Create a new branch from base_branch. No-ops if branch already exists."""
        try:
            base_ref = repo.get_git_ref(f"heads/{base_branch}")
            repo.create_git_ref(f"refs/heads/{branch_name}", base_ref.object.sha)
        except GithubException as e:
            if "already exists" in str(e):
                return
            raise

    def commit_file(
        self,
        repo: Repository,
        path: str,
        content: str,
        message: str,
        branch: str,
        sha: str = "",
    ) -> None:
        """Create or update a file in the repository on a given branch."""
        if sha:
            repo.update_file(path, message, content, sha, branch=branch)
        else:
            repo.create_file(path, message, content, branch=branch)

    def create_draft_pr(
        self,
        repo: Repository,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main",
    ) -> PullRequest:
        """Open a draft pull request."""
        return repo.create_pull(
            title=title,
            body=body,
            head=head_branch,
            base=base_branch,
            draft=True,
        )

    def find_existing_bot_pr(self, repo: Repository, branch_name: str) -> PullRequest | None:
        """Find an open PR from the bot branch, if any."""
        pulls = repo.get_pulls(state="open", head=f"{repo.owner.login}:{branch_name}")
        for pr in pulls:
            return pr
        return None

    def post_comment(self, pr: PullRequest, body: str) -> None:
        pr.create_issue_comment(body)

    # -------------------------------------------------------------------------
    # Comment parsing
    # -------------------------------------------------------------------------

    def is_bot_command(self, comment_body: str) -> bool:
        """Return True if the comment starts with /doc-sync."""
        return comment_body.strip().lower().startswith("/doc-sync")

    def parse_bot_command(self, comment_body: str) -> str:
        """Extract the refinement instruction from a /doc-sync command."""
        # Strip the /doc-sync prefix and return the rest as the instruction
        return re.sub(r"^/doc-sync\s*", "", comment_body.strip(), flags=re.IGNORECASE).strip()

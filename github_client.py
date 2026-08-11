import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}


def _run_graphql(query, variables):
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": variables},
        headers=HEADERS,
    )
    response.raise_for_status()
    data = response.json()
    if "errors" in data:
        print(f"  GraphQL error: {data['errors'][0]['message'][:120]}")
        return None
    return data


def get_org_pr_stats(org_name, days_back=30):
    from datetime import timezone

    query = """
    query($org: String!) {
      organization(login: $org) {
        repositories(first: 50, orderBy: {field: PUSHED_AT, direction: DESC}) {
          nodes {
            name
            pullRequests(
              first: 100
              states: MERGED
              orderBy: {field: CREATED_AT, direction: DESC}
            ) {
              nodes {
                createdAt
                mergedAt
                author { login }
              }
              totalCount
            }
          }
        }
      }
    }
    """

    data = _run_graphql(query, {"org": org_name})

    if data is None:
        return None

    org_data = data.get("data", {}).get("organization")
    if not org_data:
        print(f"  [!] Organization '{org_name}' not found")
        return None

    repos = org_data.get("repositories", {}).get("nodes", [])
    if not repos:
        print(f"  [!] No repositories found for {org_name}")
        return None

    all_prs = []
    repo_pr_counts = {}
    contributors = {}
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)

    for repo in repos:
        repo_name = repo["name"]
        pr_nodes = repo.get("pullRequests", {}).get("nodes", [])

        for pr in pr_nodes:
            created_at = datetime.fromisoformat(
                pr["createdAt"].replace("Z", "+00:00")
            )

            if created_at < cutoff:
                continue

            all_prs.append(pr)

            author = (
                pr.get("author", {}).get("login")
                if pr.get("author")
                else None
            )
            if author:
                contributors[author] = contributors.get(author, 0) + 1

            repo_pr_counts[repo_name] = repo_pr_counts.get(repo_name, 0) + 1

    merge_times = []
    for pr in all_prs:
        if pr.get("mergedAt") and pr.get("createdAt"):
            created = datetime.fromisoformat(
                pr["createdAt"].replace("Z", "+00:00")
            )
            merged = datetime.fromisoformat(
                pr["mergedAt"].replace("Z", "+00:00")
            )
            hours = (merged - created).total_seconds() / 3600
            if hours > 0:
                merge_times.append(hours)

    sorted_contributors = sorted(
        contributors.items(), key=lambda x: x[1], reverse=True
    )
    top_contributors = [u for u, _ in sorted_contributors[:5]]

    sorted_repos = sorted(
        repo_pr_counts.items(), key=lambda x: x[1], reverse=True
    )
    top_repos = [r for r, _ in sorted_repos[:3]]

    return {
        "org_name": org_name,
        "total_prs_merged": len(all_prs),
        "avg_merge_time_hours": (
            round(sum(merge_times) / len(merge_times), 1) if merge_times else 0
        ),
        "unique_contributors": len(contributors),
        "top_contributors": top_contributors,
        "top_repos": top_repos,
        "total_repos_analyzed": len(repos),
    }

def get_repo_ci_signals(org_name, repo_name):
    url = f"https://api.github.com/repos/{org_name}/{repo_name}/contents/.github"
    resp = requests.get(url, headers=HEADERS)

    if resp.status_code == 200:
        wf_resp = requests.get(f"{url}/workflows", headers=HEADERS)
        return {
            "has_github_actions": True,
            "ci_signal": "GitHub Actions detected",
        }
    return {"has_github_actions": False, "ci_signal": "No GitHub Actions detected"}
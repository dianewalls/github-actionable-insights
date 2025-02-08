import streamlit as st
import requests
import pandas as pd
import os
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ORG_NAME = os.getenv("GITHUB_ORG_NAME")

# GitHub API headers
def github_headers():
    return {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

# Fetch repositories
def get_repos():
    url = f"https://api.github.com/orgs/{ORG_NAME}/repos"
    response = requests.get(url, headers=github_headers())
    repos = response.json()
    return [repo['name'] for repo in repos if not repo['archived']]

# Fetch pull requests
def get_pull_requests(repo):
    url = f"https://api.github.com/repos/{ORG_NAME}/{repo}/pulls?state=all"
    response = requests.get(url, headers=github_headers())
    return response.json()

# Fetch issues
def get_issues(repo):
    url = f"https://api.github.com/repos/{ORG_NAME}/{repo}/issues?state=all"
    response = requests.get(url, headers=github_headers())
    return response.json()

# Identify first-time contributors
def first_time_contributors(prs):
    first_time_contribs = {}
    for pr in prs:
        user = pr['user']['login']
        if user not in first_time_contribs:
            first_time_contribs[user] = {
                "opened": 0,
                "merged": 0,
                "first_pr_date": datetime.datetime.strptime(pr['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            }
        first_time_contribs[user]["opened"] += 1
        if pr.get("merged_at"):
            first_time_contribs[user]["merged"] += 1
    return first_time_contribs

# Calculate response time to first-time PRs
def response_time_to_first_pr(prs):
    response_times = []
    for pr in prs:
        created_at = datetime.datetime.strptime(pr['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        first_comment_time = None  # Default if no comments found
        comments_url = pr['comments_url']
        comments = requests.get(comments_url, headers=github_headers()).json()
        if comments:
            first_comment_time = datetime.datetime.strptime(comments[0]['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        if first_comment_time:
            response_times.append((first_comment_time - created_at).total_seconds() / (24*3600))
    return sum(response_times) / len(response_times) if response_times else None


# Calculate response time to merge
def time_to_merge_pr(prs):
    merged_times = []
    for pr in prs:
        created_at = datetime.datetime.strptime(pr['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        merged_at = pr['merged_at']
        merged_at = datetime.datetime.strptime(merged_at, "%Y-%m-%dT%H:%M:%SZ") if merged_at else None
        if merged_at:
            merged_times.append((merged_at - created_at).total_seconds() / (24*3600))
    return sum(merged_times) / len(merged_times) if merged_times else None

# Calculate response time to merge
def time_of_forgotten_pr(prs):
    date_now = datetime.datetime.now()
    not_merged_times = []
    for pr in prs:
        created_at = datetime.datetime.strptime(pr['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        merged_at = pr['merged_at']
        if not merged_at:
            not_merged_times.append((date_now - created_at).total_seconds() / (24*3600))
    return sum(not_merged_times) / len(not_merged_times) if not_merged_times else None

# Identify first-time users who opened issues
def first_time_issues(issues):
    first_time_issues = {}
    for issue in issues:
        user = issue['user']['login']
        if user not in first_time_issues:
            first_time_issues[user] = {"opened": 0, "closed": 0}
        first_time_issues[user]["opened"] += 1
        if issue.get("closed_at"):
            first_time_issues[user]["closed"] += 1
    return first_time_issues

# Check second contribution within 3 months
def second_contribution_check(first_time_contribs, prs):
    second_contribs = 0
    for user, data in first_time_contribs.items():
        first_pr_date = data['first_pr_date']
        three_months_later = first_pr_date + datetime.timedelta(days=90)
        for pr in prs:
            if pr['user']['login'] == user:
                pr_date = datetime.datetime.strptime(pr['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                if pr_date > first_pr_date and pr_date <= three_months_later:
                    second_contribs += 1
                    break
    return second_contribs

# Streamlit UI
st.title("GitHub Contribution Stats for Python-Chile")

repos = get_repos()
selected_repo = st.selectbox("Select a repository", repos)

if selected_repo:
    prs = get_pull_requests(selected_repo)
    issues = get_issues(selected_repo)
    
    first_time_pr_data = first_time_contributors(prs)
    first_time_issues_data = first_time_issues(issues)
    
    opened_prs = sum([v["opened"] for v in first_time_pr_data.values()])
    merged_prs = sum([v["merged"] for v in first_time_pr_data.values()])
    response_time = response_time_to_first_pr(prs)
    time_to_merge = time_to_merge_pr(prs)
    time_of_forgotten_pr = time_of_forgotten_pr(prs)
    second_contributors = second_contribution_check(first_time_pr_data, prs)
    
    opened_issues = sum([v["opened"] for v in first_time_issues_data.values()])
    closed_issues = sum([v["closed"] for v in first_time_issues_data.values()])
    
    st.metric("# First-Time PRs Opened", opened_prs)
    st.metric("# First-Time PRs Merged", merged_prs)

    st.metric("Response Time to First PRs (days)", f"{response_time:.2f}" if response_time else "N/A")
    st.metric("Time to Merge PRs (days)", f"{time_to_merge:.2f}" if time_to_merge else "N/A")
    st.metric("Time of forgotten PRs (days)", f"{time_of_forgotten_pr:.2f}" if time_of_forgotten_pr else "N/A")

    st.metric("Merge Ratio", f"{(merged_prs/opened_prs)*100:.2f}%" if opened_prs else "N/A")
    st.metric("First-Time Issues Opened", opened_issues)
    st.metric("First-Time Issues Closed", closed_issues)
    st.metric("Second-Time Contributors (Within 3 Months)", second_contributors)

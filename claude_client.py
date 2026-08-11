import anthropic
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_pitch(company_name, github_stats, ci_signal):
    """
    Generate sales intelligence from GitHub data.
    Returns dict with pain_point_hypothesis, icebreaker, suggested_talking_points.
    """

    system_prompt = """You are an AI assistant helping a GTM Engineer at Aviator, a company that builds developer workflow automation tools.

Aviator's products:
- MergeQueue: A merge queue that eliminates merge conflicts and broken builds by serializing merges and running CI before merge
- FlexReview: Intelligent code review routing that sends simpler PRs to faster testing tiers
- Runbooks: Collaborative AI agent platform for automating complex engineering workflows

Your job: Analyze GitHub activity data for a target company and generate technical, specific sales intelligence.
You are NOT writing marketing copy. You are writing the research an AE would do before a call.
Be specific, technical, and reference real engineering concepts. Do NOT use generic placeholders or vague claims."""

    user_prompt = f"""Analyze this company for Aviator sales intelligence:

COMPANY: {company_name}
GITHUB STATS (last 30 days):
- Merged PRs: {github_stats['total_prs_merged']}
- Average merge time: {github_stats['avg_merge_time_hours']} hours
- Unique contributors: {github_stats['unique_contributors']}
- Most active repos: {', '.join(github_stats['top_repos'])}
- Top contributors: {', '.join(github_stats['top_contributors'])}
- CI/CD signal: {ci_signal}

Based on this data, generate a sales intelligence package. Your response MUST be in this exact JSON format:

{{
  "pain_point_hypothesis": "A 2-3 sentence technical hypothesis about their biggest developer experience bottleneck, based on the data. Reference specific numbers.",
  "icebreaker": "Exactly 2 sentences for a cold email to their Head of Platform Engineering. First sentence must reference their PR velocity. Second sentence must connect that to a specific DevEx pain (CI costs, merge conflicts, review bottlenecks, flaky tests). Be specific — mention GitHub Actions if detected, or reference their repo names.",
  "suggested_talking_points": ["3 bullet points that an AE could use on a discovery call. Each should be technical and reference the company's actual engineering setup."]
}}

CRITICAL RULES:
- Do not make up blog posts or specific tools they use unless detected in the data
- Base everything on the GitHub stats provided
- If their PR volume is high and merge time is low, hypothesize about CI cost/bottleneck tradeoffs
- If their merge time is high, focus on review bottlenecks and merge conflicts
- Never use phrases like "I noticed" or "we can help" — be direct and technical
- Never use [CompanyName] placeholders — use the actual company name"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw_text = response.content[0].text

    json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
    if json_match:
        raw_text = json_match.group(0)

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "pain_point_hypothesis": "Parse error",
            "icebreaker": raw_text[:300],
            "suggested_talking_points": ["Check raw response"],
        }
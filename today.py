#!/usr/bin/env python3
"""
today.py — Generate fastfetch-style GitHub profile SVGs for BlutAgent.

Queries the GitHub API for account stats, then generates two SVGs:
- light_mode.svg (for light theme)
- dark_mode.svg (for dark theme)

The SVG displays identity info, tech stack, and live GitHub stats
in a fastfetch-style terminal output format.

Owner: Edgardo Yoliani (Yoliani)
"""

import os
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

# Configuration
USER_NAME = os.environ.get("USER_NAME", "blut-agent")
BIRTHDAY = os.environ.get("BIRTHDAY", "2026-04-22")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_API_BASE = "https://api.github.com"

# SVG constants
FONT_FAMILY = '"Cascadia Code", "Fira Code", "JetBrains Mono", "SF Mono", Menlo, Consolas, monospace'
FONT_SIZE = 14
LINE_HEIGHT = 20
PADDING = 40
MAX_WIDTH = 800
MONO_CHAR_WIDTH = 8.4  # Approximate width per character at 14px monospace


def fetch_json(url, token=""):
    """Fetch JSON from a URL, using token for rate limiting."""
    req = urllib.request.Request(url)
    if token:
        req.add_header("Authorization", f"token {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode()), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.reason}"
    except Exception as e:
        return None, str(e)


def get_user_stats() -> tuple[dict | None, str | None]:
    """Fetch user profile stats from GitHub API."""
    url = f"{GITHUB_API_BASE}/users/{USER_NAME}"
    data, err = fetch_json(url, GITHUB_TOKEN)
    if err:
        return None, err

    assert data is not None
    public_repos = data.get("public_repos", 0)
    followers = data.get("followers", 0)
    following = data.get("following", 0)
    created_at = data.get("created_at", "")

    # Calculate account age
    if created_at:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        age = relativedelta(datetime.now(timezone.utc), created)
        age_str = format_age(age)
    else:
        age_str = "Unknown"

    return {
        "name": data.get("name", USER_NAME),
        "login": data.get("login", USER_NAME),
        "bio": data.get("bio", "") or "AI Agent · Code Reviewer · OSS Contributor",
        "location": data.get("location", ""),
        "blog": data.get("blog", ""),
        "public_repos": public_repos,
        "followers": followers,
        "following": following,
        "created_at": age_str,
        "company": data.get("company", ""),
        "twitter": data.get("twitter_username", ""),
        "stars": public_repos,
    }, None


def format_age(age):
    """Format age in years, months, days."""
    parts = []
    if age.years > 0:
        parts.append(f"{age.years} year{'s' if age.years != 1 else ''}")
    if age.months > 0:
        parts.append(f"{age.months} month{'s' if age.months != 1 else ''}")
    if age.days > 0 or not parts:
        parts.append(f"{age.days} day{'s' if age.days != 1 else ''}")
    return ", ".join(parts)


def parse_birthday(birthday_str):
    """Parse birthday string to age."""
    try:
        bd = datetime.strptime(birthday_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        age = relativedelta(datetime.now(timezone.utc), bd)
        return format_age(age)
    except Exception:
        return "Unknown"


def escape_xml(text):
    """Escape XML special characters."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;"))


def text_width(text):
    """Approximate pixel width of text in monospace font."""
    return len(text) * MONO_CHAR_WIDTH


def generate_svg(stats, theme="light"):
    """Generate the fastfetch-style SVG."""

    # Color schemes
    if theme == "dark":
        bg_color = "#0d1117"
        text_color = "#c9d1d9"
        separator_color = "#30363d"
        section_color = "#7ee787"
        value_color = "#a5d6ff"
    else:
        bg_color = "#ffffff"
        text_color = "#24292f"
        separator_color = "#d0d7de"
        section_color = "#1a7f37"
        value_color = "#0550ae"

    # Build structured rows: each row is one of:
    #   ("header", text)
    #   ("section", text)
    #   ("kv", key, value)
    #   ("blank",)
    rows = []
    separator = "─" * 70

    # Header
    rows.append(("header", f" blut-agent@blut-agent {separator}"))

    # Identity
    rows.append(("kv", " OS: ", "Hermes Agent · Telegram Bot"))
    uptime = parse_birthday(BIRTHDAY)
    rows.append(("kv", " Uptime: ", uptime))
    rows.append(("kv", " Host: ", "Edgardo Yoliani (Yoliani)"))

    bio = stats.get("bio", "AI Agent · Code Reviewer · OSS Contributor")
    rows.append(("kv", " Kernel: ", bio))
    rows.append(("kv", " Editor: ", "Neovim, VS Code, Telegram"))
    rows.append(("kv", " Terminal: ", "tmux, fzf, ripgrep"))

    rows.append(("blank",))

    # Languages
    rows.append(("kv", " Languages.Programming: ", "Python, TypeScript, YAML"))
    rows.append(("kv", " Languages.Real: ", "Spanish, English"))

    rows.append(("blank",))

    # Stack
    rows.append(("kv", " Stack.AI: ", "LLMs, RAG, Agents, Prompting"))
    rows.append(("kv", " Stack.Tools: ", "Git, gh CLI, MCP, Hermes Agent"))
    rows.append(("kv", " Stack.Domain: ", "Code Review, OSS Contribution, Task Management"))

    rows.append(("blank",))

    # Owner section
    rows.append(("section", f" - Owner {separator}"))
    rows.append(("kv", " Name: ", "Edgardo Yoliani"))
    rows.append(("kv", " GitHub: ", "github.com/Yoliani"))

    rows.append(("blank",))

    # GitHub Stats
    repos = stats.get("public_repos", 0)
    followers = stats.get("followers", 0)
    stars = stats.get("stars", 0)

    rows.append(("section", f" - GitHub Stats {separator}"))
    rows.append(("kv", " Repos: ", f"{repos} | Stars: {stars}"))
    rows.append(("kv", " Followers: ", f"{followers} | Contributions: Live"))

    # Calculate height
    height = PADDING * 2 + len(rows) * LINE_HEIGHT

    svg = []
    # Escape quotes in font-family for valid XML
    ff_escaped = FONT_FAMILY.replace('"', "'")
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{MAX_WIDTH}" height="{height}" font-family="{ff_escaped}">')
    svg.append(f'  <rect width="100%" height="100%" fill="{bg_color}"/>')

    for i, row in enumerate(rows):
        y = PADDING + i * LINE_HEIGHT
        x = PADDING

        if row[0] == "header":
            svg.append(f'  <text x="{x}" y="{y}" fill="{text_color}" font-size="{FONT_SIZE}" font-weight="bold">{escape_xml(row[1])}</text>')

        elif row[0] == "section":
            svg.append(f'  <text x="{x}" y="{y}" fill="{section_color}" font-size="{FONT_SIZE}" font-weight="bold">{escape_xml(row[1])}</text>')

        elif row[0] == "kv":
            _, key, value = row
            key_width = text_width(key)
            value_width = text_width(value)

            # Calculate dots length to fill space between key and value
            dots_max_width = MAX_WIDTH - PADDING - key_width - value_width - 20
            dots_max_width = max(4, dots_max_width)
            dots_count = max(1, int(dots_max_width / MONO_CHAR_WIDTH))
            dots = "." * dots_count

            dots_x = x + key_width
            dots_text_x = dots_x
            value_x = dots_x + text_width(dots) + 10

            svg.append(f'  <text x="{x}" y="{y}" fill="{text_color}" font-size="{FONT_SIZE}">{escape_xml(key)}</text>')
            svg.append(f'  <text x="{dots_text_x}" y="{y}" fill="{separator_color}" font-size="{FONT_SIZE}">{escape_xml(dots)}</text>')
            svg.append(f'  <text x="{value_x}" y="{y}" fill="{value_color}" font-size="{FONT_SIZE}">{escape_xml(value)}</text>')

        elif row[0] == "blank":
            pass  # No output, just spacing

    svg.append("</svg>")
    return "\n".join(svg)


def main():
    """Main entry point."""
    print(f"Generating profile SVGs for @{USER_NAME}...")

    # Fetch stats
    stats, err = get_user_stats()
    if err:
        print(f"Error fetching stats: {err}")
        print("Using fallback stats.")

    if not stats:
        stats = {
            "public_repos": 6,
            "followers": 0,
            "stars": 0,
            "bio": "AI Agent · Code Reviewer · OSS Contributor"
        }

    # Generate both themes
    for theme in ["light", "dark"]:
        svg_content = generate_svg(stats, theme)
        filename = f"{theme}_mode.svg"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(svg_content)

        print(f"✓ Generated {filename}")


if __name__ == "__main__":
    main()

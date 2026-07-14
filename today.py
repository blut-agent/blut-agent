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
        "stars": public_repos,  # Approximation
    }, None


def get_contributions(token=""):
    """Get contribution count (approximate from events)."""
    # We'll use a simple approximation: public_repos * avg_contributions
    # For accurate data, we'd need to parse events for the last year
    # This is a simplified version
    return 0, "N/A"


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
    except:
        return "Unknown"


def generate_svg(stats, theme="light"):
    """Generate the fastfetch-style SVG."""
    
    # Color schemes
    if theme == "dark":
        bg_color = "#0d1117"
        text_color = "#c9d1d9"
        accent_color = "#58a6ff"
        separator_color = "#30363d"
        section_color = "#7ee787"
        value_color = "#a5d6ff"
        header_color = "#f0f6fc"
        link_color = "#58a6ff"
    else:
        bg_color = "#ffffff"
        text_color = "#24292f"
        accent_color = "#0969da"
        separator_color = "#d0d7de"
        section_color = "#1a7f37"
        value_color = "#0550ae"
        header_color = "#1f2328"
        link_color = "#0969da"
    
    # Build the content lines
    lines = []
    separator = "─" * 70
    
    # Header
    lines.append(f" blut-agent@blut-agent {separator}")
    
    # Identity section
    lines.append(f" OS: {'Hermes Agent · Telegram Bot' if theme == 'dark' else 'Hermes Agent · Telegram Bot'}")
    
    # Calculate "uptime" from birthday
    uptime = parse_birthday(BIRTHDAY)
    lines.append(f" Uptime: {uptime}")
    lines.append(f" Host: Edgardo Yoliani (Yoliani)")
    
    # Kernel/Bio
    bio = stats.get("bio", "AI Agent · Code Reviewer · OSS Contributor")
    lines.append(f" Kernel: {bio}")
    
    # Editor & Tools
    lines.append(f" Editor: Neovim, VS Code, Telegram")
    lines.append(f" Terminal: tmux, fzf, ripgrep")
    
    # Empty line
    lines.append("")
    
    # Languages
    lines.append(f" Languages.Programming: ... Python, TypeScript, YAML")
    lines.append(f" Languages.Real: ........ Spanish, English")
    
    # Empty line
    lines.append("")
    
    # Stack
    lines.append(f" Stack.AI: .............. LLMs, RAG, Agents, Prompting")
    lines.append(f" Stack.Tools: ........... Git, gh CLI, MCP, Hermes Agent")
    lines.append(f" Stack.Domain: .......... Code Review, OSS Contribution, Task Management")
    
    # Empty line
    lines.append("")
    
    # Owner section
    lines.append(f" - Owner {separator}")
    lines.append(f" Name: ........................ Edgardo Yoliani")
    lines.append(f" GitHub: ........................ github.com/Yoliani")
    
    # Empty line
    lines.append("")
    
    # GitHub Stats
    lines.append(f" - GitHub Stats {separator}")
    repos = stats.get("public_repos", 0)
    followers = stats.get("followers", 0)
    stars = stats.get("stars", 0)
    
    lines.append(f" Repos: .... {repos} | Stars: ............ {stars}")
    lines.append(f" Followers: .... {followers} | Contributions: .. Live")
    
    # Render SVG
    return render_svg(lines, bg_color, text_color, accent_color, separator_color, 
                      section_color, value_color, header_color, link_color)


def render_svg(lines, bg_color, text_color, accent_color, separator_color,
               section_color, value_color, header_color, link_color):
    """Render lines to SVG with monospace font styling."""
    
    font_family = '"Cascadia Code", "Fira Code", "JetBrains Mono", "SF Mono", Menlo, Consolas, monospace'
    font_size = 14
    line_height = 20
    padding = 40
    width = 800
    height = padding * 2 + len(lines) * line_height
    
    svg_elements = []
    svg_elements.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" font-family="{font_family}">')
    
    # Background
    svg_elements.append(f'  <rect width="100%" height="100%" fill="{bg_color}"/>')
    
    # Lines
    for i, line in enumerate(lines):
        y = padding + i * line_height
        x = padding
        
        # Detect sections (lines starting with "-")
        if line.strip().startswith("-"):
            # Section header
            svg_elements.append(f'  <text x="{x}" y="{y}" fill="{section_color}" font-size="{font_size}" font-weight="bold">{escape_xml(line)}</text>')
        elif ":" in line and not line.strip().startswith("-"):
            # Key: Value lines
            parts = line.split(":", 1)
            key = parts[0]
            value = parts[1] if len(parts) > 1 else ""
            
            # Find the dots separator position
            dot_match = None
            for idx, char in enumerate(key):
                if char == ".":
                    dot_match = idx
                    break
            
            if dot_match:
                # Split at dots
                key_part = key[:dot_match]
                dots_and_value = key[dot_match:]
                
                # Key text
                svg_elements.append(f'  <text x="{x}" y="{y}" fill="{text_color}" font-size="{font_size}">{escape_xml(key_part)}</text>')
                
                # Dots (repeated character)
                dots_start = x + len(key_part) * font_size * 0.6  # Approximate monospace width
                dots_end = min(dots_start + len(dots_and_value) * font_size * 0.6, width - padding - 200)
                dots_count = max(1, int((dots_end - dots_start) / (font_size * 0.6)))
                dots_text = "." * dots_count
                svg_elements.append(f'  <text x="{dots_start}" y="{y}" fill="{separator_color}" font-size="{font_size}">{escape_xml(dots_text)}</text>')
                
                # Value
                svg_elements.append(f'  <text x="{dots_end + 10}" y="{y}" fill="{value_color}" font-size="{font_size}">{escape_xml(value.strip())}</text>')
            else:
                svg_elements.append(f'  <text x="{x}" y="{y}" fill="{text_color}" font-size="{font_size}">{escape_xml(line)}</text>')
        else:
            svg_elements.append(f'  <text x="{x}" y="{y}" fill="{text_color}" font-size="{font_size}">{escape_xml(line)}</text>')
    
    svg_elements.append(f'</svg>')
    return "\n".join(svg_elements)


def escape_xml(text):
    """Escape XML special characters."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;"))


def main():
    """Main entry point."""
    print(f"Generating profile SVGs for @{USER_NAME}...")
    
    # Fetch stats
    stats, err = get_user_stats()
    if err:
        print(f"Error fetching stats: {err}")
        print("Using cached/placeholder stats.")
    
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

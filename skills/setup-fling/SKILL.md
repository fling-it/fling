---
name: setup-fling
description: >
  Initialize a new Fling project — a personal software platform with React
  frontend, Hono API backend, SQLite database, and Cloudflare Workers deployment.
  Use when the user wants to create a new Fling project or asks about Fling.
allowed-tools: Bash(python3 *), Bash(npm install*), Read
---

# Setup Fling Project

Initialize a new Fling project in the current directory.

## Steps

1. **Verify the current directory is empty.** If it contains files, confirm with the user before proceeding — they should create a new empty directory first.

2. **Run the init script** to scaffold the project:
   ```bash
   python3 `echo $CLAUDE_PLUGIN_ROOT`/skills/setup-fling/scripts/init.py
   ```

3. **Install dependencies:**
   ```bash
   npm install
   ```

4. **Read the project skill** to understand what the user can build:
   ```
   Read .claude/skills/fling/SKILL.md
   ```

5. **Tell the user what was created:**
   - React frontend with Tailwind CSS
   - Hono API backend with typed routes
   - SQLite database with migrations
   - Cron job support
   - Static file storage
   - Cloudflare Workers deployment via `fling push`

6. **Ask the user what they want to build.** Suggest ideas based on the project capabilities.

7. **Mention** they can also just open Claude Code in this directory anytime to continue working on their project.

# Milestone 3: Git and GitHub Workflow

This guide walks you through the complete Git workflow for Milestone 3. If you've never used Git before, think of it like this: **Git is to code what tracked changes in a Word document is to writing** — except far more powerful. It records a full history of every change you've made so you can always go back, see what changed, and collaborate with teammates without overwriting each other's work.

---

## 1. Concepts: Git vs. GitHub

These two things are often confused but are distinct:

| Term | What it is |
|------|-----------|
| **Git** | A program that runs on your computer and tracks changes to your files locally |
| **GitHub** | A website that hosts a copy of your repository online so others can access it |

The analogy: Git is like saving versions of your Python script on your own machine. GitHub is like uploading that script to Google Drive so your teammates can download it.

---

## 2. First-Time Setup

### 2a. Create a GitHub Account

Go to [https://github.com](https://github.com) and sign up for a free account if you don't already have one. All group members need an account.

### 2b. Generate a Personal Access Token (PAT)

GitHub no longer accepts passwords over the command line. Instead it uses **Personal Access Tokens (PATs)** — treat these like a password.

1. Log in to GitHub
2. Click your profile picture (top right) → **Settings**
3. Scroll down to **Developer Settings** → **Personal Access Tokens** → **Tokens (classic)**
4. Click **Generate new token (classic)**
5. Give it a name (e.g., "jhub"), set expiration, and **check all permission boxes**
6. Click **Generate token** and **copy it immediately** — you will only see it once

> **Tip:** Save your token in a plain text file on JupyterHub so you can copy it again when Git asks for your password. You can run the following in a terminal to create the file and lock it down so only you can read it:
> ```bash
> echo "YOUR_TOKEN_HERE" > ~/.github_token
> chmod 600 ~/.github_token
> ```
> `chmod 600` sets the file permissions so that only your user account can read or write it — no one else on the system can view it. When Git later asks for your password, you can quickly retrieve the token with `cat ~/.github_token` and paste it in. Replace `YOUR_TOKEN_HERE` with your actual token before running the command.

### 2c. Configure Git with Your Identity

Git needs to know who you are so it can label your commits. Run these once in a terminal (replace with your own name and email):

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

You can verify the settings were saved with:

```bash
git config --list
```

---

## 3. Creating a Repository (One Group Member Does This Section)

Only **one group member** needs to create the repository. The others will clone it later.

### Step 1: Create the Repository on GitHub

1. Log in to GitHub
2. Click the **+** (top right) → **New repository**
3. Name it something descriptive (e.g., `meteo473-sp26-group1`)
4. Set it to **Public**
5. **Do not** initialize with a README (you'll add one from the command line)
6. Click **Create repository** — keep this page open, you'll need the URL

### Step 2: Initialize Git in Your Project Directory

Open a terminal on JupyterHub and navigate to your group project directory:

```bash
cd /courses/meteo473/<semester>/473_<semester>_group<#>
```

For example: `cd /courses/meteo473/sp26/473_sp26_group1`

Then initialize Git:

```bash
git init
```

This creates a hidden `.git/` folder that Git uses to track your project — you never need to touch that folder directly.

### Step 3: Create a .gitignore File

Before adding any files, create a `.gitignore` to tell Git which files to **always ignore**. This is critical — large data files (NetCDF, GRIB2) should never go on GitHub.

Create a file named `.gitignore` in your project directory with this content:

```
# Data files — too large for GitHub
*.nc
*.grib2
*.grb
*.grb2
*.idx

# Jupyter checkpoint folders
.ipynb_checkpoints/

# Python cache
__pycache__/
*.pyc

# macOS junk
.DS_Store
```

> **Why this matters:** GitHub has a 100 MB file size limit. Accidentally pushing a large NetCDF will cause your push to fail (or get your account flagged). A `.gitignore` prevents this.

### Step 4: Stage, Commit, and Push

```bash
# See the current state of all files
git status

# Stage all files you want to include (. means "everything in this directory")
git add .

# Double-check what's staged
git status

# Make your first commit with a descriptive message
git commit -m "Initial commit: add project notebooks and scripts"

# Set the main branch name (run this once)
git branch -M main

# Connect your local repo to GitHub (paste the URL from Step 1)
git remote add origin https://github.com/yourusername/your-repo-name.git

# Push to GitHub
git push -u origin main
```

When prompted for a username, use your GitHub username. When prompted for a password, **paste your Personal Access Token** (not your GitHub password).

---

## 4. Adding Collaborators (Repository Owner Does This)

The group member who created the repository needs to add the others as collaborators:

1. On GitHub, go to your repository
2. Click **Settings** → **Collaborators** → **Add people**
3. Search for each teammate's GitHub username and invite them

Each invited member will receive an email and must **accept the invitation** before they can push changes.

---

## 5. Cloning the Repository (Other Group Members Do This)

Once invited, each other group member clones (downloads) the repository:

```bash
# Move to your home directory (NOT your group project directory)
cd ~

# Clone the repository — this creates a new folder with all the project files
git clone https://github.com/yourusername/your-repo-name.git

# Enter the new folder
cd your-repo-name
```

> **Note:** Clone into your home directory (`~`), **not** into your group project directory at `/courses/meteo473/<semester>/473_<semester>_group<#>` — these should be two separate locations.

You now have a local copy. The connection to GitHub is already set up — no need to run `git remote add`.

---

## 6. The Daily Workflow: Pull → Edit → Add → Commit → Push

Every time you sit down to work, follow this pattern to avoid conflicts:

```bash
# 1. Always pull the latest changes from GitHub first
git pull origin main

# 2. Make your changes (edit files, add notebooks, etc.)

# 3. Check what changed
git status

# 4. Stage the files you want to commit
git add filename.py           # add a specific file
git add .                     # or add everything

# 5. Commit with a clear message describing what you did
git commit -m "Add threat index function and plot for f000-f024"

# 6. Push your changes to GitHub
git push origin main
```

> **Think of commits like Python print statements during debugging** — they're checkpoints that let you understand what happened and when.

---

## 7. The README

Your repository must include a `README.md` file. GitHub displays this automatically on your repository's main page. Here's a minimal example (edit to fit your own project):

```markdown
# Meteo 473 Threat Index — Group 1

## Project Description
We developed a wildfire threat index using GFS model data...

## Group Members
- Alice Smith
- Bob Jones
- Carol Lee

## How to Run
1. Download data by running `download_data.py`
2. Generate plots by running `threat_index.py`

## License
MIT
```

Use `# ` for headings, `**bold**` for bold, and `-` for bullet points. GitHub renders full Markdown formatting automatically.

---

## 8. Choosing a License

GitHub will prompt you to add a license. For a class project, **MIT License** is a safe, standard choice — it lets others use your code freely while giving you credit. You can add it when creating the repo or manually create a file called `LICENSE` from GitHub's template picker.

---

## 9. Common Issues and Fixes

### "Authentication failed" when pushing
You entered your GitHub password instead of your PAT. Re-run the push and paste the token when prompted for a password.

### "error: failed to push some refs"
Someone else pushed new commits after you last pulled. Run:
```bash
git pull origin main
```
Resolve any conflicts, then push again.

### I accidentally staged a file I didn't mean to
```bash
git restore --staged filename.py
```

### I want to undo my last commit (before pushing)
```bash
git reset --soft HEAD~1
```
This un-commits your most recent commit but keeps your file changes intact.

### Merge conflict
This happens when two people edited the same part of the same file. Git will mark the conflict inside the file with `<<<<<<<` and `>>>>>>>` markers. Open the file, decide which version to keep (or combine them), delete the markers, then `git add` and `git commit` the resolved file.

---

## Quick Reference Card

| Command | What it does |
|---------|-------------|
| `git init` | Initialize a new local repository |
| `git status` | Show which files are staged, modified, or untracked |
| `git add <file>` | Stage a file for the next commit |
| `git add .` | Stage all modified/new files |
| `git commit -m "msg"` | Save a snapshot with a message |
| `git log --oneline` | Show a compact commit history |
| `git push origin main` | Upload commits to GitHub |
| `git pull origin main` | Download latest commits from GitHub |
| `git clone <url>` | Copy a remote repository to your machine |
| `git diff` | Show unstaged changes line by line |
| `git restore --staged <file>` | Unstage a file without losing changes |

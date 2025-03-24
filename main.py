import git
import os
import tempfile
import shutil
import sys
import time
from pathlib import Path


def build_tree_structure(file_data):
    """Builds a tree structure from file paths."""
    tree = {'dirs': {}, 'files': {}}
    for file_path in file_data:
        parts = file_path.split('/')
        current = tree
        for part in parts[:-1]:
            if part not in current['dirs']:
                current['dirs'][part] = {'dirs': {}, 'files': {}}
            current = current['dirs'][part]
        current['files'][parts[-1]] = file_data[file_path]
    return tree


def aggregate_tree(node):
    """Aggregates lines of code and commits up the tree."""
    total_lines = 0
    all_commits = set()
    for file_name, data in node['files'].items():
        total_lines += data['lines']
        all_commits.update(data['commits'])
    for dir_name, subnode in node['dirs'].items():
        sub_lines, sub_commits = aggregate_tree(subnode)
        total_lines += sub_lines
        all_commits.update(sub_commits)
    node['lines'] = total_lines
    node['commits'] = all_commits
    return total_lines, all_commits


def print_tree(node, level=0):
    """Generates a pretty Markdown list for the tree structure."""
    lines = []
    dir_names = sorted(node['dirs'].keys())
    file_names = sorted(node['files'].keys())

    for dir_name in dir_names:
        subnode = node['dirs'][dir_name]
        lines.append(f"{'  ' * level}- **{dir_name}/** (Lines: {subnode['lines']}, Commits: {len(subnode['commits'])})")
        lines.extend(print_tree(subnode, level + 1))

    for file_name in file_names:
        data = node['files'][file_name]
        lines.append(f"{'  ' * level}- `{file_name}` (Lines: {data['lines']}, Commits: {len(data['commits'])})")

    return lines


def safe_rmtree(path):
    """Safely remove a directory tree, handling permission errors on Windows."""

    def remove_readonly(func, path, _):
        os.chmod(path, 0o777)
        func(path)

    for _ in range(5):  # Retry up to 5 times
        try:
            shutil.rmtree(path, onerror=remove_readonly)
            break
        except PermissionError:
            time.sleep(1)  # Wait briefly before retrying
    else:
        print(f"Warning: Could not fully remove temporary directory {path}", file=sys.stderr)


def get_repo_name(repo_url):
    """Extracts the repository name from the URL."""
    return repo_url.split('/')[-1].replace('.git', '')


def analyze_repo(repo_url):
    """Analyzes the GitHub repository and generates Markdown reports."""
    temp_dir = tempfile.mkdtemp()
    repo_name = get_repo_name(repo_url)
    report_dir = Path('reports') / repo_name
    report_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Convert HTTPS URL to SSH if needed, but prefer HTTPS for public repos
        if repo_url.startswith('https://github.com/'):
            clone_url = repo_url + '.git' if not repo_url.endswith('.git') else repo_url
        elif repo_url.startswith('git@github.com:'):
            clone_url = repo_url
        else:
            raise ValueError(
                "Invalid GitHub URL. Use HTTPS (https://github.com/...) or SSH (git@github.com:...) format.")

        # Clone the repository
        git.Repo.clone_from(clone_url, temp_dir)
        repo = git.Repo(temp_dir)

        # Get all tracked files
        tracked_files = [f for f in repo.git.ls_files().split('\n') if f]

        # Calculate lines and commits per file
        file_data = {}
        for file_path in tracked_files:
            with open(os.path.join(temp_dir, file_path), 'r', encoding='utf-8', errors='ignore') as f:
                lines = sum(1 for line in f)
            commits = set(repo.git.log('--follow', '--pretty=format:%H', file_path).split('\n'))
            file_data[file_path] = {'lines': lines, 'commits': commits}

        # Build and aggregate the folder structure
        tree = build_tree_structure(file_data)
        aggregate_tree(tree)

        # Get commit history (oldest to newest)
        commits = list(repo.iter_commits())
        commits.reverse()
        authors = set(commit.author.name for commit in commits)

        # Signature for all reports
        signature = (
            "\n---\n"
            f"Generated with [Q-Git](https://github.com/QLineTech/Q-Git) on {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # Generate repo_info.md
        with open(report_dir / 'repo_info.md', 'w', encoding='utf-8') as f:
            f.write("# Repository Information\n\n")
            f.write("| Metric                | Value                                      |\n")
            f.write("|-----------------------|--------------------------------------------|\n")
            f.write(f"| Total Lines of Code  | {tree['lines']}                           |\n")
            f.write(f"| Total Commits        | {len(commits)}                            |\n")
            f.write(f"| Contributors         | {len(authors)}                            |\n")
            f.write(f"| Creation Date        | {commits[0].committed_datetime.strftime('%Y-%m-%d %H:%M:%S')} |\n")
            f.write(f"| Last Update          | {commits[-1].committed_datetime.strftime('%Y-%m-%d %H:%M:%S')} |\n")
            f.write(signature)

        # Generate folder_structure.md
        with open(report_dir / 'folder_structure.md', 'w', encoding='utf-8') as f:
            f.write("# Folder Structure\n\n")
            f.write("```markdown\n")
            f.write("\n".join(print_tree(tree)))
            f.write("\n```\n")
            f.write(signature)

        # Generate timeline.md
        with open(report_dir / 'timeline.md', 'w', encoding='utf-8') as f:
            f.write("# Development Timeline\n\n")
            f.write("| Date                | Author          | Message                  | Changes         |\n")
            f.write("|---------------------|-----------------|--------------------------|-----------------|\n")
            for commit in commits:
                date = commit.committed_datetime.strftime("%Y-%m-%d %H:%M:%S")
                author = commit.author.name
                message = commit.message.strip().replace('\n', ' ')
                stats = commit.stats.total
                changes = f"+{stats['insertions']}, -{stats['deletions']}"
                f.write(f"| {date} | {author} | {message[:50]}{'...' if len(message) > 50 else ''} | {changes} |\n")
            f.write(signature)

        # Generate full_report.md
        with open(report_dir / 'full_report.md', 'w', encoding='utf-8') as f:
            f.write("# Full Repository Report\n\n")
            f.write("![Q-Git Badge](https://img.shields.io/badge/Q--Git-Analyzed-blue?style=flat-square)\n\n")
            f.write("## Repository Information\n\n")
            with open(report_dir / 'repo_info.md', 'r', encoding='utf-8') as repo_file:
                f.write(repo_file.read().split("---")[0])  # Exclude signature
            f.write("\n## Folder Structure\n\n")
            with open(report_dir / 'folder_structure.md', 'r', encoding='utf-8') as folder_file:
                f.write(folder_file.read().split("---")[0])  # Exclude signature
            f.write("\n## Timeline\n\n")
            with open(report_dir / 'timeline.md', 'r', encoding='utf-8') as timeline_file:
                f.write(timeline_file.read().split("---")[0])  # Exclude signature
            f.write(signature)

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        raise
    finally:
        safe_rmtree(temp_dir)


if __name__ == "__main__":
    repo_url = input("Enter the GitHub repo URL: ").strip()
    analyze_repo(repo_url)
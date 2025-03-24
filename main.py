import git
import os
import tempfile
import shutil
import sys
import time
from pathlib import Path
from collections import defaultdict

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

def get_language_labels(lang):
    """Returns labels for Markdown reports based on the selected language."""
    labels = {
        "EN": {
            "repo_info_title": "Repository Information",
            "folder_structure_title": "Folder Structure",
            "timeline_title": "Development Timeline",
            "full_report_title": "Full Repository Report",
            "contributors_title": "Contributors Analysis",
            "languages_title": "Programming Languages",
            "frameworks_title": "Frameworks Used",
            "user_contrib_title": "Projects Contributed Summary",
            "user_projects_title": "User Projects Summary",
            "user_full_title": "Full User Summary",
            "metrics": {
                "total_lines": "Total Lines of Code",
                "total_commits": "Total Commits",
                "contributors": "Contributors",
                "creation_date": "Creation Date",
                "last_update": "Last Update"
            },
            "timeline_headers": ["Date", "Author", "Message", "Changes"],
            "contributors_headers": ["Contributor", "GitHub Link", "Lines of Code", "Commits"],
            "languages_headers": ["Language", "Lines of Code", "Percentage"],
            "frameworks_headers": ["Framework", "Indicator File"]
        },
        "TR": {
            "repo_info_title": "Depo Bilgileri",
            "folder_structure_title": "Klasör Yapısı",
            "timeline_title": "Geliştirme Zaman Çizelgesi",
            "full_report_title": "Tam Depo Raporu",
            "contributors_title": "Katkıda Bulunanlar Analizi",
            "languages_title": "Programlama Dilleri",
            "frameworks_title": "Kullanılan Çerçeveler",
            "user_contrib_title": "Katkı Sağlanan Projeler Özeti",
            "user_projects_title": "Kullanıcı Projeleri Özeti",
            "user_full_title": "Tam Kullanıcı Özeti",
            "metrics": {
                "total_lines": "Toplam Kod Satırı",
                "total_commits": "Toplam Commit",
                "contributors": "Katkıda Bulunanlar",
                "creation_date": "Oluşturma Tarihi",
                "last_update": "Son Güncelleme"
            },
            "timeline_headers": ["Tarih", "Yazar", "Mesaj", "Değişiklikler"],
            "contributors_headers": ["Katkıda Bulunan", "GitHub Bağlantısı", "Kod Satırları", "Commit Sayısı"],
            "languages_headers": ["Dil", "Kod Satırları", "Yüzde"],
            "frameworks_headers": ["Çerçeve", "Gösterge Dosyası"]
        }
        # Add IT, FR, ES, DE translations similarly if needed (omitted for brevity)
    }
    return labels.get(lang.upper(), labels["EN"])  # Default to English

def print_progress(step, total_steps, message):
    """Prints progress with percentage and a simple progress bar."""
    percentage = (step / total_steps) * 100
    bar_length = 20
    filled = int(bar_length * step // total_steps)
    bar = '█' * filled + ' ' * (bar_length - filled)
    sys.stdout.write(f"\r{message} [{bar}] {percentage:.1f}%")
    sys.stdout.flush()

def detect_languages(file_data):
    """Detects programming languages based on file extensions."""
    language_map = {
        '.py': 'Python', '.js': 'JavaScript', '.java': 'Java', '.cpp': 'C++', '.c': 'C',
        '.cs': 'C#', '.rb': 'Ruby', '.php': 'PHP', '.go': 'Go', '.rs': 'Rust'
    }
    languages = defaultdict(int)
    total_lines = sum(data['lines'] for data in file_data.values())
    for file_path, data in file_data.items():
        ext = os.path.splitext(file_path)[1]
        lang = language_map.get(ext, 'Unknown')
        languages[lang] += data['lines']
    return languages, total_lines

def detect_frameworks(tracked_files):
    """Detects frameworks based on common files."""
    frameworks = {}
    for file_path in tracked_files:
        if file_path == 'package.json':
            frameworks['Node.js'] = 'package.json'
        elif file_path == 'requirements.txt':
            frameworks['Python (Pip)'] = 'requirements.txt'
        elif file_path == 'pom.xml':
            frameworks['Maven (Java)'] = 'pom.xml'
        elif file_path == 'Gemfile':
            frameworks['Ruby on Rails'] = 'Gemfile'
    return frameworks

def analyze_repo(repo_url, lang="EN"):
    """Analyzes the GitHub repository and generates Markdown reports."""
    total_steps = 10
    step = 0
    print_progress(step, total_steps, "📋 Starting repository analysis...")
    step += 1
    temp_dir = tempfile.mkdtemp()
    repo_name = get_repo_name(repo_url)
    report_dir = Path('reports') / repo_name
    report_dir.mkdir(parents=True, exist_ok=True)

    try:
        labels = get_language_labels(lang)

        print_progress(step, total_steps, "🔗 Validating repository URL...")
        step += 1
        if repo_url.startswith('https://github.com/'):
            clone_url = repo_url + '.git' if not repo_url.endswith('.git') else repo_url
        elif repo_url.startswith('git@github.com:'):
            clone_url = repo_url
        else:
            raise ValueError("Invalid GitHub URL. Use HTTPS (https://github.com/...) or SSH (git@github.com:...) format.")

        print_progress(step, total_steps, "📥 Cloning repository...")
        step += 1
        git.Repo.clone_from(clone_url, temp_dir)
        repo = git.Repo(temp_dir)

        print_progress(step, total_steps, "📄 Collecting tracked files...")
        step += 1
        tracked_files = [f for f in repo.git.ls_files().split('\n') if f]

        print_progress(step, total_steps, "📊 Analyzing files and commits...")
        step += 1
        file_data = {}
        for file_path in tracked_files:
            with open(os.path.join(temp_dir, file_path), 'r', encoding='utf-8', errors='ignore') as f:
                lines = sum(1 for line in f)
            commits = set(repo.git.log('--follow', '--pretty=format:%H', file_path).split('\n'))
            file_data[file_path] = {'lines': lines, 'commits': commits}

        print_progress(step, total_steps, "🌳 Building folder structure...")
        step += 1
        tree = build_tree_structure(file_data)
        aggregate_tree(tree)

        print_progress(step, total_steps, "⏳ Fetching commit history...")
        step += 1
        commits = list(repo.iter_commits())
        commits.reverse()
        authors = set(commit.author.name for commit in commits)

        print_progress(step, total_steps, "🔍 Analyzing languages and frameworks...")
        step += 1
        languages, total_lines = detect_languages(file_data)
        frameworks = detect_frameworks(tracked_files)

        # Contributor analysis (separate from repo_info)
        contributor_data = defaultdict(lambda: {'commits': [], 'lines_added': 0, 'lines_removed': 0})
        for commit in commits:
            author = commit.author.name
            stats = commit.stats.total
            contributor_data[author]['commits'].append({
                'date': commit.committed_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                'message': commit.message.strip().replace('\n', ' '),
                'lines_added': stats['insertions'],
                'lines_removed': stats['deletions']
            })
            contributor_data[author]['lines_added'] += stats['insertions']
            contributor_data[author]['lines_removed'] += stats['deletions']

        signature = (
            "\n---\n"
            f"Generated with [Q-Git](https://github.com/QLineTech/Q-Git) on {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        print_progress(step, total_steps, "📝 Generating repo_info.md...")
        step += 1
        with open(report_dir / 'repo_info.md', 'w', encoding='utf-8') as f:
            f.write(f"# {labels['repo_info_title']}\n\n")
            f.write("| Metric                | Value                                      |\n")
            f.write("|-----------------------|--------------------------------------------|\n")
            f.write(f"| {labels['metrics']['total_lines']}  | {tree['lines']}                           |\n")
            f.write(f"| {labels['metrics']['total_commits']}        | {len(commits)}                            |\n")
            f.write(f"| {labels['metrics']['contributors']}         | {len(authors)}                            |\n")
            f.write(f"| {labels['metrics']['creation_date']}        | {commits[0].committed_datetime.strftime('%Y-%m-%d %H:%M:%S')} |\n")
            f.write(f"| {labels['metrics']['last_update']}          | {commits[-1].committed_datetime.strftime('%Y-%m-%d %H:%M:%S')} |\n")
            f.write(f"\n## {labels['languages_title']}\n\n")
            f.write(f"| {labels['languages_headers'][0]} | {labels['languages_headers'][1]} | {labels['languages_headers'][2]} |\n")
            f.write("|------------|------------------|-----------------|\n")
            for lang_name, lines in sorted(languages.items(), key=lambda x: x[1], reverse=True):
                percentage = (lines / total_lines) * 100 if total_lines > 0 else 0
                f.write(f"| {lang_name} | {lines} | {percentage:.2f}% |\n")
            f.write(f"\n## {labels['frameworks_title']}\n\n")
            f.write(f"| {labels['frameworks_headers'][0]} | {labels['frameworks_headers'][1]} |\n")
            f.write("|------------|------------------|\n")
            for framework, indicator in frameworks.items():
                f.write(f"| {framework} | {indicator} |\n")
            f.write(signature)

        with open(report_dir / 'folder_structure.md', 'w', encoding='utf-8') as f:
            f.write(f"# {labels['folder_structure_title']}\n\n")
            f.write("```markdown\n")
            f.write("\n".join(print_tree(tree)))
            f.write("\n```\n")
            f.write(signature)

        with open(report_dir / 'timeline.md', 'w', encoding='utf-8') as f:
            f.write(f"# {labels['timeline_title']}\n\n")
            f.write(f"| {labels['timeline_headers'][0]} | {labels['timeline_headers'][1]} | {labels['timeline_headers'][2]} | {labels['timeline_headers'][3]} |\n")
            f.write("|---------------------|-----------------|--------------------------|-----------------|\n")
            for commit in commits:
                date = commit.committed_datetime.strftime("%Y-%m-%d %H:%M:%S")
                author = commit.author.name
                message = commit.message.strip().replace('\n', ' ')
                stats = commit.stats.total
                changes = f"+{stats['insertions']}, -{stats['deletions']}"
                f.write(f"| {date} | {author} | {message[:50]}{'...' if len(message) > 50 else ''} | {changes} |\n")
            f.write(signature)

        with open(report_dir / 'contributors.md', 'w', encoding='utf-8') as f:
            f.write(f"# {labels['contributors_title']}\n\n")
            f.write(f"| {labels['contributors_headers'][0]} | {labels['contributors_headers'][1]} | {labels['contributors_headers'][2]} | {labels['contributors_headers'][3]} |\n")
            f.write("|-------------------|-------------------|-------------------|-------------------|\n")
            for author, data in sorted(contributor_data.items()):
                github_link = "Not Available"
                total_lines_contrib = data['lines_added'] - data['lines_removed']
                f.write(f"| {author} | {github_link} | {total_lines_contrib} | {len(data['commits'])} |\n")
            f.write("\n## Contributor Timelines\n\n")
            for author, data in sorted(contributor_data.items()):
                f.write(f"### {author}\n\n")
                f.write(f"| {labels['timeline_headers'][0]} | {labels['timeline_headers'][2]} | {labels['timeline_headers'][3]} |\n")
                f.write("|---------------------|--------------------------|-----------------|\n")
                for commit in sorted(data['commits'], key=lambda x: x['date']):
                    f.write(f"| {commit['date']} | {commit['message'][:50]}{'...' if len(commit['message']) > 50 else ''} | +{commit['lines_added']}, -{commit['lines_removed']} |\n")
                f.write("\n")
            f.write(signature)

        print_progress(step, total_steps, "📝 Generating full_report.md...")
        step += 1
        with open(report_dir / 'full_report.md', 'w', encoding='utf-8') as f:
            f.write(f"# {labels['full_report_title']}\n\n")
            f.write("![Q-Git Badge](https://img.shields.io/badge/Q--Git-Analyzed-blue?style=flat-square)\n\n")
            f.write(f"## {labels['repo_info_title']}\n\n")
            with open(report_dir / 'repo_info.md', 'r', encoding='utf-8') as repo_file:
                f.write(repo_file.read().split("---")[0])  # Exclude signature
            f.write(f"\n## {labels['folder_structure_title']}\n\n")
            with open(report_dir / 'folder_structure.md', 'r', encoding='utf-8') as folder_file:
                f.write(folder_file.read().split("---")[0])
            f.write(f"\n## {labels['timeline_title']}\n\n")
            with open(report_dir / 'timeline.md', 'r', encoding='utf-8') as timeline_file:
                f.write(timeline_file.read().split("---")[0])
            f.write(signature)

        print_progress(total_steps, total_steps, "✅ Analysis complete! Reports in: " + str(report_dir))
        print()

    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        raise
    finally:
        print_progress(total_steps, total_steps, "🧹 Cleaning up temporary files...")
        print()
        safe_rmtree(temp_dir)

def analyze_git_user(username, lang="EN"):
    """Analyzes a GitHub user's contributions and projects (mock implementation)."""
    total_steps = 8
    step = 0
    print_progress(step, total_steps, "📋 Starting GitHub user analysis...")
    step += 1

    # Mock data (replace with GitHub API calls in production)
    labels = get_language_labels(lang)
    report_dir = Path('reports') / f"user_{username}"
    report_dir.mkdir(parents=True, exist_ok=True)

    # Mock contributed projects
    print_progress(step, total_steps, "🔍 Fetching contributed projects...")
    step += 1
    contrib_projects = [
        {"name": "repo1", "lines": 500, "commits": 10, "languages": {"Python": 400, "JavaScript": 100}, "frameworks": {"Node.js": "package.json"}},
        {"name": "repo2", "lines": 300, "commits": 5, "languages": {"Java": 300}, "frameworks": {"Maven": "pom.xml"}}
    ]

    print_progress(step, total_steps, "🔍 Fetching user projects...")
    step += 1
    user_projects = [
        {"name": "myrepo", "lines": 1000, "commits": 20, "languages": {"Python": 1000}, "frameworks": {"Python (Pip)": "requirements.txt"}}
    ]

    print_progress(step, total_steps, "📊 Summarizing contributions...")
    step += 1
    contrib_lines = sum(p["lines"] for p in contrib_projects)
    contrib_commits = sum(p["commits"] for p in contrib_projects)
    contrib_langs = defaultdict(int)
    contrib_frameworks = {}
    for p in contrib_projects:
        for lang, lines in p["languages"].items():
            contrib_langs[lang] += lines
        contrib_frameworks.update(p["frameworks"])

    print_progress(step, total_steps, "📊 Summarizing user projects...")
    step += 1
    user_lines = sum(p["lines"] for p in user_projects)
    user_commits = sum(p["commits"] for p in user_projects)
    user_langs = defaultdict(int)
    user_frameworks = {}
    for p in user_projects:
        for lang, lines in p["languages"].items():
            user_langs[lang] += lines
        user_frameworks.update(p["frameworks"])

    print_progress(step, total_steps, "⏳ Generating timeline...")
    step += 1
    timeline = [
        {"date": "2023-01-01", "action": "Contributed to repo1", "changes": "+500, -0"},
        {"date": "2023-02-01", "action": "Created myrepo", "changes": "+1000, -0"}
    ]

    signature = (
        "\n---\n"
        f"Generated with [Q-Git](https://github.com/QLineTech/Q-Git) on {time.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    print_progress(step, total_steps, "📝 Generating user reports...")
    step += 1
    with open(report_dir / 'contributed_summary.md', 'w', encoding='utf-8') as f:
        f.write(f"# {labels['user_contrib_title']}\n\n")
        f.write(f"- **Total Lines of Code**: {contrib_lines}\n")
        f.write(f"- **Total Projects**: {len(contrib_projects)}\n")
        f.write(f"- **Total Commits**: {contrib_commits}\n")
        f.write(f"\n## Languages\n\n| Language | Lines of Code |\n|----------|---------------|\n")
        for lang, lines in contrib_langs.items():
            f.write(f"| {lang} | {lines} |\n")
        f.write(f"\n## Frameworks\n\n| Framework | Indicator File |\n|-----------|----------------|\n")
        for framework, indicator in contrib_frameworks.items():
            f.write(f"| {framework} | {indicator} |\n")
        f.write(signature)

    with open(report_dir / 'user_projects_summary.md', 'w', encoding='utf-8') as f:
        f.write(f"# {labels['user_projects_title']}\n\n")
        f.write(f"- **Total Lines of Code**: {user_lines}\n")
        f.write(f"- **Total Projects**: {len(user_projects)}\n")
        f.write(f"- **Total Commits**: {user_commits}\n")
        f.write(f"\n## Languages\n\n| Language | Lines of Code |\n|----------|---------------|\n")
        for lang, lines in user_langs.items():
            f.write(f"| {lang} | {lines} |\n")
        f.write(f"\n## Frameworks\n\n| Framework | Indicator File |\n|-----------|----------------|\n")
        for framework, indicator in user_frameworks.items():
            f.write(f"| {framework} | {indicator} |\n")
        f.write(signature)

    with open(report_dir / 'full_user_summary.md', 'w', encoding='utf-8') as f:
        f.write(f"# {labels['user_full_title']}\n\n")
        f.write(f"- **All Lines of Code**: {contrib_lines + user_lines}\n")
        f.write(f"- **All Commits**: {contrib_commits + user_commits}\n")
        f.write(f"\n## All Languages\n\n| Language | Lines of Code |\n|----------|---------------|\n")
        all_langs = defaultdict(int)
        for lang, lines in contrib_langs.items():
            all_langs[lang] += lines
        for lang, lines in user_langs.items():
            all_langs[lang] += lines
        for lang, lines in all_langs.items():
            f.write(f"| {lang} | {lines} |\n")
        f.write(f"\n## Timeline\n\n| Date | Action | Changes |\n|------|--------|---------|\n")
        for event in timeline:
            f.write(f"| {event['date']} | {event['action']} | {event['changes']} |\n")
        f.write(signature)

    print_progress(total_steps, total_steps, "✅ User analysis complete! Reports in: " + str(report_dir))
    print()

def show_menu(current_lang):
    """Displays the selection menu and returns the user's choice."""
    print("\n=== Q-Git Menu ===")
    print(f"1. Language Selection (Current: {current_lang})")
    print("2. Analyze Repository")
    print("3. Analyze Git User")
    print("4. Exit")
    choice = input("Select an option (1-4): ").strip()
    return choice

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    ascii_art = (
        "┌──────────────────────────────────────────┐\n"
        "│  ██████         ██████  ██ ████████      │\n"
        "│ ██    ██       ██       ██    ██         │\n"
        "│ ██    ██ █████ ██   ███ ██    ██         │\n"
        "│ ██ ▄▄ ██       ██    ██ ██    ██         │\n"
        "│  ██████         ██████  ██    ██         │\n"
        "│     ▀▀                                   │\n"
        "│  ----------- Advanced Git Analyzer       │\n"
        "│  --- developed with ♥ by @keyvanarasteh  │\n"
        "└──────────────────────────────────────────┘\n"
    )
    print(ascii_art)

    lang = "EN"
    supported_langs = ["EN", "TR", "IT", "FR", "ES", "DE"]

    while True:
        choice = show_menu(lang)

        if choice == "1":
            lang = input(f"Choose report language ({', '.join(supported_langs)}, default: EN): ").strip().upper()
            if not lang or lang not in supported_langs:
                lang = "EN"
            print(f"Selected language: {lang}")

        elif choice == "2":
            repo_url = input("Enter the GitHub repo URL: ").strip()
            analyze_repo(repo_url, lang)

        elif choice == "3":
            username = input("Enter the GitHub username: ").strip()
            analyze_git_user(username, lang)

        elif choice == "4":
            print("👋 Exiting Q-Git. Goodbye!")
            break

        else:
            print("❌ Invalid option. Please select 1, 2, 3, or 4.")
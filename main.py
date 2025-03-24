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

def get_language_labels(lang):
    """Returns labels for Markdown reports based on the selected language."""
    labels = {
        "EN": {
            "repo_info_title": "Repository Information",
            "folder_structure_title": "Folder Structure",
            "timeline_title": "Development Timeline",
            "full_report_title": "Full Repository Report",
            "metrics": {
                "total_lines": "Total Lines of Code",
                "total_commits": "Total Commits",
                "contributors": "Contributors",
                "creation_date": "Creation Date",
                "last_update": "Last Update"
            },
            "timeline_headers": ["Date", "Author", "Message", "Changes"]
        },
        "TR": {
            "repo_info_title": "Depo Bilgileri",
            "folder_structure_title": "Klasör Yapısı",
            "timeline_title": "Geliştirme Zaman Çizelgesi",
            "full_report_title": "Tam Depo Raporu",
            "metrics": {
                "total_lines": "Toplam Kod Satırı",
                "total_commits": "Toplam Commit",
                "contributors": "Katkıda Bulunanlar",
                "creation_date": "Oluşturma Tarihi",
                "last_update": "Son Güncelleme"
            },
            "timeline_headers": ["Tarih", "Yazar", "Mesaj", "Değişiklikler"]
        },
        "IT": {
            "repo_info_title": "Informazioni sul Repository",
            "folder_structure_title": "Struttura delle Cartelle",
            "timeline_title": "Cronologia di Sviluppo",
            "full_report_title": "Rapporto Completo del Repository",
            "metrics": {
                "total_lines": "Linee di Codice Totali",
                "total_commits": "Commit Totali",
                "contributors": "Contributori",
                "creation_date": "Data di Creazione",
                "last_update": "Ultimo Aggiornamento"
            },
            "timeline_headers": ["Data", "Autore", "Messaggio", "Modifiche"]
        },
        "FR": {
            "repo_info_title": "Informations sur le Dépôt",
            "folder_structure_title": "Structure des Dossiers",
            "timeline_title": "Chronologie de Développement",
            "full_report_title": "Rapport Complet du Dépôt",
            "metrics": {
                "total_lines": "Lignes de Code Totales",
                "total_commits": "Commits Totaux",
                "contributors": "Contributeurs",
                "creation_date": "Date de Création",
                "last_update": "Dernière Mise à Jour"
            },
            "timeline_headers": ["Date", "Auteur", "Message", "Changements"]
        },
        "ES": {
            "repo_info_title": "Información del Repositorio",
            "folder_structure_title": "Estructura de Carpetas",
            "timeline_title": "Línea de Tiempo de Desarrollo",
            "full_report_title": "Informe Completo del Repositorio",
            "metrics": {
                "total_lines": "Líneas de Código Totales",
                "total_commits": "Commits Totales",
                "contributors": "Contribuidores",
                "creation_date": "Fecha de Creación",
                "last_update": "Última Actualización"
            },
            "timeline_headers": ["Fecha", "Autor", "Mensaje", "Cambios"]
        },
        "DE": {
            "repo_info_title": "Repository-Informationen",
            "folder_structure_title": "Ordnerstruktur",
            "timeline_title": "Entwicklungszeitleiste",
            "full_report_title": "Vollständiger Repository-Bericht",
            "metrics": {
                "total_lines": "Gesamte Codezeilen",
                "total_commits": "Gesamte Commits",
                "contributors": "Mitwirkende",
                "creation_date": "Erstellungsdatum",
                "last_update": "Letztes Update"
            },
            "timeline_headers": ["Datum", "Autor", "Nachricht", "Änderungen"]
        }
    }
    return labels.get(lang.upper(), labels["EN"])  # Default to English

def analyze_repo(repo_url, lang="EN"):
    """Analyzes the GitHub repository and generates Markdown reports."""
    print("📋 Starting repository analysis...")
    temp_dir = tempfile.mkdtemp()
    repo_name = get_repo_name(repo_url)
    report_dir = Path('reports') / repo_name
    report_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Get language-specific labels
        labels = get_language_labels(lang)

        print("🔗 Validating repository URL...")
        if repo_url.startswith('https://github.com/'):
            clone_url = repo_url + '.git' if not repo_url.endswith('.git') else repo_url
        elif repo_url.startswith('git@github.com:'):
            clone_url = repo_url
        else:
            raise ValueError("Invalid GitHub URL. Use HTTPS (https://github.com/...) or SSH (git@github.com:...) format.")

        print("📥 Cloning repository...")
        git.Repo.clone_from(clone_url, temp_dir)
        repo = git.Repo(temp_dir)

        print("📄 Collecting tracked files...")
        tracked_files = [f for f in repo.git.ls_files().split('\n') if f]

        print("📊 Analyzing files and commits...")
        file_data = {}
        for file_path in tracked_files:
            with open(os.path.join(temp_dir, file_path), 'r', encoding='utf-8', errors='ignore') as f:
                lines = sum(1 for line in f)
            commits = set(repo.git.log('--follow', '--pretty=format:%H', file_path).split('\n'))
            file_data[file_path] = {'lines': lines, 'commits': commits}

        print("🌳 Building folder structure...")
        tree = build_tree_structure(file_data)
        aggregate_tree(tree)

        print("⏳ Fetching commit history...")
        commits = list(repo.iter_commits())
        commits.reverse()
        authors = set(commit.author.name for commit in commits)

        # Signature for all reports
        signature = (
            "\n---\n"
            f"Generated with [Q-Git](https://github.com/QLineTech/Q-Git) on {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        print("📝 Generating repo_info.md...")
        with open(report_dir / 'repo_info.md', 'w', encoding='utf-8') as f:
            f.write(f"# {labels['repo_info_title']}\n\n")
            f.write("| Metric                | Value                                      |\n")
            f.write("|-----------------------|--------------------------------------------|\n")
            f.write(f"| {labels['metrics']['total_lines']}  | {tree['lines']}                           |\n")
            f.write(f"| {labels['metrics']['total_commits']}        | {len(commits)}                            |\n")
            f.write(f"| {labels['metrics']['contributors']}         | {len(authors)}                            |\n")
            f.write(f"| {labels['metrics']['creation_date']}        | {commits[0].committed_datetime.strftime('%Y-%m-%d %H:%M:%S')} |\n")
            f.write(f"| {labels['metrics']['last_update']}          | {commits[-1].committed_datetime.strftime('%Y-%m-%d %H:%M:%S')} |\n")
            f.write(signature)

        print("📝 Generating folder_structure.md...")
        with open(report_dir / 'folder_structure.md', 'w', encoding='utf-8') as f:
            f.write(f"# {labels['folder_structure_title']}\n\n")
            f.write("```markdown\n")
            f.write("\n".join(print_tree(tree)))
            f.write("\n```\n")
            f.write(signature)

        print("📝 Generating timeline.md...")
        with open(report_dir / 'timeline.md', 'w', encoding='utf-8') as f:
            f.write(f"# {labels['timeline_title']}\n\n")
            f.write(f"| {labels['timeline_headers'][0]}                | {labels['timeline_headers'][1]}          | {labels['timeline_headers'][2]}                  | {labels['timeline_headers'][3]}         |\n")
            f.write("|---------------------|-----------------|--------------------------|-----------------|\n")
            for commit in commits:
                date = commit.committed_datetime.strftime("%Y-%m-%d %H:%M:%S")
                author = commit.author.name
                message = commit.message.strip().replace('\n', ' ')
                stats = commit.stats.total
                changes = f"+{stats['insertions']}, -{stats['deletions']}"
                f.write(f"| {date} | {author} | {message[:50]}{'...' if len(message) > 50 else ''} | {changes} |\n")
            f.write(signature)

        print("📝 Generating full_report.md...")
        with open(report_dir / 'full_report.md', 'w', encoding='utf-8') as f:
            f.write(f"# {labels['full_report_title']}\n\n")
            f.write("![Q-Git Badge](https://img.shields.io/badge/Q--Git-Analyzed-blue?style=flat-square)\n\n")
            f.write(f"## {labels['repo_info_title']}\n\n")
            with open(report_dir / 'repo_info.md', 'r', encoding='utf-8') as repo_file:
                f.write(repo_file.read().split("---")[0])  # Exclude signature
            f.write(f"\n## {labels['folder_structure_title']}\n\n")
            with open(report_dir / 'folder_structure.md', 'r', encoding='utf-8') as folder_file:
                f.write(folder_file.read().split("---")[0])  # Exclude signature
            f.write(f"\n## {labels['timeline_title']}\n\n")
            with open(report_dir / 'timeline.md', 'r', encoding='utf-8') as timeline_file:
                f.write(timeline_file.read().split("---")[0])  # Exclude signature
            f.write(signature)

        print("✅ Analysis complete! Reports generated in:", report_dir)

    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        raise
    finally:
        print("🧹 Cleaning up temporary files...")
        safe_rmtree(temp_dir)

if __name__ == "__main__":
    # Clear console on script start
    os.system('cls' if os.name == 'nt' else 'clear')

    # Draw ASCII art in a bordered rectangle with heart emoji
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

    # Language selection
    supported_langs = ["EN", "TR", "IT", "FR", "ES", "DE"]
    lang = input(f"Choose report language ({', '.join(supported_langs)}, default: EN): ").strip().upper()
    if not lang or lang not in supported_langs:
        lang = "EN"
    print(f"Selected language: {lang}")

    repo_url = input("Enter the GitHub repo URL: ").strip()
    analyze_repo(repo_url, lang)
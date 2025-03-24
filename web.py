from flask import Flask, render_template, request, redirect, url_for, flash
import webbrowser
import threading
import os
from main import analyze_repo, analyze_git_user, get_language_labels, safe_rmtree
from pathlib import Path
import sys
import time

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flash messages

# Global variables to track analysis progress
progress = {'status': 'Idle', 'message': '', 'percentage': 0}
reports_dir = Path('reports')

# Supported languages from main.py
SUPPORTED_LANGS = ["EN", "TR", "IT", "FR", "ES", "DE"]


def run_analysis_in_thread(func, *args):
    """Runs the analysis function in a separate thread and updates progress."""

    def wrapper():
        global progress
        try:
            progress['status'] = 'Running'
            func(*args)
            progress['status'] = 'Complete'
            progress['message'] = f"Analysis complete! Reports saved in: {reports_dir}"
            progress['percentage'] = 100
        except Exception as e:
            progress['status'] = 'Error'
            progress['message'] = f"Error: {str(e)}"
            progress['percentage'] = 0
            flash(f"Error during analysis: {str(e)}", "error")
        finally:
            if progress['status'] != 'Error':
                flash("Analysis completed successfully!", "success")

    # Redirect stdout/stderr to capture progress updates
    sys.stdout = ProgressWriter()
    sys.stderr = sys.stdout
    thread = threading.Thread(target=wrapper)
    thread.start()


class ProgressWriter:
    """Custom writer to capture progress updates from main.py."""

    def write(self, text):
        global progress
        if "❌ Error" in text:
            progress['status'] = 'Error'
            progress['message'] = text.strip()
        elif text.strip() and "✅" in text or "🧹" in text:
            progress['message'] = text.strip()
            progress['percentage'] = 100
        elif text.strip():
            # Extract percentage from progress bar output
            try:
                percentage = float(text.split()[-1].replace('%', ''))
                progress['percentage'] = percentage
                progress['message'] = text.split(']')[0].strip()
            except (ValueError, IndexError):
                progress['message'] = text.strip()

    def flush(self):
        pass


@app.route('/')
def index():
    return render_template('index.html', langs=SUPPORTED_LANGS)


@app.route('/analyze', methods=['POST'])
def analyze():
    analysis_type = request.form.get('analysis_type')
    lang = request.form.get('language', 'EN')
    if lang not in SUPPORTED_LANGS:
        lang = 'EN'

    global progress
    progress = {'status': 'Running', 'message': 'Starting analysis...', 'percentage': 0}

    if analysis_type == 'repo':
        repo_url = request.form.get('repo_url', '').strip()
        if not repo_url:
            flash("Repository URL cannot be empty.", "error")
            return redirect(url_for('index'))
        run_analysis_in_thread(analyze_repo, repo_url, lang)

    elif analysis_type == 'user':
        username = request.form.get('username', '').strip()
        if not username:
            flash("GitHub username cannot be empty.", "error")
            return redirect(url_for('index'))
        run_analysis_in_thread(analyze_git_user, username, lang)

    else:
        flash("Invalid analysis type.", "error")
        return redirect(url_for('index'))

    return redirect(url_for('progress_page'))


@app.route('/progress')
def progress_page():
    return render_template('progress.html', progress=progress)


@app.route('/reports')
def reports():
    if progress['status'] != 'Complete':
        flash("No reports available yet. Please complete an analysis first.", "info")
        return redirect(url_for('index'))

    repo_dirs = [d for d in reports_dir.iterdir() if d.is_dir()]
    reports_list = []
    for repo_dir in repo_dirs:
        reports = [f.name for f in repo_dir.glob('*.md')]
        reports_list.append({'name': repo_dir.name, 'files': reports})

    return render_template('reports.html', reports=reports_list)


@app.route('/report/<repo_name>/<filename>')
def view_report(repo_name, filename):
    report_path = reports_dir / repo_name / filename
    if not report_path.exists():
        flash("Report not found.", "error")
        return redirect(url_for('reports'))

    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return render_template('report_view.html', content=content, repo_name=repo_name, filename=filename)


def open_browser():
    """Opens the default browser to the Flask app URL."""
    time.sleep(1)  # Wait for server to start
    webbrowser.open('http://127.0.0.1:5000')


if __name__ == "__main__":
    # Ensure reports directory exists
    reports_dir.mkdir(exist_ok=True)

    # Start Flask app in a thread and open browser
    threading.Thread(target=open_browser).start()
    app.run(debug=False, use_reloader=False)
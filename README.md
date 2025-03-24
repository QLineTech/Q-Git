# Git Analyzer

A Python script to analyze any GitHub repository and generate detailed Markdown reports about its code, structure, and history.

**Developed by:** [@keyvanarasteh](https://github.com/keyvanarasteh)

---

## Overview // Genel Bakış

This tool takes a GitHub repository URL (via SSH), clones it, and generates four Markdown reports:
- `repo_info.md`: General statistics (lines of code, commits, contributors, etc.).
- `folder_structure.md`: Tree view of the folder structure with lines of code and commit counts.
- `timeline.md`: Chronological commit history with details of changes.
- `full_report.md`: A comprehensive report combining all the above.

**TR:** Bu araç, bir GitHub deposu URL'sini (SSH üzerinden) alır, klonlar ve dört Markdown raporu oluşturur:
- `repo_info.md`: Genel istatistikler (kod satırları, commit'ler, katkıda bulunanlar vb.).
- `folder_structure.md`: Kod satırları ve commit sayıları ile klasör yapısının ağaç görünümü.
- `timeline.md`: Değişiklik detaylarıyla kronolojik commit geçmişi.
- `full_report.md`: Yukarıdakilerin tümünü birleştiren kapsamlı bir rapor.

---

## Features // Özellikler

- **Lines of Code**: Counts total lines across all tracked files.
- **Folder Structure**: Displays a hierarchical tree with stats per file and directory.
- **Commit History**: Details every commit, including lines added/removed and timestamps.
- **Timeline**: Visualizes the development progression over time.

**TR:**
- **Kod Satırları**: Tüm izlenen dosyalardaki toplam satırları sayar.
- **Klasör Yapısı**: Her dosya ve dizin için istatistiklerle hiyerarşik bir ağaç gösterir.
- **Commit Geçmişi**: Her commit'in detaylarını, eklenen/çıkarılan satırları ve zaman damgalarını içerir.
- **Zaman Çizelgesi**: Geliştirme sürecini zaman içinde görselleştirir.

---

## Installation Guide // Kurulum Rehberi

### Prerequisites // Ön Koşullar
- **Python 3.x**: Ensure Python is installed.
- **Git**: Installed and configured with SSH authentication for GitHub.
- **GitPython**: Python library for Git operations.

**TR:**
- **Python 3.x**: Python'un kurulu olduğundan emin olun.
- **Git**: GitHub için SSH kimlik doğrulaması ile kurulu ve yapılandırılmış olmalı.
- **GitPython**: Git işlemleri için Python kütüphanesi.

### Steps // Adımlar
1. **Clone the Repository**  
   ```bash
   git clone git@github.com:keyvanarasteh/git-repo-analyzer.git
   cd git-repo-analyzer
   ```

2. **Install Dependencies**  
   ```bash
   pip install gitpython
   ```

3. **Set Up SSH Authentication**  
   Ensure your GitHub SSH key is configured:
   - Generate an SSH key if needed: `ssh-keygen -t rsa`.
   - Add the key to your GitHub account (Settings > SSH and GPG keys).
   - Test it: `ssh -T git@github.com`.

4. **Run the Script**  
   ```bash
   python analyze_repo.py
   ```
   Enter a GitHub repo URL (e.g., `git@github.com:user/repo.git`) when prompted.

**TR:**
1. **Depoyu Klonlayın**  
   ```bash
   git clone git@github.com:keyvanarasteh/git-repo-analyzer.git
   cd git-repo-analyzer
   ```

2. **Bağımlılıkları Kurun**  
   ```bash
   pip install gitpython
   ```

3. **SSH Kimlik Doğrulamasını Ayarlayın**  
   GitHub SSH anahtarınızın yapılandırıldığından emin olun:
   - Gerekirse SSH anahtarı oluşturun: `ssh-keygen -t rsa`.
   - Anahtarı GitHub hesabınıza ekleyin (Ayarlar > SSH ve GPG anahtarları).
   - Test edin: `ssh -T git@github.com`.

4. **Script'i Çalıştırın**  
   ```bash
   python analyze_repo.py
   ```
   İstendiğinde bir GitHub depo URL'si girin (örneğin, `git@github.com:user/repo.git`).

---

## Usage // Kullanım

Run the script and provide a GitHub repository URL. It will:
- Clone the repo temporarily.
- Analyze its contents and history.
- Generate four Markdown files in the current directory.

**Example:**
```bash
$ python analyze_repo.py
Enter the GitHub repo URL: git@github.com:user/repo.git
```

**TR:**
Script'i çalıştırın ve bir GitHub deposu URL'si sağlayın. Şunları yapar:
- Depoyu geçici olarak klonlar.
- İçeriğini ve geçmişini analiz eder.
- Mevcut dizinde dört Markdown dosyası oluşturur.

**Örnek:**
```bash
$ python analyze_repo.py
GitHub depo URL'sini girin: git@github.com:user/repo.git
```

---

## Output Files // Çıktı Dosyaları

- **`repo_info.md`**: General stats about the repository.
- **`folder_structure.md`**: Tree view of files and directories.
- **`timeline.md`**: Commit history in chronological order.
- **`full_report.md`**: All-in-one detailed report.

**TR:**
- **`repo_info.md`**: Depo hakkında genel istatistikler.
- **`folder_structure.md`**: Dosya ve dizinlerin ağaç görünümü.
- **`timeline.md`**: Kronolojik sırayla commit geçmişi.
- **`full_report.md`**: Hepsi bir arada detaylı rapor.

---

## Contributing // Katkıda Bulunma

Feel free to fork this repository, submit issues, or send pull requests to improve the tool!

**TR:**
Bu depoyu forklayın, sorunları bildirin veya aracı geliştirmek için pull request gönderin!

---

## License // Lisans

This project is licensed under the MIT License.

**TR:**
Bu proje MIT Lisansı altında lisanslanmıştır.

---

**Developed with ❤️ by [@keyvanarasteh](https://github.com/keyvanarasteh)**  
```

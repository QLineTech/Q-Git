# Q-Git Repository Analyzer

![Python](https://img.shields.io/badge/Python-3.6%2B-blue?style=flat-square) ![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

A powerful Python tool to analyze GitHub repositories, providing detailed insights into code metrics, folder structures, and commit histories.

**TR:** GitHub depolarını analiz eden güçlü bir Python aracı, kod metrikleri, klasör yapıları ve commit geçmişleri hakkında detaylı bilgiler sağlar.

---

## Installation // Kurulum

### Prerequisites // Ön Koşullar
- Python 3.6+ installed.
- Git on your system.

**TR:**
- Python 3.6+ kurulu.
- Sisteminizde Git.

### Steps // Adımlar
1. **Clone the repo**  
   ```bash
   git clone https://github.com/QLineTech/Q-Git.git
   cd Q-Git
   ```

2. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

**TR:**
1. **Depoyu klonlayın**  
   ```bash
   git clone https://github.com/QLineTech/Q-Git.git
   cd Q-Git
   ```

2. **Bağımlılıkları kurun**  
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage // Kullanım

Run the script and follow the prompts!  
```bash
python main.py
```

- Enter a GitHub URL (HTTPS for public, SSH for private).
- Choose a report language (EN, TR, IT, FR, ES, DE; default: EN).
- Find reports in `reports/<repo-name>/`.

**TR:**
Script'i çalıştırın ve istemleri takip edin!  
```bash
python main.py
```

- GitHub URL'sini girin (genel için HTTPS, özel için SSH).
- Rapor dilini seçin (EN, TR, IT, FR, ES, DE; varsayılan: EN).
- Raporları `reports/<repo-name>/` dizininde bulun.

---

## Features // Özellikler

- **Repository Statistics**: Lines of code, commits, contributors, dates.  
- **Folder Structure Analysis**: Tree view with file and directory metrics.  
- **Commit History Timeline**: Dates, authors, messages, and changes.  
- **Comprehensive Reporting**: All insights in a single Markdown file.  

**TR:**
- **Depo İstatistikleri**: Kod satırları, commit'ler, katkıda bulunanlar, tarihler.  
- **Klasör Yapısı Analizi**: Dosya ve dizin metrikleriyle ağaç görünümü.  
- **Commit Geçmişi Zaman Çizelgesi**: Tarihler, yazarlar, mesajlar ve değişiklikler.  
- **Kapsamlı Raporlama**: Tüm bilgiler tek bir Markdown dosyasında.  

---

## Contributing // Katkıda Bulunma

Fork the repo and submit pull requests! Open issues for major changes.  

**TR:**  
Depoyu fork edin ve pull request gönderin! Büyük değişiklikler için issue açın.  

---

## Contributors // Katkıda Bulunanlar

| Contributor          | Name           |
|----------------------|----------------|
| [@keyvanarasteh](https://github.com/keyvanarasteh) | Keyvan Arasteh |
| [@Mrrtzz](https://github.com/Mrrtzz) | Morteza Azmude |

---

## License // Lisans

MIT License. See [LICENSE](LICENSE) for details.  

**TR:**  
MIT Lisansı. Detaylar için [LICENSE](LICENSE) dosyasına bakın.  

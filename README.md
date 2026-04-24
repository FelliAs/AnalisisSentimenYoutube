# Analisis Sentimen YouTube

Proyek ini adalah pipeline lengkap untuk *scraping* (ekstraksi data) komentar dari YouTube dan melakukan analisis sentimen menggunakan *Machine Learning*.

## Fitur Utama

1. **YouTube Scraper (`youtube_scraper.py`)**
   - Mengambil komentar dari video YouTube menggunakan YouTube Data API v3.
   - Mendukung *pagination* untuk mengambil komentar dalam jumlah besar.
   - Dilengkapi dengan *exponential backoff* untuk mengatasi *rate limiting* dari API.
   - Fitur *resume* otomatis: menyimpan *progress* ke dalam file CSV secara berkala, sehingga jika proses terhenti bisa dilanjutkan tanpa mengulang dari awal.

2. **Analisis Sentimen (`sentiment_analysis.ipynb`)**
   - **Preprocessing**: Membersihkan teks (menghapus URL, tag, angka, karakter khusus), *stopword removal* (kecuali kata-kata negasi penting), dan *Lemmatization*.
   - **Labeling Otomatis**: Menggunakan VADER (`SentimentIntensityAnalyzer`) untuk melabeli komentar menjadi positif, netral, atau negatif.
   - **Feature Extraction**: Menggunakan `TfidfVectorizer` (hingga 5000 fitur, *unigram* & *bigram*).
   - **Model Klasifikasi**: Menggunakan *Logistic Regression* yang telah dioptimasi performanya untuk menangani *imbalanced dataset* (kelas yang tidak seimbang).
   - **Optimasi Khusus**: Implementasi *custom class weights* dan optimasi *threshold post-prediction* untuk mencapai performa metrik *precision*, *recall*, dan *f1-score* yang stabil pada semua kelas.

3. **Data Komentar (`comments.csv`)**
   - File dataset hasil *scraping* yang digunakan untuk melatih dan mengevaluasi model.

## Prasyarat (*Requirements*)

Pastikan Anda memiliki Python 3.8+ terinstal di sistem. Library yang dibutuhkan terdapat dalam file `requirements.txt`.

```bash
pip install -r requirements.txt
```

## Cara Penggunaan

### 1. Menjalankan Scraper
Untuk mengambil data komentar, pastikan Anda mengatur `YOUTUBE_API_KEY` (biasanya sebagai *environment variable* atau didefinisikan di dalam file script) lalu jalankan:

```bash
python youtube_scraper.py
```
Hasil akan disimpan sebagai `comments.csv`.

### 2. Menjalankan Analisis
Buka file *Jupyter Notebook* `sentiment_analysis.ipynb`:

```bash
jupyter notebook sentiment_analysis.ipynb
```
Jalankan setiap *cell* secara berurutan untuk memproses data, melatih model, mengevaluasi performa, dan melihat demonstrasi prediksi model.

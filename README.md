# Personal Portfolio Website — Adam Wahyu Syaputra

[![Deployment Status](https://img.shields.io/badge/PWS-Running-success)](https://adam-wahyu51-myportofolio.pws.cs.ui.ac.id/)
[![Course](https://img.shields.io/badge/PBP-2026%2F2027-blue)](https://pbp.cs.ui.ac.id)
[![Framework](https://img.shields.io/badge/Django-5.x-darkgreen)](https://www.djangoproject.com/)

Website portofolio pribadi berbasis web dinamis berarsitektur Model-View-Template (MVT) yang dikembangkan untuk mata kuliah **Pemrograman Berbasis Platform (CSGE602022)** di Fakultas Ilmu Komputer, Universitas Indonesia (Semester Gasal 2026/2027).

* **Nama**: Adam Wahyu Syaputra
* **NPM**: 2506534964
* **Kelas**: PBP B
* **URL Deployment PWS**: [https://adam-wahyu51-myportofolio.pws.cs.ui.ac.id/](https://adam-wahyu51-myportofolio.pws.cs.ui.ac.id/)

---

## 🛠️ Tech Stack & Architecture

* **Framework Backend**: Django (Python 3.x)
* **Database**: PostgreSQL (Production PWS) & SQLite3 (Local Development)
* **Markup & Struktur**: HTML5 Semantik (`<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<dl>`, `<footer>`)
* **Styling**: Pure CSS3 (CSS Grid, Flexbox, Custom Properties, Media Queries, Halftone Screentone)
* **Static Assets**: WhiteNoise Middleware
* **Hosting & Deployment**: Pacil Web Service (PWS) dengan containerized environment & Gunicorn

---

## ⚙️ Setup Instructions

Instruksi berikut dapat diikuti untuk menjalankan aplikasi ini secara lokal di komputer Anda:

### 1. Clone the Repository
```bash
git clone [https://github.com/adamwsyaputra/myportofolio.git](https://github.com/adamwsyaputra/myportofolio.git)
cd myportofolio
```

### 2. Setup & Activate Virtual Environment
* **Windows:**
  ```bash
  python -m venv env
  env\Scripts\activate
  ```
* **Unix (macOS / Linux):**
  ```bash
  python3 -m venv env
  source env/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Buat berkas `.env` pada direktori utama (`myportofolio/`) dan sesuaikan dengan konfigurasi lokal:
```env
PRODUCTION=False
SECRET_KEY=django-insecure-local-dev-key-change-in-production
```

### 5. Run Migrations & Start Server
```bash
python manage.py migrate
python manage.py runserver
```
Buka `http://localhost:8000` pada peramban web Anda.

---

## 📋 Weekly Progress Tracker

- [x] **Minggu 0**
  - [x] Tutorial 0: Setup Git Repository & Instalasi Django
- [x] **Minggu 1**
  - [x] Tutorial 01: Django Initial Project, HTML5, dan CSS3
  - [x] Individual Assignment 1: Web Portofolio Statis Berbasis HTML5 & CSS3
- [x] **Minggu 2**
  - [x] Tutorial 02: Implementasi Model-View-Template (MVT) pada Django
  - [x] Individual Assignment 2: Dynamic Portfolio Sections with Models & Views
- [ ] **Minggu 3**
  - [ ] Tutorial 03
  - [ ] Individual Assignment 3
- [ ] **Minggu 4**
  - [ ] Tutorial 04
  - [ ] Individual Assignment 4
- [ ] **Minggu 5**
  - [ ] Tutorial 05
  - [ ] Individual Assignment 5
- [ ] **Minggu 6**
  - [ ] Tutorial 06
  - [ ] Individual Assignment 6
- [ ] **Minggu 7**
  - [ ] Tutorial 07
  - [ ] Individual Assignment 7

---

## 📚 Weekly Documentation & AI Disclosure

Dokumentasi lengkap terkait jawaban pertanyaan reflektif, analisis keterbatasan AI, dan catatan perbaikan manual setiap penugasan dapat diakses melalui berkas berikut pada direktori [`docs/`](docs/):

* [📄 **Individual Assignment 1 Documentation**](docs/assignment-1.md)
* [📄 **Individual Assignment 2 Documentation**](docs/assignment-2.md)
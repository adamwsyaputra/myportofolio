# Personal Portfolio Website — Adam Wahyu Syaputra

[![Deployment Status](https://img.shields.io/badge/PWS-Running-success)](https://adam-wahyu51-myportofolio.pws.cs.ui.ac.id/)
[![Course](https://img.shields.io/badge/PBP-2026%2F2027-blue)](https://pbp.cs.ui.ac.id)
[![Framework](https://img.shields.io/badge/Django-5.x-darkgreen)](https://www.djangoproject.com/)

Website portofolio pribadi berbasis web statis yang dikembangkan untuk mata kuliah **Pemrograman Berbasis Platform (CSGE602022)** di Fakultas Ilmu Komputer, Universitas Indonesia (Semester Gasal 2026/2027).

* **Nama**: Adam Wahyu Syaputra
* **NPM**: 2506534964
* **Kelas**: PBP B
* **URL Deployment PWS**: [https://adam-wahyu51-myportofolio.pws.cs.ui.ac.id/](https://adam-wahyu51-myportofolio.pws.cs.ui.ac.id/)

---

## Tech Stack & Architecture

* **Framework Backend**: Django (Python 3.x)
* **Markup & Struktur**: HTML5 Semantik (`<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<dl>`, `<footer>`)
* **Styling**: Pure CSS3 (CSS Grid, Flexbox, Custom Properties, Media Queries, Halftone Screentone)
* **Static Assets**: WhiteNoise Middleware
* **Hosting & Deployment**: Pacil Web Service (PWS) dengan containerized environment & Gunicorn

---

## Weekly Progress Tracker

- [x] **Minggu 0**
  - [x] Tutorial 0: Setup Git Repository & Instalasi Django
- [x] **Minggu 1**
  - [x] Tutorial 01: Django Initial Project, HTML5, dan CSS3
  - [x] Individual Assignment 1: Web Portofolio Statis Berbasis HTML5 & CSS3

---

### Assignment 1
1. **Penggunaan Elemen Semantik HTML5**
   Dalam merancang struktur halaman portofolio ini, saya secara konsisten memanfaatkan elemen-elemen semantik HTML5 seperti `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<footer>`, serta `<dl>`, `<dt>`, dan `<dd>`. Alih-alih membuat penumpukan tag `<div>` yang tidak bermakna, elemen `<section>` membagi halaman menjadi blok tematik mandiri (`#profile`, `#skills`, `#projects`, `#experience`, `#contact`). Setiap kartu proyek dan pencapaian pada timeline dibungkus dengan `<article>` karena masing-masing merepresentasikan entitas konten independen yang utuh.

2. **Tantangan Tata Letak Responsif & Evaluasi Prioritas Elemen**
    *Tantangan Layout*: 
     Tantangan utama muncul saat mengelola sistem multi-kolom CSS Grid (pada skills* 3-kolom, *projects* 3-kolom, dan *experience* 2-kolom) serta elemen grafis absolut seperti node permata merah pada *timeline*. Pada layar sempit, kartu menjadi terlalu sempit, teks deskripsi terhimpit, dan translasi/rotasi elemen memicu horizontal scrolling yang tidak diinginkan.
    *Evaluasi Prioritas Mobile*:
     Melalui media query `@media (max-width: 600px)`, saya memprioritaskan readability dengan mengubah seluruh *grid* menjadi satu kolom (`grid-template-columns: 1fr`). Transformasi rotasi dinetralkan (`transform: none`) agar tata letak tetap simetris dan rapi. Pada *hero section*, urutan tampilan diatur ulang menggunakan `grid-template-areas` agar identitas nama dan foto tampil terlebih dahulu sebelum detail bio, sedangkan tombol kontak dialihkan menjadi full-width dengan word-break agar alamat email tidak terpotong.

3. **Batasan Web Statis & Rencana Fungsionalitas Dinamis**
    *Batasan Web Statis*: 
     Seluruh data proyek, riwayat keahlian, dan timeline saat ini masih dihardcode secara manual di dalam berkas HTML. Setiap kali ada penambahan portofolio baru, struktur markup harus disalin dan diubah secara manual, yang rentan terhadap inkonsistensi syntax. Selain itu, web statis belum mendukung interaktivitas tingkat lanjut seperti filter kategori proyek (misal: memfilter proyek berbasis Python atau Web Dev) serta formulir kontak yang hanya mengandalkan tautan `mailto:`.
   *Fungsionalitas Dinamis Berikutnya*:
     Pada iterasi berikutnya bersama Django, saya ingin menerapkan arsitektur Model-View-Template (MVT). Data proyek dan pencapaian akan disimpan di database melalui Django Models dan dirender secara dinamis menggunakan template tags.

---

#### Pengungkapan Penggunaan AI (AI Disclosure)

**Alat yang Digunakan**: Google Gemini (model penalaran teknis & arsitektur) dan ChatGPT (eksplorasi ide estetika awal & Image generation untuk menilai ide desain).

**Strategi Prompting (Constraint-Driven & Iterative Refinement)**:
  1. *Eksplorasi Konseptual (Role & Style Prompting)*: Meminta AI mengeksplorasi konsep visual berani bertema comic-book terinspirasi dari Persona 5 untuk membedakan portofolio dari template umum.
  2. *Refinement Berbasis Batasan (Constraint Injection)*: Menegakkan batasan teknis yang ketat pada AI, seperti larangan menggunakan framework CSS (Tailwind/Bootstrap) dan larangan menggunakan pustaka JavaScript pihak ketiga, karena tugas berfokus pada HTML5 dan CSS3.
  3. *Prompting Kontekstual Berbasis Rubrik*: Menginstruksikan AI untuk memeriksa struktur HTML agar mematuhi checklist wajib Tutorial 01 dan Tugas 1 (`<article>`, `<section>`, `<header>`, `<nav>`, `<main>`, `<footer>`).
  4. *Troubleshooting Diagnostik*: Menggunakan model untuk menganalisis galat spesifik secara bertahap, seperti mendiagnosis galat Docker build environment variable di PWS serta mengevaluasi breakdown layout CSS Grid pada layar ponsel.

* **Analisis Kritis Keterbatasan AI**:
  1. *Amnesia Checklist & Kurangnya Kesadaran Konteks Akademik*: Output awal AI terlalu fokus pada estetika visual sehingga menghapus elemen fungsional wajib dari penugasan. AI mengganti elemen penting seperti nomor NPM dan program studi dengan kartu abstrak generik (*"Student"*, *"Focus"*, *"Goal"*), yang jika langsung dipakai akan melanggar *checklist* minimum tugas.
  2. *Ketergantungan Berlebihan pada JavaScript*: AI cenderung menyelesaikan efek dinamis (seperti animasi *scroll reveal* dan interaktivitas hover) menggunakan script JavaScript eksternal. Padahal objektif penugasan ini secara eksplisit menguji pemahaman CSS3 lanjutan.
  3. *Magic Numbers dan Ketidakstabilan Responsif*: AI menghasilkan banyak nilai absolut dan *magic numbers* (seperti `width: 54vw; height: 580px; right: -6vw`) yang hanya bekerja di ukuran layar tertentu. Ketika diuji di perangkat bergerak, elemen visual tersebut bertabrakan, keluar dari layar, dan merusak hierarki teks.
  4. *Inkompatibilitas Konfigurasi Framework (Django)*: Kode HTML yang disarankan AI menggunakan path relatif statis biasa (`href="style.css"` dan `src="assets/..."`). Harus ada konfigurasi manual agar konfigurasi `STATICFILES_DIRS` dan WhiteNoise, yang membutuhkan struktur rute spesifik `/static/css/...` agar tidak mengalami error HTTP 404 saat deployment.

* **Intervensi & Perbaikan Manual yang Dilakukan**:
  1. *Refaktorisasi ke Pure CSS3*: Menghapus seluruh file dan logika `script.js` yang disarankan AI. Mengganti logika interaktivitas dengan pure CSS transitions (`:hover`, `:active`, `transform`, `box-shadow`) serta memanfaatkan `html { scroll-behavior: smooth; }` bawaan peramban.
  2. *Restrukturisasi Semantik & Validasi Data Pribadi*: Menulis ulang bagian *hero* dan metadata untuk menyematkan kembali identitas asli (Nama lengkap, NPM Fasilkom UI, Program Studi) menggunakan elemen semantik yang benar (`<dl>`, `<dt>`, `<dd>`) alih-alih `<div>` generik.
  3. *Rekalkulasi Layout Responsif Mobile*: Memperbaiki CSS media query `@media (max-width: 600px)` secara manual untuk mengatasi masalah *overflow* pada garis *timeline* dan *node* permata merah, serta menetralkan transformasi rotasi (`transform: none`) agar keterbacaan di layar kecil tetap terjaga
  4. *Sinkronisasi Path Django*: Mengubah seluruh tautan aset visual dan lembar gaya agar sesuai dengan standar direktori statis Django (`/static/css/style.css` dan `/static/img/...`).
  5. *Integrasi Kode Per-Section Secara Manual*: ChatGPT memberikan file html dengan design yang jauh berbeda dari template *MYPORTOFOLIO* awal. Elemen dari website HTML buatan ChatGPT di integrasi secara satu per satu section ke file Portofolio kita. Design *CSS* diubah menjadi lebih minimalistik seperti ide konsep awal.
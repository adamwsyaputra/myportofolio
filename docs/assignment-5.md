# Individual Assignment 5: Web Application Development with JavaScript and AJAX

### Tugas 5

#### 1. Debouncing dan Kenapa Penting di Fitur Search AJAX
Debouncing adalah teknik menunda eksekusi fungsi sampai user berhenti memicu event selama waktu tertentu, misalnya 300ms. Kalau user mengetik lagi sebelum waktunya habis, timer di-reset pakai `clearTimeout`. Di fitur search, tanpa debouncing setiap huruf yang diketik langsung mengirim request ke server, padahal yang kita butuhkan hanya hasil dari kata akhirnya. Dengan debouncing request yang dikirim jauh lebih sedikit, dan hasil search di halaman juga tidak ketimpa response lama yang datangnya telat.

---

#### 2. Fungsi `await` pada `fetch()`
`fetch()` tidak langsung mengembalikan datanya, tapi sebuah Promise. `await` dipakai supaya kode berhenti dulu sampai Promise itu selesai dan baru lanjut ke baris berikutnya. Hal yang sama berlaku untuk `response.json()`. Kalau tidak pakai `await`, variabelnya hanya berisi Promise yang belum selesai, jadi saat dipanggil `.json()` atau di-loop akan error, atau kartu Projects, Skills, dan Experience yang dirender malah kosong karena datanya belum ada.

---

#### 3. XSS dan Perbandingan AJAX dengan Django Template
XSS adalah serangan ketika penyerang menyisipkan script ke halaman web supaya dijalankan di browser user lain, biasanya untuk mencuri cookie atau session. Django template aman secara default karena otomatis meng-escape karakter seperti `<` dan `>`, jadi script yang diinput user hanya tampil sebagai teks biasa. Pada AJAX, server hanya mengirim JSON dan kartunya dibuat di JavaScript. Kalau string dari user dimasukkan lewat `innerHTML`, browser akan menganggapnya sebagai HTML dan script di dalamnya ikut jalan. JavaScript tidak punya escape otomatis seperti Django, jadi kita harus melakukannya sendiri, misalnya dengan `textContent`.

---

### Pengungkapan Penggunaan AI (AI Disclosure)

* **Alat yang Digunakan**: Google Gemini untuk konsultasi arsitektur dan alur AJAX, dan Antigravity untuk sebagian besar pembangunan kode seperti view JSON, modal Popover API, debouncing search, dan perapian tampilan.
* **Tautan Log Percakapan**: [Lihat Log Percakapan Lengkap](https://share.gemini.google/WlE0VkpIYTFu)
* *Catatan: Percakapan dimulai sejak Tutorial 0 dan masih dipakai sampai week 5, jadi mungkin akan lag saat di-scroll menuju week 5.*

#### Strategi Prompting
1. **Konsultasi Arsitektur (Gemini)**: Dipakai untuk merancang perpindahan dari server-side rendering Django ke client-side rendering dengan AJAX, mulai dari endpoint JSON sampai pemilihan Popover API.
2. **Pembangunan Kode Bertahap (Antigravity)**: Dipakai untuk mengubah views, form modal, template, JavaScript, dan CSS. Saya memantau hasilnya lewat test runner dan screenshot browser, lalu memberi feedback kalau ada yang perlu disesuaikan.

#### Analisis Keterbatasan AI & Perbaikan Manual
Hasil awal dari AI masih banyak yang standar dan tidak konsisten dengan tema desain yang sudah dibuat. Berikut perbaikan manual yang saya lakukan:
* **AJAX Star / Endorse / Vouch**: Tombol Star di kartu hasil render JavaScript masih memakai form submit biasa sehingga halaman ter-refresh. Saya ubah supaya di-intercept pakai `event.preventDefault()` dan dikirim lewat `fetch()`, jadi jumlah bintang langsung berubah tanpa reload.
* **Toast dan Top Layer**: Toast awalnya tertutup backdrop modal Popover. Saya pakai `popover="manual"` pada kontainer toast supaya naik ke top layer, lalu membatasi maksimal 3 toast dan menambah animasi saat bertumpuk.
* **Empty State**: Border `#empty` di halaman Projects, Skills, dan Experience tidak seragam. Saya pindahkan ke class `.comic-empty-state` dengan border 3px solid ink dan bayangan 5px 5px, dan `id="empty"` serta class `.hide` tetap dipertahankan supaya JavaScript dan test Django tidak rusak.
# Individual Assignment 2: Dynamic Portfolio Sections with Models & Views

### Tugas 2

#### 1. Alur Siklus Permintaan-Respons MVT
Ketika pengguna mengakses URL `/projects/`, permintaan HTTP GET dikirim oleh peramban dan pertama kali diterima oleh web server sebelum diteruskan ke Django. Di level proyek, `portofolio/urls.py` bertindak sebagai gerbang utama yang membaca pola path dan menggunakan fungsi `include()` untuk mendelegasikan rute tersebut ke `main/urls.py`. Selanjutnya, `urls.py` milik aplikasi mencocokkan path spesifik `projects/` dengan named route `show_projects`, lalu memanggil fungsi view yang bersangkutan di `main/views.py`.

Fungsi view bertindak sebagai penghubung logika bisnis. Di dalam view, Django mengeksekusi ORM melalui `Project.objects.all()` untuk mengambil data dari model `Project` yang ada di `main/models.py`. Model kemudian menerjemahkan query tersebut menjadi perintah SQL ke database (SQLite di lokal atau PostgreSQL di PWS) dan mengembalikan hasilnya dalam bentuk QuerySet. View membungkus QuerySet ini ke dalam dictionary context, lalu memanggil fungsi `render()` untuk memproses template `projects.html`. Django template engine menyusun HTML final dengan mengevaluasi perulangan for dan kondisi data, lalu mengirimkan kembali respons HTML lengkap berstatus HTTP 200 OK ke peramban pengguna.

---

#### 2. Keunggulan Model Dibandingkan Hardcoded Template
Menyimpan data di dalam model menerapkan prinsip separation of concerns secara nyata, di mana template murni berfungsi untuk urusan presentasi visual dan model bertanggung jawab atas data serta aturan bisnis. Dari sisi maintainability, pendekatan ini menciptakan *single source of truth*. Jika terjadi perubahan deskripsi proyek, pembaruan tautan GitHub, atau penambahan entri portofolio baru, kita cukup memperbarui data lewat database, Django admin, atau Django shell tanpa perlu menyentuh markup HTML. Hal ini menghindarkan kita dari risiko kesalahan sintaks, seperti tag penutup yang tidak sengaja terhapus atau class styling yang rusak saat mengedit template secara manual.

Selain itu, pemisahan ini sangat berpengaruh pada fleksibilitas dan skalabilitas aplikasi. Data yang terstruktur di dalam model dapat dimanipulasi dengan mudah menggunakan ORM, seperti diurutkan berdasarkan waktu, difilter berdasarkan teknologi tertentu, maupun dipaginasi tanpa merombak file template. Template juga dapat menangani kondisi data secara otomatis, misalnya menampilkan pesan fallback empty state ketika belum ada data yang tersimpan, atau di masa depan diekspos menjadi REST API jika portofolio ini ingin dikembangkan ke platform mobile.

---

#### 3. Perbedaan Fungsi `makemigrations` dan `migrate`
Perbedaan mendasar antara keduanya terletak pada tahap perancangan versus eksekusi skema database. Perintah `makemigrations` berfungsi untuk mendeteksi perubahan deklaratif yang kita buat di file `models.py` dan menerjemahkannya menjadi berkas migrasi baru di direktori `migrations/`. Perintah ini belum mengubah tabel di dalam database, melainkan hanya membuat blueprint atau rencana perubahan skema. Sebaliknya, `migrate` adalah perintah yang mengeksekusi instruksi dari berkas migrasi tersebut ke dalam database fisik dan mencatat statusnya pada tabel internal Django.

Contoh nyatanya terjadi saat pembuatan bagian Projects pada tugas ini. Pertama, kita mendefinisikan model baru `Project` di `main/models.py` dengan field seperti `title`, `description`, `tech_stack`, dan `project_url`. Kita harus menjalankan `python manage.py makemigrations` agar Django menyusun berkas migrasi baru (misalnya `0002_project.py`). Setelah berkas blueprint tersebut terbuat, kita menjalankan `python manage.py migrate` agar Django benar-benar membuat tabel fisik `main_project` di dalam database sehingga data siap disimpan dan ditampilkan.

---

### Pengungkapan Penggunaan AI (AI Disclosure)

* **Alat yang Digunakan**: Google Gemini (digunakan asisten untuk konsultasi, troubleshooting environment, dan pembuatan skenario pengujian).
* **Tautan Log Percakapan**: [Lihat Log Percakapan Lengkap](https://share.gemini.google/yxd3jnIM9J16)

#### Strategi Prompting
1. **Perancangan Arsitektur Sesuai Syarat Tugas**: Menggunakan prompt terarah untuk menyusun model `Project`, konfigurasi view, URL routing, dan template `projects.html` yang bersih.
2. **Troubleshooting Error Lintas Lingkungan**: Berkonsultasi mengenai pesan error yang muncul di terminal:
   * Mengidentifikasi kegagalan deployment PWS akibat ketidakcocokan Django versi rilis terbaru dengan server PostgreSQL PWS (versi 14), yang diselesaikan dengan mengunci versi `django~=5.0` di `requirements.txt`.
   * Menganalisis kegagalan unit test lokal pada environment Python 3.14 karena perubahan perilaku modul `copy` bawaan Python.
3. **Penyusunan Rangkaian Unit Test**: Mengarahkan model untuk menyusun skenario uji di `main/tests.py` yang mencakup verifikasi status kode HTTP, ketepatan rendering data model, dan penanganan kondisi data kosong.
4. **Eksplorasi Variasi Desain**: Meminta saran implementasi tombol navigasi vertikal menggunakan CSS `writing-mode: vertical-rl` pada seksi featured projects.

#### Keterbatasan AI
Template dan CSS awal yang disarankan untuk `projects.html` dan `experience.html` terasa terlalu polos dan tidak menyatu dengan tema brutalist comic yang sudah ada. Kartu tidak memiliki animasi hover, tidak ada background pattern titik-titik, dan tidak ada badge kategori. Saya harus beberapa kali prompt ulang untuk menyesuaikan tampilan agar sesuai yang saya inginkan dan saya koreksi manual di css untuk perbaikan minor.
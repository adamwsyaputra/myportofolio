# Individual Assignment 4: Authentication, Session and Cookies Implementation

### Tugas 4

#### Implementasi 4-Tier Role-Based Access Control (RBAC)

Pada tugas ini, sistem otorisasi dan kontrol akses diterapkan menggunakan autentikasi bawaan Django dan sistem `auth.Group` untuk membagi hak akses ke dalam 4 tingkatan peran (*role*):

1. **Anonymous Visitor (Pengunjung Tanpa Akun)**
   * **View / Read**: Memiliki akses baca penuh untuk menjelajahi seluruh halaman publik, seperti halaman beranda, Projects (`/projects/`), Skills (`/skills/`), dan Experience (`/experience/`).
   * **Star / Endorse / Vouch**: Tidak diizinkan melakukan interaksi. Jika mencoba mengakses endpoint aksi interaksi, pengunjung akan otomatis diredirect ke halaman login (`/login/`) melalui decorator `@login_required`.
   * **Update (Edit)**: Dibatasi sepenuhnya dan dialihkan ke `/login/`.
   * **Create & Delete**: Dibatasi sepenuhnya dan dialihkan ke `/login/`.
   * **Tampilan UI**: Tombol-tombol aksi pengelolaan seperti `+ Tambah...`, tombol `Edit`, dan tombol `Hapus` disembunyikan menggunakan pengecekan template `{% if user.is_authenticated %}` dan pengecekan role terkait.

2. **Regular User (Pengguna Terdaftar Non-Editor)**
   * **View / Read**: Dapat melihat seluruh data portofolio.
   * **Star / Endorse / Vouch**: Diizinkan untuk melakukan toggle interaksi pada entitas yang didukung via relasi `ManyToManyField(User)`.
   * **Update (Edit)**: Ditolak dengan status HTTP 403 Forbidden (`raise PermissionDenied`).
   * **Create & Delete**: Ditolak dengan status HTTP 403 Forbidden (`raise PermissionDenied`).
   * **Tampilan UI**: Dapat melihat dan mengklik tombol interaksi (Star, Endorse, atau Vouch), namun tombol `Edit`, `Hapus`, serta tombol pembuatan data baru tidak ditampilkan.

3. **Editor (Anggota Group `Editor`)**
   * **View / Read**: Memiliki akses baca penuh ke seluruh halaman portofolio.
   * **Star / Endorse / Vouch**: Diizinkan melakukan toggle interaksi.
   * **Update (Edit)**: Diberikan hak akses untuk memperbarui dan mengedit entitas (Projects, Skills, dan Experience) yang divalidasi melalui helper `is_editor(request.user)`.
   * **Create & Delete**: Ditolak dengan status HTTP 403 Forbidden (`raise PermissionDenied`) karena hak pembuatan dan penghapusan data bersifat destruktif dan hanya diperuntukkan bagi pemilik portofolio.
   * **Tampilan UI**: Tombol `Edit` ditampilkan pada setiap kartu entitas melalui kondisi `{% if user.is_superuser or is_editor %}`, sementara tombol `Hapus` dan tombol penambahan data tetap disembunyikan.

4. **Superuser / Owner (Pemilik Portofolio)**
   * Memiliki kendali penuh (*full privileges*) terhadap seluruh siklus data: membaca, melakukan interaksi, membuat entitas baru, memperbarui data yang ada, hingga menghapus entitas.
   * Mendapatkan hak editor secara otomatis (*implicit editor privileges*) pada helper backend:
     ```python
     def is_editor(user):
         return user.is_authenticated and (user.is_superuser or user.groups.filter(name="Editor").exists())
     ```
   * **Tampilan UI**: Seluruh tombol aksi ditampilkan secara lengkap pada ui (tombol `+ Tambah...`, tombol `Edit`, dan pemicu modal konfirmasi `Hapus`).

Selain pembagian peran di atas, dilakukan juga penyesuaian pada format serialisasi JSON di endpoint API (seperti `/api/skills/` dan `/api/experience/`) dengan menambahkan parameter `use_natural_foreign_keys=True`. Hal ini bertujuan agar data relasi many-to-many mengembalikan array username pengguna (misalnya `[["editor_test"]]`) alih-alih mengekspos primary key ID database.

---

### Pengungkapan Penggunaan AI (AI Disclosure)

* **Alat yang Digunakan**: Google Gemini (digunakan untuk perancangan roadmap teknis, pemetaan checklist fase pengerjaan, dan konsultasi arsitektur RBAC) dan Antigravity (digunakan untuk eksekusi kode, refactoring view otorisasi, penyesuaian template, serta otomasi test suite).
* **Tautan Log Percakapan**: [Lihat Log Percakapan Lengkap](https://share.gemini.google/hX4uQIbGR2o6)
* (*Note: Percakapan dimulai sejak Tutorial 0 dan masih digunakan sampai week ke 4, mungkin akan lag saat di scroll menuju ke week 4.)

#### Strategi Prompting
1. **Phase Checklisting & Scope Isolation (Gemini)**: Membatasi penggunaan Gemini strictly untuk menyusun breakdown checklist teknis dari Phase 0 hingga Phase 8 tanpa meminta penulisan kode dalam jumlah besar. Pembagian fase yang modular ini menjaga alur pengerjaan tetap terarah, mencegah penurunan context drift, dan memastikan setiap dependensi otorisasi terpetakan sebelum implementasi dimulai.
2. **Codebase Execution & Test Automation (Antigravity)**: Menggunakan Antigravity secara terfokus untuk mengeksekusi perubahan kode berdasarkan checklist fase yang telah disusun. Eksekusi mencakup refactoring view otorisasi menggunakan decorator dan helper `is_editor`, pembersihan secret code, penyesuaian kondisional template Django, hingga penyusunan unit test menyeluruh di `main/tests.py`.

#### Analisis Keterbatasan AI & Perbaikan Manual
Pada pengerjaan Assignment 4, AI menyarankan untuk menyeragamkan interaksi Star secara generik ke seluruh entitas data, mengabaikan hierarki peran Editor pada entitas proyek, serta menghasilkan markup yang merusak tata letak tema antarmuka yang sudah ada. Selain itu, generator test suite sempat melewatkan dependensi modul yang menyebabkan kegagalan saat pengujian otomatis dijalankan.

Menanggapi keterbatasan tersebut, berikut perbaikan manual dan penyesuaian independen yang saya lakukan:
* **Desain Interaksi & UX Domain**: Menolak generalisasi fitur bintang untuk semua model. Saya membedakan interaksi tiap entitas secara kontekstual dengan tetap memanfaatkan fondasi `ManyToManyField(User)`: sistem **Star** untuk Proyek, sistem **Endorsement** bergaya LinkedIn untuk Keahlian, dan sistem **Vouch** (rekomendasi profesional) untuk Pengalaman.
* **Otorisasi & Matriks Hak Akses (RBAC)**: Mengoreksi logika otorisasi pada view `update_project` dan template `projects.html` secara mandiri agar pengguna dengan peran `Editor` dapat melakukan pembaruan data proyek, tidak terbatas hanya pada superuser.
* **Refactoring CSS & Konsistensi UI**: Menata ulang styling tombol interaksi dan kontainer aksi kartu pada `style.css` agar tetap selaras dengan estetika Neo-Brutalisme komik dan tidak bertabrakan dengan modal popover native saat dibuka di layar sempit.
* **Audit & Otomasi Pengujian**: Menambahkan import model `Group` yang terlewat pada skrip pengujian serta menyelaraskan assertion status kode, sehingga seluruh 67 unit test dan 5 skenario Selenium E2E dapat berjalan 100% pass.
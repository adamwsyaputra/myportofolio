# Individual Assignment 6: Django REST Framework Implementation

### Tugas 6

#### 1. REST, Kenapa JSON Saja Belum Cukup, dan Perbedaan `PUT` dengan `PATCH`
REST adalah gaya arsitektur API yang memodelkan data sebagai resource dengan URL yang konsisten seperti `/api/v1/skills/` atau `/api/v1/experience/<id>/`, memakai HTTP method sesuai fungsinya seperti `GET`, `POST`, `PUT`, `PATCH`, dan `DELETE`, bersifat stateless, serta mengembalikan HTTP status code yang tepat seperti `200`, `201`, `204`, `400`, atau `403`. Mengembalikan JSON saja belum cukup untuk disebut RESTful karena kalau URL masih memakai nama seperti `/create_skill_ajax/` atau semua operasi tulis dipaksa lewat `POST`, maka kontrak API menjadi tidak standar. Untuk mengubah data, `PUT` dipakai untuk mengganti seluruh resource sehingga semua field wajib harus ikut dikirim, misalnya saat menyimpan ulang seluruh form edit dari awal. Sementara itu, `PATCH` dipakai untuk mengubah sebagian field saja tanpa harus mengirim field lain yang tidak berubah, misalnya saat user hanya mengubah nilai `proficiency_percent` pada skill atau status `is_ongoing` pada experience lewat modal edit.

---

#### 2. Peran Serializer pada Django REST Framework Dibandingkan `JsonResponse` Manual
Serializer di Django REST Framework bertugas mengubah object model Django menjadi tipe data Python yang siap dijadikan JSON saat mengirim response, sekaligus membaca dan memvalidasi data JSON yang masuk dari request sebelum disimpan ke database. Dibandingkan merakit dictionary secara manual pakai `JsonResponse` seperti di Tutorial 05, serializer jauh lebih rapi karena kita tidak perlu menulis ulang mapping field satu per satu di dalam view. Selain itu, aturan validasi seperti `strip_tags`, pengecekan string kosong, validasi URL, dan pembatasan field read-only seperti `star_count` atau `is_vouched` langsung terpusat di satu class `ModelSerializer` yang dipakai bersama untuk operasi `GET`, `POST`, `PUT`, dan `PATCH`.

---

#### 3. Perbedaan Autentikasi dan Otorisasi serta Pentingnya Permission Class di Server
Autentikasi adalah proses mengenali siapa user yang sedang mengirim request, misalnya lewat `SessionAuthentication` yang mengecek session dari user yang sudah login. Otorisasi adalah proses menentukan apakah user tersebut punya hak akses untuk melakukan aksi tertentu, misalnya lewat `IsPortfolioOwnerOrEditorOrReadOnly` yang mengizinkan semua orang membaca data, mengizinkan member grup `Editor` melakukan `PUT` dan `PATCH`, serta membatasi `POST` dan `DELETE` hanya untuk superuser. Hak akses wajib diperiksa dengan permission class di server karena menyembunyikan tombol di template HTML hanya memengaruhi tampilan di browser. User biasa atau pengunjung tetap bisa mengirim request `DELETE` atau `PATCH` langsung ke `/api/v1/skills/<id>/` lewat DevTools, `fetch`, atau `curl`, sehingga tanpa pemeriksaan di server data tetap bisa diubah atau dihapus secara tidak sah.

---

#### 4. Alasan Butuh CSRF Token pada `SessionAuthentication` dan Keterbatasan `force_authenticate`
Saat API memakai `SessionAuthentication`, browser otomatis menyertakan cookie `sessionid` pada setiap request ke domain yang sama, termasuk jika request itu dipicu diam-diam dari situs lain yang dibuka user. Karena itu, setiap request yang mengubah data seperti `POST`, `PUT`, `PATCH`, dan `DELETE` tetap wajib menyertakan header `X-CSRFToken` supaya server yakin bahwa request tersebut benar-benar berasal dari halaman aplikasi kita sendiri. Pada pengujian dengan `APITestCase`, `force_authenticate` hanya menempelkan user langsung ke request untuk memudahkan pengetesan permission dan melewati proses session login maupun pemeriksaan CSRF. Untuk membuktikan proteksi CSRF benar-benar berjalan, kita harus memakai `APIClient` dengan opsi `enforce_csrf_checks=True` dan login lewat method `login` agar request tanpa token terbukti ditolak dengan status `403`.

---

### Pengungkapan Penggunaan AI

* **Alat yang Digunakan**: Pada tugas ini saya sudah tidak memakai Google Gemini, dan hanya menggunakan Antigravity untuk membantu sebagian besar pembuatan kode seperti serializer, permission class, API views, integrasi fetch di template, modal edit, dan kerangka test.
* **Tautan Log Percakapan**: [Lihat Log Percakapan Lengkap](https://share.gemini.google/WlE0VkpIYTFu)
* *Catatan: Tautan di atas adalah log percakapan sampai week 5 karena di week 6 pengerjaan langsung dilakukan di Antigravity.*

#### Strategi Prompting
1. **Perencanaan Integrasi**: Meminta Antigravity membaca spesifikasi yang diberikan dan memastikan kompatibel mulai dari serializer, permission 4-tier RBAC, endpoint API untuk Skills dan Experience, sampai integrasi frontend dengan codebase dan bagian mana yang harus di adjust.
2. **Eksekusi Bertahap**: Mengerjakan fitur per bagian mulai dari backend DRF, komponen modal edit, update script AJAX di template, lalu menjalankan test suite untuk memastikan tidak ada fitur lama yang rusak.

#### Analisis Keterbatasan AI & Perbaikan Manual
* **Pemisahan Modal Tambah dan Edit**: Saat menambahkan fitur edit lewat API di halaman `skills.html` dan `experience.html`, modal tambah tetap harus dibatasi khusus untuk superuser supaya unit test lama dari tugas sebelumnya tidak gagal, sehingga saya memisahkan modal edit ke komponen sendiri yang dirender untuk superuser dan editor.
* **Penyesuaian Kasus Uji Sanitasi HTML**: Pada `ExperienceAPITest`, test validasi dengan input `<script>xss</script>` awalnya gagal mengembalikan status `400` karena `strip_tags` hanya menghapus tag HTML dan menyisakan teks di dalamnya. Saya sesuaikan kasus ujinya menjadi tag tanpa teks isi seperti `<img src="x">` untuk menguji penolakan input kosong setelah sanitasi, serta test terpisah untuk memastikan tag HTML benar-benar dibersihkan.
* **Kompatibilitas Endpoint Lama**: Supaya seluruh unit test lama di `main/tests.py` tetap berjalan hijau bersamaan dengan test baru di `main/tests_api.py`, view JSON lama tetap dipertahankan sementara halaman frontend diarahkan penuh ke endpoint `/api/v1/`.

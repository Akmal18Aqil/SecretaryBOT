# The Secretary Swarm: Buku Panduan Operator

Selamat! Asisten Pribadi berbasis AI untuk Pesantren Anda sudah **hidup, aman, dan punya ingatan**.
Berikut adalah panduan lengkap cara mengoperasikannya.

## 1. Arsitektur Sistem Baru
Sistem Anda sekarang terdiri dari 3 pilar:
1.  **Vercel (Otak)**: Menjalankan kode Python & AI (Gemini).
2.  **Supabase (Ingatan)**: Database untuk menyimpan daftar anggota & riwayat surat.
3.  **Telegram (Wajah)**: Tempat Anda berinteraksi.

## 2. Fitur & Cara Pakai

### A. Mode Kerja (Buat Surat)
Perintahkan seperti biasa.
*   👨‍💻 User: *"Buatkan surat peminjaman proyektor untuk workshop besok"*
*   🤖 Bot: *"Siap! Surat peminjaman proyektor selesai."*

### B. Mode Chat (Basa-basi)
Ajak ngobrol santai layaknya asisten manusia.
*   👨‍💻 User: *"Assalamualaikum, lagi sibuk gak?"*
*   🤖 Bot: *"Waalaikumsalam! Santai kok. Mau dibuatin kopi atau surat?"*

### C. Mode Rekap (Laporan) [BARU ✨]
Tanya sejarah surat yang pernah dibuat.
*   👨‍💻 User: *"Rekap surat bulan ini dong"*
*   🤖 Bot: *"Ini laporannya: 1. Undangan Rapat (30 Jan), 2. Peminjaman Kamera (29 Jan)..."*

### D. Mode Tanya Jawab Kantor (Otak Cerdas) [BARU 🧠]
Bot bisa menjawab pertanyaan seputar SOP, Proker, dan Info Kantor.
*   👨‍💻 User: *"Bagaimana SOP izin pulang malam?"*
*   🤖 Bot: *"Menurut SOP, santri harus lapor H-1 dan membawa surat tugas..."* (Jawaban diambil dari database).

## 3. Manajemen Keamanan (Auth)

Bot ini **TERKUNCI**. Hanya orang yang terdaftar di database Supabase yang bisa memerintahnya.

**Cara Menambah Anggota Baru:**
1.  Minta teman Anda chat ke bot **@userinfobot** di Telegram untuk dapat ID-nya (contoh: `123456789`).
2.  Buka **Supabase dashboard**.
3.  Masuk ke **Table Editor** -> pilih tabel **`users`**.
4.  Klik **Insert Row**, lalu isi:
    *   `telegram_id`: 123456789
    *   `nama`: "Budi (Sie Acara)"
    *   `role`: "member"
5.  Klik **Save**. Teman Anda langsung bisa pakai bot detik itu juga.

## 4. Manajemen Pengetahuan (Untuk Admin)
Agar bot pintar, Anda harus "mengajarinya" terlebih dahulu.

**Cara Upload SOP/Info ke Otak Bot:**
1.  Buka terminal laptop (tempat kodingan bot).
2.  Jalankan perintah:
    ```bash
    python scripts/admin_add_knowledge.py
    ```
3.  Ketik info yang mau diajarkan. Contoh:
    *"SOP Peminjaman Kamera: Peminjam wajib menyerahkan KTM dan mengisi form di pos satpam. Maksimal pinjam 2 hari."*
4.  Tekan Enter. Bot akan menyimpan ilmu baru ini selamanya.

## 5. Troubleshooting
Jika bot error:
1.  **"Unauthorized"**: Cek apakah ID Telegram Anda sudah ada di tabel `users`.
2.  **"500 Error"**: Cek apakah `SUPABASE_URL` dan `KEY` di Vercel sudah benar.
3.  **"Diam saja"**: Cek Webhook URL atau restart Vercel (Redeploy).

## 5. Cara Update Bot
Jika ingin mengubah kode/template:
1.  Edit kode di laptop.
2.  Push ke GitHub: `git push`.
3.  Tunggu 1 menit, Vercel akan otomatis update.

---
*Dibuat dengan 💖 oleh Tim IT Multimedia*

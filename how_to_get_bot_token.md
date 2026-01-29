# Cara Mendapatkan Token Telegram Bot 🤖

Agar "The Secretary Swarm" bisa online di Telegram, Anda butuh "Bot Token". Gratis selamanya.

## Langkah-langkah:

1.  Buka aplikasi **Telegram** (HP/Desktop).
2.  Cari akun bernama **@BotFather** (pastikan yang ada centang biru).
3.  Klik **Start** atau ketik `/start`.
4.  Ketik perintah: `/newbot`.
5.  **Beri Nama Bot**: Misal `Sekretaris Pesantren Bot` (ini nama yang muncul di chat).
6.  **Beri Username Bot**: Harus berakhiran 'bot'. Misal `sekretaris_swarm_bot`.
7.  **SELESAI!** BotFather akan membalas dengan pesan panjang yang berisi token:
    `Use this token to access the HTTP API: 123456789:ABCdefGhIVkLmNoPqrStuVWxyz`

## Cara Pasang:
1.  Copy token tersebut.
2.  Buka file `.env` di folder project.
3.  Paste di bagian: `TELEGRAM_BOT_TOKEN=paste_disini`.
4.  Simpan file.
5.  Jalankan `run_demo.bat`.

Sekarang bot Anda sudah hidup! Coba chat: "Halo" ke bot tersebut.

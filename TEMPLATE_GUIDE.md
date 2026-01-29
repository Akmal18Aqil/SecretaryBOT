# Panduan Variabel Template (The Secretary Swarm)

Gunakan variabel-variabel di bawah ini di dalam file Word (`.docx`) Anda.  
Format penulisan di Word: `{{ nama_variabel }}`

---

## 1. Surat Undangan Internal
**Nama File:** `tpl_undangan_internal.docx`

| Variabel | Penjelasan | Contoh Output AI |
| :--- | :--- | :--- |
| `{{ nomor_surat }}` | Nomor surat otomatis | 001/MM/I/2026 |
| `{{ penerima }}` | Nama yang diundang | Ust. Abdurrahman |
| `{{ acara }}` | Nama/Agenda acara | Rapat Evaluasi Bulanan |
| `{{ hari_tanggal }}` | Hari dan Tanggal lengkap | Jumat, 30 Januari 2026 |
| `{{ waktu }}` | Jam pelaksanaan | 20.00 WIB - Selesai |
| `{{ tempat }}` | Lokasi acara | Studio Multimedia |

---

## 2. Surat Peminjaman Barang
**Nama File:** `tpl_peminjaman_barang.docx`

| Variabel | Penjelasan | Contoh Output AI |
| :--- | :--- | :--- |
| `{{ nomor_surat }}` | Nomor surat otomatis | 002/SARPRAS/I/2026 |
| `{{ pemohon }}` | Nama orang yang meminjam | Akmal (Div. Multimedia) |
| `{{ keperluan }}` | Alasan peminjaman | Dokumentasi Haul |
| `{{ nama_barang }}` | Barang yang dipinjam | Kamera Sony A7III & Tripod |
| `{{ waktu_pinjam }}` | Durasi/Tanggal pemakaian | Minggu, 2 Feb 2026 (07.00 - Selesai) |

---

## 3. Surat Tugas (Opsional)
**Nama File:** `tpl_surat_tugas.docx`
*(Jika Anda ingin mengaktifkan fitur ini)*

| Variabel | Penjelasan | Contoh Output AI |
| :--- | :--- | :--- |
| `{{ nomor_surat }}` | Nomor surat otomatis | 003/ST/MM/I/2026 |
| `{{ tugas }}` | Deskripsi tugas | Meliput Kunjungan Tamu |
| `{{ penerima_tugas }}` | Nama-nama petugas | Budi, Siti, dan Reza |
| `{{ hari_tanggal }}` | Waktu pelaksanaan | Senin, 3 Feb 2026 |
| `{{ tempat }}` | Lokasi tugas | Aula Utama |
| `{{ penandatangan }}` | Yang memberi tugas | Ketua Divisi |

---

### Tips Debugging
Jika output di Word masih muncul kurung kurawal `{{ ... }}` atau kosong:
1.  Cek layar terminal hitam (Output Debug).
2.  Lihat bagian `[DEBUG AGENT 1] JSON Generated`.
3.  Pastikan ejaan variabel di Word **SAMA PERSIS** dengan key JSON di terminal.
    *   Benar: `{{ hari_tanggal }}`
    *   Salah: `{{ Hari_Tanggal }}` (Huruf besar berpengaruh!)

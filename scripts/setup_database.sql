-- 1. Enable UUID Extension (Agar bisa generate ID unik)
create extension if not exists "uuid-ossp";

-- 2. Create Table USERS (Daftar Pengurus yang Boleh Pakai Bot)
create table users (
  telegram_id bigint primary key, -- ID unik dari Telegram (Bukan Nomor HP)
  nama text not null,             -- Nama Pengurus (ex: "Akmal")
  role text default 'member',     -- 'admin' / 'member'
  is_active boolean default true, -- Kalau false, dia diblokir
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 3. Create Table SURAT_HISTORY (Arsip Surat Digital)
create table surat_history (
  id uuid default uuid_generate_v4() primary key,
  nomor_surat text,               -- "001/INV/MM/I/2026"
  jenis_surat text not null,      -- "undangan_internal"
  detail_json jsonb,              -- Data lengkap surat (isi, penerima, dll)
  dibuat_oleh bigint references users(telegram_id), -- Siapa yang minta?
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 4. Set RLS (Row Level Security) - Opsional dulu biar mudah
alter table users enable row level security;
alter table surat_history enable row level security;

-- Policy: Allow Anon Key to Read/Insert (Karena Bot connect pakai Anon Key di Vercel)
create policy "Enable access for all users" on users for all using (true);
create policy "Enable access for all users" on surat_history for all using (true);

-- 5. SEED DATA (Contoh Data Awal - Ganti ID dengan ID Telegram Anda!)
-- Cara cari ID: Chat ke @userinfobot di Telegram
insert into users (telegram_id, nama, role) values 
(123456789, 'Admin Multimedia', 'admin');

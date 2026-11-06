# Research Kitchen dan Agent Observatory Bridge

Alur satu perintah yang tersedia adalah `jorhas-full`. Fungsi Python berjalan
jika kontrak masukannya terpenuhi dan mencatat `WORKFLOW_PLAN.json`. Tahap tanpa
input tetap `NOT_RUN`. ORIGO merupakan draf, bukan telaah literatur lengkap atau
penelitian otonom oleh model bahasa.

```bash
python -m epistarium jorhas-full --idea "Topik riset sintetis" --out private/run-001 --lang id
python -m epistarium observatory --idea "Topik riset sintetis" --mode full --open
```

Setiap run Observatory memiliki ID yang menghubungkan manifest Python, ledger
event, rencana, dan laporan eksternal. Observatory dimulai dalam bahasa Inggris
dan tema gelap. Pengguna dapat mengganti keduanya. Checkpoint Python berlabel
`runtime_observed`; laporan host berlabel `agent_reported` dan `SELF_REPORTED`.
Laporan host belum menjadi bukti independen bahwa pekerjaan dilakukan atau
bahwa klaim didukung. Hash hanya membuktikan kesesuaian berkas lokal dengan
digest yang diterima pada saat event diproses.

## Mencatat checkpoint agen

Adapter tersedia bagi host yang dapat memanggil perintah shell. Adapter belum
memantau OpenCode, Antigravity, atau host lain secara otomatis. Agen harus
mengirim event ketika aktivitas yang dilaporkan berlangsung. Integrasi native
dan cakupan pemantauan masing-masing host masih memerlukan pengujian tersendiri.

Operator dapat melihat ID pada dashboard dan secara eksplisit memberikan akses
baca ke berkas `bridge.token` milik run tersebut. Token ini rahasia dan hanya
berlaku untuk satu run. Jangan menyalin isinya ke naskah, log, Git, atau chat.
Ganti placeholder di bawah dengan path lokal yang sebenarnya:

```bash
python -m epistarium.observatory.agent_adapter \
  --server http://127.0.0.1:4782 --run-id RUN_ID \
  --token-file PRIVATE_ROOT/runs/RUN_ID/bridge.token \
  --spool PRIVATE_SPOOL report --persona Liora --actor opencode \
  --step-id liora-1 --parent-step-id jorhas --operation start --status RUNNING
```

Untuk melaporkan `SUCCESS`, gunakan `--operation finish --status SUCCESS`,
sertakan `--artifact-root PRIVATE_ROOT/outputs/RUN_ID` dan
`--artifact RELATIVE_PATH`. Berkas harus sudah ada dalam root keluaran;
symlink, traversal, path di luar root, dan hash yang salah ditolak. Gunakan
status operasional yang sesuai untuk kegagalan atau hasil parsial. Jangan
melaporkan persetujuan, verifikasi sumber, atau pekerjaan yang tidak dilakukan.
Opsi `--event-id` menjaga pengiriman ulang tetap idempoten.

Jika server sementara tidak dapat dihubungi, adapter menyimpan event dalam
spool privat dan mengembalikan exit 3. Kirim ulang dengan argumen umum yang sama
diikuti `replay`. Token dibaca saat pengiriman dan tidak disimpan di spool.
Permintaan 4xx yang ditolak tidak dikirim ulang secara diam-diam. Simpan semua
run, spool, dan token di luar checkout Git.

## Persetujuan dan batasnya

Saat server dimulai melalui terminal interaktif, tentukan kata sandi peninjauan
privat minimal 12 karakter. Masukkan kata sandi itu pada dashboard untuk setiap
keputusan. Jika server dijalankan tanpa terminal interaktif atau kata sandi
dikosongkan, persetujuan dinonaktifkan sampai server dimulai ulang dengan kata
sandi. Kata sandi tersimpan di memori server, tidak diberikan ke bridge agen,
dan tidak dicatat dalam log event. Token bridge tidak dapat menyetujui keputusan.
Sesi lokal dan kata sandi belum membuktikan identitas maupun kehadiran manusia;
proses berbahaya dengan kendali penuh atas akun sistem operasi yang sama berada
di luar batas perlindungan ini.

Persetujuan akhir menyimpan hash manifest dan daftar hash artefak. Periksa isi
dan bandingkan hash kembali sebelum membagikan paket karena perubahan berkas
setelah persetujuan tidak otomatis dicegah. Persetujuan tidak mengesahkan bukti
atau memberi izin publikasi. Server hanya membuka loopback; jangan gunakan
tunnel publik atau reverse proxy.
Gunakan satu proses server Observatory untuk setiap root privat. Dua server
yang memakai root yang sama secara bersamaan belum didukung.

```bash
python -m epistarium.observatory.verify_approval --root PRIVATE_ROOT --run-id RUN_ID
```

Perintah tersebut memeriksa berkas yang berubah, hilang, atau bertambah. Hasilnya
tidak menilai mutu penelitian atau membuktikan identitas peninjau.

Opsi `--allow-partial` hanya mengubah exit code `jorhas-pathfind` dan
`jorhas-full` ketika hasil `PARTIAL`. Status manifest tetap sama; hasil
`BLOCKED`, `FAILED`, atau tidak lengkap tetap menghasilkan exit nonzero.

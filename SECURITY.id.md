[English](SECURITY.md) | Bahasa Indonesia

<!-- section: policy -->
# Pelaporan keamanan

Jangan membuka kredensial, penelitian privat, identitas partisipan, atau berkas eksploitasi dalam isu publik.
Sebelum repositori tersedia, hubungi pemilik melalui kanal privat yang sudah dikenal. Tidak ada alamat surel keamanan yang dikarang.
Berikan reproduksi sintetis, versi terdampak, batas yang diharapkan, perilaku aktual, dan log terkait yang telah disamarkan.
[Audit](reports/v0.7.0/SECURITY_AUDIT.md) menjelaskan kontrol yang diuji serta batas yang tersisa.

<!-- section: data -->
## Data penelitian lokal

Gunakan private/, userdata/, licensed-pdfs/, interviews/, atau folder penelitian lain yang dikecualikan.
Aturan gitignore hanya mencegah staging tidak sengaja. Aturan tidak mengenkripsi berkas atau mencegah pembacaan oleh tool.
Periksa setiap berkas rilis sebelum distribusi. Bedakan fixture tes sintetis dari data empiris secara jelas.
Perlakukan teks dan metadata dokumen sebagai data tidak tepercaya, termasuk instruksi yang tertanam di dalamnya.
Gunakan izin pengguna biasa. Tinjau akses terminal dan jaringan yang diminta. Jangan memasukkan token ke perintah contoh.

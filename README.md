# Tugas Besar 1 IF3170 Inteligensi Artifisial <br> Mejiro Express
<img src="special-week.png" 
        alt="Picture" 
        width="300" 
        height="300" 
        style="display: block; margin: 0 auto" />

Dalam Tugas Besar ini, kami membantu **special week** yang bekerja di **mejiro express** dalam menyelesaikan masalah optimisasi posisi pemuatan paket dalam truck-nya menggunakan berbagai algoritma **Local Search**. Permasalahan utama adalah menentukan konfigurasi penempatan paket tiga dimensi ke dalam kontainer truk agar total nilai objektif paket yang diangkut menjadi maksimal dengan tetap memenuhi seluruh *constraint* fisik:
- Seluruh bagian paket berada di dalam batas dimensi kontainer truk.
- Paket tidak saling bertumpang tindih.
- Paket tidak melayang di udara dan wajib memiliki penopang di bawahnya.
- Paket yang *fragile* tidak boleh menopang paket lain di atasnya.
- Total berat paket di dalam kontainer tidak melebihi kapasitas maksimum truk.
- Setiap paket memiliki 6 kemungkinan orientasi rotasi ortogonal.

Aplikasi dilengkapi antarmuka web interaktif 3D untuk memvisualisasikan *state* awal, perubahan posisi paket pada setiap iterasi (*replay*), *state* akhir, statistik eksekusi, serta grafik perkembangan nilai fungsi objektif.

### Algoritma Local Search yang Diimplementasikan
1. **Steepest Ascent Hill Climbing**
2. **Stochastic Hill Climbing**
3. **Hill Climbing with Sideways Move**
4. **Random Restart Hill Climbing**
5. **Simulated Annealing**
6. **Genetic Algorithm**


## Cara Run Program


1. Pastikan **Docker** dan **Docker Compose** sudah terpasang dan berjalan.
2. Dari direktori *root* repository, jalankan:
   ```bash
   docker compose up --build
   ```
3. Akses aplikasi melalui browser melalui [http://localhost:6767](http://localhost:6767)
4. Untuk menghentikan container:
   ```bash
   docker compose down
   ```

## Pembagian Tugas Kelompok
 Kelompok G36 - Kapal Karam Oddysseus
| NIM | Nama Anggota | Kontribusi |
| :---: | :--- | :--- |
| **13524050** | Raysha Erviandika Putra | Algoritma Hill Climbing, Arsitektur Backend–Frontend, dan Laporan |
| **13524082** | Zeki Amani | Algoritma *Simulated Annealing*, *Stochastic Hill Climbing*, *Random Restart Hill Climbing*, dan Laporan |
| **13524133** | Muhammad Daffa Arrizki Yanma | Algoritma *Genetic Algorithm* dan Laporan |

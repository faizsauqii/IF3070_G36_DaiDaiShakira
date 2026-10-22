# IF3070_G36_DaiDaiShakira

Tugas Besar 1 IF3070 Dasar Inteligensi Artifisial: Pencarian Solusi Penataan Kendaraaan pada Kapal Kargo dengan Local Search.

## Deskripsi

Program ini mencari susunan kendaraan pada geladak kapal (kendaraan mana yang dimuat, beserta posisi dan orientasinya) agar total ShippingFee sebesar mungkin, dengan batasan:
- kendaraan tidak boleh saling tumpang tindih,
- kendaraan harus berada di dalam geladak,
- total berat kendaraan tidak boleh melebihi MaxCapacity kapal.

Algoritma yang diimplementasikan:
- Steepest Ascent Hill-Climbing
- Hill-Climbing with Sideways Move
- Stochastic Hill-Climbing
- Random Restart Hill-Climbing
- Simulated Annealing
- Genetic Algorithm

## Struktur Folder

```
data/              data uji (kecil.json, sedang.json)
output/            hasil eksperimen (JSON dan gambar) per algoritma
src/
  algorithms/      hc.py, sa.py, ga.py
  models.py        representasi kendaraan, kapal, dan state
  loader.py        membaca file data JSON
  constraints.py   pengecekan batasan
  objective.py     objective function
  neighbors.py     pembangkitan neighbor
  initial.py       pembangkitan initial state acak
  visual.py        visualisasi state dan plot objective
  main.py          program utama
```

## Setup

Membutuhkan Python 3.10 atau lebih baru.

```
git clone https://github.com/faizsauqii/IF3070_G36_DaiDaiShakira.git
cd IF3070_G36_DaiDaiShakira
python3 -m venv .venv
source .venv/bin/activate (MacOS)
.venv\Scripts\activate (Windows)
pip install -r requirements.txt
```

## Cara Menjalankan

### Menu interaktif

```
python3 -m src.main
```

Pilih algoritma dan file data dengan mengetik nomornya, lalu masukkan jumlah run (tekan Enter untuk 1 run). Program akan menampilkan ringkasan tiap run, run terbaik, dan daftar kendaraan yang dimuat beserta posisinya. Ketik `0` di menu utama untuk keluar.

### Lewat argumen

```
python3 -m src.main --algorithm hc --data data/sedang.json --seeds 1 2 3
```

Pilihan `--algorithm`: `hc`, `hc_sideways`, `hc_stochastic`, `hc_random_restart`, `sa`, `ga`.

### Hasil

Setiap run disimpan di `output/<algoritma>/`:
- `runK_seedS.json`: state awal, state akhir, total ShippingFee, nilai objective, durasi, banyak iterasi, dan riwayat objective
- `runK_seedS_awal.png` dan `runK_seedS_akhir.png`: visualisasi state awal dan akhir
- `runK_seedS_objective.png`: plot nilai objective terhadap iterasi

## Format Data

Contoh format file data ada di `data/template.json`. Salin file tersebut, ubah isinya, lalu simpan di folder `data/` agar otomatis muncul di menu.

- `ships`: daftar kapal, berisi `Dimensions` (lebar `w` dan panjang `l` geladak dalam satuan grid) dan `MaxCapacity`.
- `vehicles`: daftar kendaraan, berisi `id`, `Dimensions`, `ShippingFee`, `Weight`, dan `ETA`.


## Pembagian Tugas

| NIM | Nama | Tugas |
|---|---|---|
| 18224050 | Syafaq Jiwa Raharjo | Genetic Algorithm, eksperimen dan analisis GA |
| 18224086 | Faiz Muhammad Sauqi | Fondasi program, Hill-Climbing (semua varian), program utama, README, eksperimen dan analisis HC |
| 18224096 | Azfar Arafi Shofyan | Simulated Annealing, visualisasi, eksperimen dan analisis SA |
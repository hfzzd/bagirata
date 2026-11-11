"""Unit test ekspor CSV BagiRata: tagihan, pembayaran, laporan.

Header dan isi diperiksa lewat `csv.reader` supaya format (pemisah,
kutip, baris baru) ikut terverifikasi, bukan hanya substring.
"""

import csv
import io
import unittest

from bagirata import export as export_mod
from bagirata import model


def data_contoh():
    """3 anggota, 2 tagihan + 1 pembayaran di bulan 2026-11.

    Listrik 510rb (Rani, bertiga) -> ditanggung 170rb/orang.
    WiFi 200rb (Budi, berdua Rani-Budi) -> ditanggung 100rb/orang.
    Budi bayar 100rb ke Rani.
    Saldo akhir: Rani +140rb, Budi +30rb, Sinta -170rb (total 0).
    """
    data = model.data_kosong()
    for nama in ("Rani", "Budi", "Sinta"):
        model.tambah_anggota(data, nama)
    model.tambah_tagihan(data, "Listrik", "Rani", 510000,
                         ["Rani", "Budi", "Sinta"], "2026-11-01")
    model.tambah_tagihan(data, "WiFi", "Budi", 200000,
                         ["Rani", "Budi"], "2026-11-10")
    model.tambah_pembayaran(data, "Budi", "Rani", 100000, "2026-11-05")
    return data


def baca_csv(teks):
    """Ubah teks CSV menjadi daftar baris (daftar kolom string)."""
    return list(csv.reader(io.StringIO(teks)))


class TestEksporTagihan(unittest.TestCase):
    def test_header_dan_isi_benar(self):
        baris = baca_csv(export_mod.ekspor_csv_tagihan(data_contoh()))
        self.assertEqual(
            baris[0],
            ["nomor", "nama", "pembayar", "jumlah", "tanggal", "peserta"])
        self.assertEqual(
            baris[1],
            ["1", "Listrik", "Rani", "510000", "2026-11-01",
             "Rani;Budi;Sinta"])
        self.assertEqual(
            baris[2],
            ["2", "WiFi", "Budi", "200000", "2026-11-10", "Rani;Budi"])
        self.assertEqual(len(baris), 3)

    def test_data_kosong_hanya_header(self):
        baris = baca_csv(export_mod.ekspor_csv_tagihan(model.data_kosong()))
        self.assertEqual(len(baris), 1)
        self.assertEqual(baris[0][0], "nomor")


class TestEksporPembayaran(unittest.TestCase):
    def test_header_dan_isi_benar(self):
        baris = baca_csv(export_mod.ekspor_csv_pembayaran(data_contoh()))
        self.assertEqual(baris[0], ["nomor", "dari", "ke", "jumlah",
                                    "tanggal"])
        self.assertEqual(baris[1], ["1", "Budi", "Rani", "100000",
                                    "2026-11-05"])
        self.assertEqual(len(baris), 2)

    def test_data_kosong_hanya_header(self):
        baris = baca_csv(
            export_mod.ekspor_csv_pembayaran(model.data_kosong()))
        self.assertEqual(len(baris), 1)


class TestEksporLaporan(unittest.TestCase):
    def test_header_dan_isi_benar(self):
        baris = baca_csv(export_mod.ekspor_csv_laporan(data_contoh(),
                                                        "2026-11"))
        self.assertEqual(
            baris[0],
            ["bulan", "anggota", "dibayar", "ditanggung", "membayar",
             "menerima", "saldo_akhir"])
        per_anggota = {b[1]: b for b in baris[1:]}
        self.assertEqual(
            per_anggota["Rani"],
            ["2026-11", "Rani", "510000", "270000", "0", "100000",
             "140000"])
        self.assertEqual(
            per_anggota["Budi"],
            ["2026-11", "Budi", "200000", "270000", "100000", "0",
             "30000"])
        self.assertEqual(
            per_anggota["Sinta"],
            ["2026-11", "Sinta", "0", "170000", "0", "0", "-170000"])
        self.assertEqual(len(baris), 4)

    def test_bulan_tanpa_tagihan_angka_nol(self):
        baris = baca_csv(export_mod.ekspor_csv_laporan(data_contoh(),
                                                        "2026-12"))
        per_anggota = {b[1]: b for b in baris[1:]}
        # Tidak ada tagihan/pembayaran di Desember, tapi saldo akhir
        # tetap saldo keseluruhan (bukan nol).
        self.assertEqual(per_anggota["Rani"][2:6],
                         ["0", "0", "0", "0"])
        self.assertEqual(per_anggota["Rani"][6], "140000")


if __name__ == "__main__":
    unittest.main()

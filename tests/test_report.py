"""Unit test laporan bulanan (report.py)."""

import unittest

from bagirata import model
from bagirata.report import laporan_bulanan


def data_contoh():
    data = model.data_kosong()
    for nama in ("Rani", "Budi"):
        model.tambah_anggota(data, nama)
    model.tambah_tagihan(data, "Listrik", "Rani", 300001,
                         ["Rani", "Budi"], "2026-11-03")
    model.tambah_tagihan(data, "Galon", "Budi", 50000,
                         ["Rani", "Budi"], "2026-10-20")
    model.tambah_pembayaran(data, "Budi", "Rani", 100000, "2026-11-05")
    return data


class TestLaporanBulanan(unittest.TestCase):
    def test_filter_bulan(self):
        lap = laporan_bulanan(data_contoh(), "2026-11")
        self.assertEqual(lap["jumlah_tagihan"], 1)  # Galon Oktober tidak ikut
        self.assertEqual(lap["total_tagihan"], 300001)
        self.assertEqual(lap["jumlah_pembayaran"], 1)

    def test_ditanggung_pakai_bagi_rata_eksak(self):
        lap = laporan_bulanan(data_contoh(), "2026-11")
        # 300001 / 2 = 150000 sisa 1 -> Rani (peserta pertama) 150001
        self.assertEqual(lap["per_anggota"]["Rani"]["ditanggung"], 150001)
        self.assertEqual(lap["per_anggota"]["Budi"]["ditanggung"], 150000)

    def test_ringkasan_per_anggota(self):
        lap = laporan_bulanan(data_contoh(), "2026-11")
        rani = lap["per_anggota"]["Rani"]
        self.assertEqual(rani["dibayar"], 300001)
        self.assertEqual(rani["menerima"], 100000)
        self.assertEqual(rani["membayar"], 0)
        budi = lap["per_anggota"]["Budi"]
        self.assertEqual(budi["membayar"], 100000)

    def test_saldo_akhir_konsisten_dengan_saldo(self):
        lap = laporan_bulanan(data_contoh(), "2026-11")
        self.assertEqual(lap["saldo_akhir"], {"Rani": 25000, "Budi": -25000})

    def test_bulan_tanpa_data(self):
        lap = laporan_bulanan(data_contoh(), "2026-12")
        self.assertEqual(lap["jumlah_tagihan"], 0)
        self.assertEqual(lap["total_tagihan"], 0)


if __name__ == "__main__":
    unittest.main()

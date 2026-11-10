"""Unit test logika pembagian (split.py)."""

import unittest

from bagirata import model
from bagirata.split import bagi_proporsional, bagi_rata, hitung_saldo


class TestBagiRata(unittest.TestCase):
    def test_total_selalu_tepat(self):
        for jumlah in (100000, 100001, 999, 1, 0):
            bagian = bagi_rata(jumlah, ["A", "B", "C"])
            self.assertEqual(sum(bagian.values()), jumlah)

    def test_sisa_dibebankan_ke_peserta_pertama(self):
        self.assertEqual(bagi_rata(100001, ["A", "B", "C"]),
                         {"A": 33334, "B": 33334, "C": 33333})

    def test_peserta_kosong_ditolak(self):
        with self.assertRaises(ValueError):
            bagi_rata(1000, [])


class TestBagiProporsional(unittest.TestCase):
    def test_total_selalu_tepat(self):
        bagian = bagi_proporsional(100000, ["A", "B"], {"A": 2, "B": 1})
        self.assertEqual(sum(bagian.values()), 100000)
        self.assertEqual(bagian, {"A": 66667, "B": 33333})

    def test_bobot_nol_ditolak(self):
        with self.assertRaises(ValueError):
            bagi_proporsional(1000, ["A", "B"], {"A": 1, "B": 0})


class TestHitungSaldo(unittest.TestCase):
    def _data(self):
        data = model.data_kosong()
        for nama in ("Rani", "Budi", "Sinta"):
            model.tambah_anggota(data, nama)
        model.tambah_tagihan(data, "Listrik", "Rani", 300000,
                             ["Rani", "Budi", "Sinta"], "2026-11-01")
        model.tambah_tagihan(data, "WiFi", "Budi", 200001,
                             ["Rani", "Budi", "Sinta"], "2026-11-02")
        return data

    def test_saldo_tagihan_saja(self):
        saldo = hitung_saldo(self._data())
        self.assertEqual(saldo, {
            "Rani": 133333, "Budi": 33334, "Sinta": -166667})

    def test_total_saldo_selalu_nol(self):
        self.assertEqual(sum(hitung_saldo(self._data()).values()), 0)

    def test_saldo_memperhitungkan_pembayaran(self):
        data = self._data()
        model.tambah_pembayaran(data, "Sinta", "Rani", 166667, "2026-11-05")
        saldo = hitung_saldo(data)
        self.assertEqual(saldo["Sinta"], 0)
        self.assertEqual(saldo["Rani"], -33334)
        self.assertEqual(sum(saldo.values()), 0)


if __name__ == "__main__":
    unittest.main()

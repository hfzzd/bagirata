"""Unit test rencana pelunasan (settle.py)."""

import unittest

from bagirata.settle import rencana_pelunasan


def terapkan(saldo, rencana):
    hasil = dict(saldo)
    for dari, ke, jumlah in rencana:
        hasil[dari] += jumlah
        hasil[ke] -= jumlah
    return hasil


class TestRencanaPelunasan(unittest.TestCase):
    def test_semua_lunas_tanpa_transfer(self):
        self.assertEqual(rencana_pelunasan({"A": 0, "B": 0}), [])

    def test_satu_transfer_mencukupi(self):
        self.assertEqual(rencana_pelunasan({"A": 100000, "B": -100000}),
                         [("B", "A", 100000)])

    def test_jumlah_transfer_tidak_lebih_dari_n_min_1(self):
        saldo = {"A": 50000, "B": -30000, "C": -20000, "D": 10000,
                 "E": -10000}
        rencana = rencana_pelunasan(saldo)
        self.assertLessEqual(len(rencana), len(saldo) - 1)
        self.assertTrue(all(v == 0 for v in terapkan(saldo, rencana).values()))

    def test_rencana_melunasi_semua_saldo(self):
        saldo = {"Rani": 133333, "Budi": 33334, "Sinta": -166667}
        rencana = rencana_pelunasan(saldo)
        self.assertEqual(len(rencana), 2)
        self.assertTrue(all(v == 0 for v in terapkan(saldo, rencana).values()))

    def test_total_transfer_sama_dengan_total_utang(self):
        saldo = {"A": 70000, "B": -40000, "C": -30000}
        rencana = rencana_pelunasan(saldo)
        self.assertEqual(sum(j for _, _, j in rencana), 70000)


if __name__ == "__main__":
    unittest.main()

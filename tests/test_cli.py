"""Test end-to-end CLI BagiRata (via main() dengan file data sementara)."""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from bagirata.cli import main


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = os.path.join(self.tmp.name, "data.json")

    def tearDown(self):
        self.tmp.cleanup()

    def jalan(self, *args):
        """Jalankan CLI, kembalikan (kode_keluar, output)."""
        out = io.StringIO()
        with redirect_stdout(out):
            kode = main(["--data", self.data, *args])
        return kode, out.getvalue()

    def test_alur_lengkap(self):
        kode, _ = self.jalan("anggota", "tambah", "Rani")
        self.assertEqual(kode, 0)
        self.jalan("anggota", "tambah", "Budi")
        kode, out = self.jalan("anggota", "daftar")
        self.assertIn("1. Rani", out)
        self.assertIn("2. Budi", out)
        kode, _ = self.jalan("tagihan", "tambah", "--nama", "Listrik",
                             "--pembayar", "Rani", "--jumlah", "300000",
                             "--peserta", "Rani", "Budi")
        self.assertEqual(kode, 0)
        kode, out = self.jalan("saldo")
        self.assertIn("Rani: berhak menerima Rp150.000", out)
        self.assertIn("Budi: berutang Rp150.000", out)
        kode, out = self.jalan("lunas")
        self.assertIn("Budi -> Rani: Rp150.000", out)
        kode, _ = self.jalan("bayar", "--dari", "Budi", "--ke", "Rani",
                             "--jumlah", "150000")
        self.assertEqual(kode, 0)
        kode, out = self.jalan("lunas")
        self.assertIn("Semua sudah lunas", out)
        kode, out = self.jalan("laporan", "--bulan", "2026-11")
        self.assertIn("Laporan 2026-11", out)

    def test_input_salah_kode_keluar_1(self):
        kode, _ = self.jalan("anggota", "tambah", "Rani")
        self.assertEqual(kode, 0)
        # Duplikat anggota -> galat, kode 1
        kode, _ = self.jalan("anggota", "tambah", "Rani")
        self.assertEqual(kode, 1)
        # Tagihan dengan pembayar tak dikenal -> galat, kode 1
        kode, _ = self.jalan("tagihan", "tambah", "--nama", "X",
                             "--pembayar", "Dedi", "--jumlah", "1000",
                             "--peserta", "Rani")
        self.assertEqual(kode, 1)

    def test_pengingat_dalam_negatif_ditolak(self):
        # --dalam negatif tidak masuk akal; ditolak ramah dengan kode 1.
        kode, _ = self.jalan("pengingat", "--dalam", "-1")
        self.assertEqual(kode, 1)
        kode, out = self.jalan("pengingat", "--dalam", "0")
        self.assertEqual(kode, 0)
        self.assertIn("Aman", out)

    def test_hapus_tagihan_lewat_cli(self):
        self.jalan("anggota", "tambah", "Rani")
        self.jalan("tagihan", "tambah", "--nama", "A", "--pembayar", "Rani",
                   "--jumlah", "1000", "--peserta", "Rani")
        self.jalan("tagihan", "tambah", "--nama", "B", "--pembayar", "Rani",
                   "--jumlah", "2000", "--peserta", "Rani")
        kode, out = self.jalan("tagihan", "hapus", "1")
        self.assertEqual(kode, 0)
        self.assertIn("dihapus", out)
        _, out = self.jalan("tagihan", "daftar")
        self.assertNotIn("1. A", out)
        self.assertIn("1. B", out)


if __name__ == "__main__":
    unittest.main()

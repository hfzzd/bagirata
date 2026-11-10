"""Antarmuka baris perintah (CLI) BagiRata.

Contoh pemakaian:
    bagirata anggota tambah "Rani"
    bagirata anggota daftar
    bagirata tagihan tambah --nama "Listrik" --pembayar Rani \\
        --jumlah 300000 --peserta Rani Budi Sinta
    bagirata tagihan daftar
"""

import argparse
import os
import sys

from . import model
from . import split as split_mod


def _parser():
    p = argparse.ArgumentParser(
        prog="bagirata",
        description="Pembagi tagihan untuk anak kos & teman serumah.",
    )
    p.add_argument(
        "--data",
        default=os.environ.get("BAGIRATA_DATA", model.DEFAULT_DATA_FILE),
        help="File data JSON (bawaan: bagirata.json atau $BAGIRATA_DATA).",
    )
    sub = p.add_subparsers(dest="perintah", required=True)

    anggota = sub.add_parser("anggota", help="Kelola daftar anggota.")
    anggota_sub = anggota.add_subparsers(dest="aksi", required=True)
    tambah = anggota_sub.add_parser("tambah", help="Tambah satu anggota.")
    tambah.add_argument("nama", help="Nama anggota, mis. \"Rani\".")
    anggota_sub.add_parser("daftar", help="Tampilkan semua anggota.")

    tagihan = sub.add_parser("tagihan", help="Kelola tagihan bersama.")
    tagihan_sub = tagihan.add_subparsers(dest="aksi", required=True)
    t_tambah = tagihan_sub.add_parser("tambah", help="Catat satu tagihan.")
    t_tambah.add_argument("--nama", required=True, help="Nama tagihan.")
    t_tambah.add_argument("--pembayar", required=True,
                          help="Anggota yang membayar dulu.")
    t_tambah.add_argument("--jumlah", required=True, type=int,
                          help="Jumlah tagihan dalam rupiah.")
    t_tambah.add_argument("--peserta", required=True, nargs="+",
                          help="Anggota yang ikut menanggung.")
    t_tambah.add_argument("--tanggal", default=None,
                          help="Tanggal YYYY-MM-DD (bawaan: hari ini).")
    tagihan_sub.add_parser("daftar", help="Tampilkan semua tagihan.")

    sub.add_parser("saldo", help="Tampilkan saldo tiap anggota.")
    return p


def _rupiah(n):
    return f"Rp{n:,}".replace(",", ".")


def main(argv=None):
    args = _parser().parse_args(argv)
    try:
        data = model.muat(args.data)
        if args.perintah == "anggota":
            if args.aksi == "tambah":
                nama = model.tambah_anggota(data, args.nama)
                model.simpan(args.data, data)
                print(f"Anggota '{nama}' ditambahkan.")
            else:
                anggota = model.daftar_anggota(data)
                if not anggota:
                    print("Belum ada anggota. Tambah dengan "
                          "'bagirata anggota tambah <nama>'.")
                for i, nama in enumerate(anggota, 1):
                    print(f"{i}. {nama}")
        elif args.perintah == "tagihan":
            if args.aksi == "tambah":
                t = model.tambah_tagihan(
                    data, args.nama, args.pembayar, args.jumlah,
                    args.peserta, args.tanggal,
                )
                model.simpan(args.data, data)
                print(f"Tagihan '{t['nama']}' {_rupiah(t['jumlah'])} dicatat, "
                      f"dibayar {t['pembayar']} untuk "
                      f"{len(t['peserta'])} peserta.")
            else:
                tagihan = model.daftar_tagihan(data)
                if not tagihan:
                    print("Belum ada tagihan.")
                for i, t in enumerate(tagihan, 1):
                    print(f"{i}. {t['nama']} — {_rupiah(t['jumlah'])} "
                          f"(dibayar {t['pembayar']}, {t['tanggal']})")
        elif args.perintah == "saldo":
            saldo = split_mod.hitung_saldo(data)
            if not saldo:
                print("Belum ada anggota.")
            for nama, nilai in saldo.items():
                if nilai > 0:
                    print(f"{nama}: berhak menerima {_rupiah(nilai)}")
                elif nilai < 0:
                    print(f"{nama}: berutang {_rupiah(-nilai)}")
                else:
                    print(f"{nama}: lunas")
        return 0
    except model.BagiRataError as e:
        print(f"Galat: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

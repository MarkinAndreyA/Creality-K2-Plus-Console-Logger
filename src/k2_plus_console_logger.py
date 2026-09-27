#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Creality K2 Plus Console Logger by FDM AI Lab — V2.3.0."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import queue
import re
import shlex
import sys
import tarfile
import threading
import time
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Callable

try:
    import customtkinter as ctk
except Exception:
    ctk = None

try:
    import paramiko
except Exception:
    paramiko = None

import tkinter as tk
from tkinter import filedialog, messagebox

APP_NAME = "Creality K2 Plus Console Logger by FDM AI Lab"
VERSION = "2.3.0"
DEFAULT_USER = "root"
DEFAULT_PASSWORD = "creality_2024"
DEFAULT_MOONRAKER_PORT = 7125
DEFAULT_SSH_PORT = 22
DEFAULT_PRINTER_NAME = "K2_Plus"
CANONICAL_CONFIG_ROOT = "/mnt/UDISK/printer_data/config"
CONFIG_CANDIDATES = (
    CANONICAL_CONFIG_ROOT,
    "/usr/data/printer_data/config",
    "/home/creality/printer_data/config",
    "/root/printer_data/config",
)
POLL_SECONDS = 0.50
SSH_IO_TIMEOUT = 12.0
BACKUP_IDLE_TIMEOUT = 15.0
MAX_BACKUP_FILES = 5000
MAX_BACKUP_DIRS = 1000
MAX_BACKUP_BYTES = 64 * 1024 * 1024
SETTINGS_FILE = "settings.json"

I18N = {
    "ru": {
        "tab_main": "Основное", "tab_log": "Журнал", "page_title": APP_NAME,
        "connection": "Подключение", "printer_name": "Имя принтера", "printer_ip": "IP / hostname",
        "moonraker_port": "Moonraker порт", "ssh_port": "SSH порт", "ssh_user": "Логин SSH",
        "ssh_password": "Пароль SSH", "show_password": "Показать пароль", "ssh_key": "SSH private key", "remember_connection": "Запомнить подключение",
        "browse": "Обзор…", "test_connection": "Тест связи", "moonraker_state": "Moonraker: не проверено",
        "ssh_state": "SSH: не проверено", "logging": "Логирование консоли", "log_folder": "Папка логов",
        "log_name": "Имя log-файла", "auto_name": "Автоимя", "start_logger": "Старт Logger",
        "stop_logger": "Стоп Logger", "logger_stopped": "Logger: остановлен", "logger_running": "Logger: работает",
        "printer_controls": "Управление принтером", "pause_resume": "Pause / Resume",
        "backup_config": "Backup конфигурации", "backup_folder": "Папка Backup", "config_path": "Config path",
        "create_backup": "Создать ZIP Backup", "cancel_backup": "Отмена", "backup_idle": "Backup: готов",
        "backup_inventory": "Оценка файлов и объёма…", "backup_copying": "Передача конфигурации…", "backup_cancelled": "Backup отменён",
        "backup_cancelling": "Отмена Backup…",
        "backup_stage_ssh": "SSH подключение…", "backup_stage_root": "Проверка config root…",
        "backup_stage_inventory": "Оценка файлов и объёма…", "backup_stage_stream": "Передача TAR по SSH…",
        "backup_stage_zip": "Создание ZIP…", "backup_stage_verify": "Проверка ZIP…",
        "ssh_keys": "SSH ключ", "key_folder": "Папка ключа", "key_name": "Имя ключа",
        "generate_key": "Сгенерировать ключ", "generate_install_key": "Сгенерировать + установить",
        "install_existing_key": "Установить public key", "copy_selected": "Копировать выделенное",
        "copy_all": "Копировать всё", "save_snapshot": "Сохранить snapshot…", "clear_view": "Очистить экран",
        "language": "Язык / Language", "status_ready": "Готово", "confirm_pause": "Приостановить текущую печать?",
        "confirm_resume": "Возобновить приостановленную печать?",
        "not_printing": "Принтер сейчас не находится в состоянии printing/paused.",
        "key_write_warning": "Будет изменён ~/.ssh/authorized_keys на принтере. Продолжить?",
        "backup_warning": "Backup может содержать пароли, сетевые параметры и другие чувствительные данные. Храните архив приватно. Продолжить?",
        "select_log_folder": "Выберите папку логов", "select_backup_folder": "Выберите папку Backup",
        "select_key_folder": "Выберите папку SSH-ключа", "select_private_key": "Выберите private SSH key",
        "snapshot_title": "Сохранить снимок консоли", "error": "Ошибка", "success": "Готово", "warning": "Внимание",
        "connection_ok": "Moonraker: PASS", "ssh_ok": "SSH: PASS", "connection_fail": "Moonraker: FAIL",
        "ssh_fail": "SSH: FAIL", "key_created": "SSH-ключ создан", "key_installed": "Public key установлен и проверен",
        "backup_done": "Backup создан", "snapshot_done": "Snapshot сохранён", "logger_file": "Лог-файл",
        "paramiko_missing": "Не установлен пакет paramiko. Установите requirements.txt или используйте собранный EXE.",
        "ctk_missing": "Не установлен пакет customtkinter. Установите requirements.txt или используйте собранный EXE.",
        "backup_root": "Remote root", "backup_progress": "Прогресс", "backup_canonical_hint": "K2 Plus canonical: /mnt/UDISK/printer_data/config",
    },
    "en": {
        "tab_main": "Main", "tab_log": "Log", "page_title": APP_NAME,
        "connection": "Connection", "printer_name": "Printer name", "printer_ip": "IP / hostname",
        "moonraker_port": "Moonraker port", "ssh_port": "SSH port", "ssh_user": "SSH login",
        "ssh_password": "SSH password", "show_password": "Show password", "ssh_key": "SSH private key", "remember_connection": "Remember connection",
        "browse": "Browse…", "test_connection": "Connection test", "moonraker_state": "Moonraker: not tested",
        "ssh_state": "SSH: not tested", "logging": "Console logging", "log_folder": "Log folder",
        "log_name": "Log file name", "auto_name": "Auto name", "start_logger": "Start Logger",
        "stop_logger": "Stop Logger", "logger_stopped": "Logger: stopped", "logger_running": "Logger: running",
        "printer_controls": "Printer controls", "pause_resume": "Pause / Resume",
        "backup_config": "Configuration backup", "backup_folder": "Backup folder", "config_path": "Config path",
        "create_backup": "Create ZIP Backup", "cancel_backup": "Cancel", "backup_idle": "Backup: ready",
        "backup_inventory": "Estimating files and size…", "backup_copying": "Streaming configuration…", "backup_cancelled": "Backup cancelled",
        "backup_cancelling": "Cancelling Backup…",
        "backup_stage_ssh": "SSH connection…", "backup_stage_root": "Checking config root…",
        "backup_stage_inventory": "Estimating files and size…", "backup_stage_stream": "Streaming TAR over SSH…",
        "backup_stage_zip": "Creating ZIP…", "backup_stage_verify": "Verifying ZIP…",
        "ssh_keys": "SSH key", "key_folder": "Key folder", "key_name": "Key name",
        "generate_key": "Generate key", "generate_install_key": "Generate + install",
        "install_existing_key": "Install public key", "copy_selected": "Copy selection", "copy_all": "Copy all",
        "save_snapshot": "Save snapshot…", "clear_view": "Clear view", "language": "Language / Язык",
        "status_ready": "Ready", "confirm_pause": "Pause the current print?", "confirm_resume": "Resume the paused print?",
        "not_printing": "Printer is not currently in printing/paused state.",
        "key_write_warning": "This will modify ~/.ssh/authorized_keys on the printer. Continue?",
        "backup_warning": "A backup can contain passwords, network parameters and other sensitive data. Keep it private. Continue?",
        "select_log_folder": "Select log folder", "select_backup_folder": "Select Backup folder",
        "select_key_folder": "Select SSH key folder", "select_private_key": "Select private SSH key",
        "snapshot_title": "Save console snapshot", "error": "Error", "success": "Done", "warning": "Warning",
        "connection_ok": "Moonraker: PASS", "ssh_ok": "SSH: PASS", "connection_fail": "Moonraker: FAIL",
        "ssh_fail": "SSH: FAIL", "key_created": "SSH key created", "key_installed": "Public key installed and verified",
        "backup_done": "Backup created", "snapshot_done": "Snapshot saved", "logger_file": "Log file",
        "paramiko_missing": "The paramiko package is not installed. Install requirements.txt or use the compiled EXE.",
        "ctk_missing": "The customtkinter package is not installed. Install requirements.txt or use the compiled EXE.",
        "backup_root": "Remote root", "backup_progress": "Progress", "backup_canonical_hint": "K2 Plus canonical: /mnt/UDISK/printer_data/config",
    },
}


def user_settings_path() -> Path:
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or str(Path.home())
    p = Path(base) / "FDM_AI_Lab" / "K2_Plus_Console_Logger"
    p.mkdir(parents=True, exist_ok=True)
    return p / SETTINGS_FILE


def now_local() -> dt.datetime:
    return dt.datetime.now().astimezone()


def full_stamp(value: dt.datetime | None = None) -> str:
    value = value or now_local()
    return value.strftime("%Y%m%d_%H%M%S_") + f"{value.microsecond // 1000:03d}" + value.strftime("%z")


def sanitize_name(value: str, fallback: str = DEFAULT_PRINTER_NAME) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", (value or "").strip()).strip("._-")
    return value or fallback


def default_log_name(printer: str, at: dt.datetime | None = None) -> str:
    return f"log_{sanitize_name(printer)}_{full_stamp(at)}.log"


def default_snapshot_name(printer: str, start: dt.datetime, end: dt.datetime) -> str:
    return f"console_snapshot_{sanitize_name(printer)}_{full_stamp(start)}_{full_stamp(end)}.log"


def default_backup_name(printer: str, at: dt.datetime | None = None) -> str:
    return f"backup_{sanitize_name(printer)}_{full_stamp(at)}.zip"


CONNECTION_SETTING_KEYS = {"host", "moonraker_port", "ssh_port", "ssh_user", "key_path"}


def sanitize_settings_for_save(data: dict[str, Any]) -> dict[str, Any]:
    out = dict(data)
    out.pop("password", None)
    if not bool(out.get("remember_connection", False)):
        for key in CONNECTION_SETTING_KEYS:
            out.pop(key, None)
    return out


def load_settings() -> dict[str, Any]:
    try:
        p = user_settings_path()
        if p.exists():
            obj = json.loads(p.read_text(encoding="utf-8"))
            if not isinstance(obj, dict):
                return {}
            clean = sanitize_settings_for_save(obj)
            if str(clean.get("config_path", "")).strip().upper() == "AUTO":
                clean["config_path"] = CANONICAL_CONFIG_ROOT
            # V2.3 privacy migration: legacy V2.0/V2.1 connection state is not restored
            # unless the user explicitly opted in via remember_connection=true.
            if clean != obj:
                p.write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")
            return clean
    except Exception:
        pass
    return {}


def save_settings(data: dict[str, Any]) -> None:
    data = sanitize_settings_for_save(data)
    user_settings_path().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def http_json(host: str, port: int, endpoint: str, method: str = "GET", timeout: float = 5.0) -> dict[str, Any]:
    url = f"http://{host.strip()}:{int(port)}{endpoint}"
    req = urllib.request.Request(url, data=(b"" if method.upper() == "POST" else None), method=method.upper(),
                                 headers={"User-Agent": f"FDM-AI-Lab-K2-Console-Logger/{VERSION}"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read().decode("utf-8", "replace")
        return json.loads(raw) if raw.strip() else {}


def extract_store(obj: Any) -> list[Any]:
    r = obj.get("result", obj) if isinstance(obj, dict) else obj
    if isinstance(r, dict):
        for k in ("gcode_store", "store", "messages"):
            if isinstance(r.get(k), list):
                return r[k]
    return r if isinstance(r, list) else []


def record_key(x: Any) -> str:
    try:
        return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    except Exception:
        return repr(x)


def record_text(x: Any) -> str:
    if isinstance(x, dict):
        for k in ("message", "msg", "response"):
            if k in x:
                return str(x[k])
        return json.dumps(x, ensure_ascii=False, sort_keys=True)
    return str(x)


def ssh_connect(host: str, port: int, username: str, password: str, key_path: str = "", timeout: float = 7.0):
    if paramiko is None:
        raise RuntimeError("paramiko is not installed")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    kwargs: dict[str, Any] = dict(hostname=host.strip(), port=int(port), username=username.strip(), timeout=timeout,
                                  banner_timeout=timeout, auth_timeout=timeout, allow_agent=False, look_for_keys=False)
    if key_path.strip():
        kwargs["key_filename"] = str(Path(key_path).expanduser())
        if password:
            kwargs["passphrase"] = password
    elif password:
        kwargs["password"] = password
    client.connect(**kwargs)
    return client


def ssh_exec_text(client, command: str, timeout: float = 10.0) -> tuple[int, str, str]:
    _stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    rc = stdout.channel.recv_exit_status()
    return rc, stdout.read().decode("utf-8", "replace"), stderr.read().decode("utf-8", "replace")


def validate_backup_root(root: str) -> str:
    root = (root or "").strip().replace("\", "/")
    if not root.startswith("/"):
        raise ValueError("Config path must be an absolute remote path")
    if any(ch in root for ch in (" ", "
", "")):
        raise ValueError("Config path contains unsupported control characters")
    parts = [x for x in root.split("/") if x]
    if any(x in (".", "..") for x in parts):
        raise ValueError("Config path traversal is not allowed")
    return "/" + "/".join(parts)


class BackupCancelled(RuntimeError):
    pass


def _register_channel(register: Callable[[Any | None], None] | None, channel: Any | None) -> None:
    if register is not None:
        register(channel)


def ssh_exec_text_cancelable(client, command: str, cancel: threading.Event,
                             register: Callable[[Any | None], None] | None = None,
                             idle_timeout: float = BACKUP_IDLE_TIMEOUT) -> tuple[int, str, str]:
    transport = client.get_transport()
    if transport is None or not transport.is_active():
        raise RuntimeError("SSH transport is not active")
    if cancel.is_set():
        raise BackupCancelled("Backup cancelled")
    chan = transport.open_session(timeout=SSH_IO_TIMEOUT)
    _register_channel(register, chan)
    try:
        chan.settimeout(1.0)
        chan.exec_command(command)
        out = bytearray(); err = bytearray(); last = time.monotonic()
        while True:
            if cancel.is_set():
                raise BackupCancelled("Backup cancelled")
            moved = False
            while chan.recv_ready():
                chunk = chan.recv(65536)
                if chunk:
                    out.extend(chunk); moved = True
            while chan.recv_stderr_ready():
                chunk = chan.recv_stderr(65536)
                if chunk:
                    err.extend(chunk); moved = True
            if moved:
                last = time.monotonic()
            if chan.exit_status_ready() and not chan.recv_ready() and not chan.recv_stderr_ready():
                break
            if time.monotonic() - last > idle_timeout:
                raise TimeoutError(f"SSH command produced no data/status for {idle_timeout:.0f} s")
            time.sleep(0.03)
        rc = chan.recv_exit_status()
        return rc, out.decode("utf-8", "replace"), err.decode("utf-8", "replace")
    finally:
        try: chan.close()
        except Exception: pass
        _register_channel(register, None)


def detect_config_root_ssh(client, requested: str, cancel: threading.Event,
                           register: Callable[[Any | None], None] | None = None) -> str:
    requested = (requested or "").strip()
    candidates = list(CONFIG_CANDIDATES) if requested.upper() == "AUTO" else [validate_backup_root(requested or CANONICAL_CONFIG_ROOT)]
    for root in candidates:
        q = shlex.quote(root)
        rc, _out, _err = ssh_exec_text_cancelable(client, f"test -d {q}", cancel, register)
        if rc == 0:
            return root.rstrip("/")
    raise FileNotFoundError("Printer config directory not found. Set Config path manually.")


def ssh_backup_inventory(client, root: str, cancel: threading.Event,
                         register: Callable[[Any | None], None] | None = None) -> dict[str, int]:
    root = validate_backup_root(root)
    q = shlex.quote(root)
    cmd = (
        f"root={q}; "
        "files=$(find "$root" -type f 2>/dev/null | wc -l); "
        "dirs=$(find "$root" -type d 2>/dev/null | wc -l); "
        "kb=$(du -sk "$root" 2>/dev/null | awk '{print $1}'); "
        "printf '%s|%s|%s\n' "$files" "$dirs" "$kb""
    )
    rc, out, err = ssh_exec_text_cancelable(client, cmd, cancel, register)
    if rc != 0:
        raise RuntimeError(err.strip() or "Unable to inspect remote config directory")
    line = out.strip().splitlines()[-1] if out.strip() else ""
    parts = line.split("|")
    if len(parts) != 3:
        raise RuntimeError(f"Unexpected inventory response: {line!r}")
    files, dirs, kib = (int((x or "0").strip()) for x in parts)
    estimate = max(0, kib) * 1024
    if files > MAX_BACKUP_FILES:
        raise RuntimeError(f"Backup safety limit exceeded: more than {MAX_BACKUP_FILES} files")
    if dirs > MAX_BACKUP_DIRS:
        raise RuntimeError(f"Backup safety limit exceeded: more than {MAX_BACKUP_DIRS} directories")
    if estimate > MAX_BACKUP_BYTES:
        raise RuntimeError(f"Backup safety limit exceeded: more than {MAX_BACKUP_BYTES // (1024*1024)} MiB")
    return {"files": files, "dirs": dirs, "bytes_estimate": estimate}


def make_tar_command(root: str) -> str:
    root = validate_backup_root(root)
    parent, base = root.rsplit("/", 1)
    parent = parent or "/"
    qp, qb = shlex.quote(parent), shlex.quote(base)
    return (
        "if command -v tar >/dev/null 2>&1; then "
        f"exec tar -C {qp} -cf - {qb}; "
        "elif command -v busybox >/dev/null 2>&1; then "
        f"exec busybox tar -C {qp} -cf - {qb}; "
        "else echo 'tar/busybox not found' >&2; exit 127; fi"
    )


class SSHChannelReader:
    def __init__(self, channel, cancel: threading.Event, idle_timeout: float = BACKUP_IDLE_TIMEOUT):
        self.channel = channel
        self.cancel = cancel
        self.idle_timeout = float(idle_timeout)
        self.stderr = bytearray()
        self.bytes_received = 0
        self.last_activity = time.monotonic()

    def _drain_stderr(self) -> None:
        while self.channel.recv_stderr_ready():
            chunk = self.channel.recv_stderr(65536)
            if not chunk:
                break
            self.stderr.extend(chunk)
            self.last_activity = time.monotonic()

    def read(self, size: int = -1) -> bytes:
        if size is None or size < 0:
            size = 65536
        out = bytearray()
        while len(out) < size:
            if self.cancel.is_set():
                raise BackupCancelled("Backup cancelled")
            self._drain_stderr()
            if self.channel.recv_ready():
                chunk = self.channel.recv(min(65536, size - len(out)))
                if chunk:
                    out.extend(chunk)
                    self.bytes_received += len(chunk)
                    self.last_activity = time.monotonic()
                    continue
            if self.channel.exit_status_ready() and not self.channel.recv_ready():
                break
            if time.monotonic() - self.last_activity > self.idle_timeout:
                raise TimeoutError(f"SSH TAR stream stalled for {self.idle_timeout:.0f} s")
            time.sleep(0.02)
        return bytes(out)

    def close(self) -> None:
        pass


def wait_ssh_channel_exit(channel, cancel: threading.Event, reader: SSHChannelReader | None = None,
                          idle_timeout: float = BACKUP_IDLE_TIMEOUT) -> tuple[int, str]:
    last = time.monotonic()
    while not channel.exit_status_ready():
        if cancel.is_set():
            raise BackupCancelled("Backup cancelled")
        moved = False
        if reader is not None:
            before = len(reader.stderr)
            reader._drain_stderr()
            moved = len(reader.stderr) != before
        if moved:
            last = time.monotonic()
        if time.monotonic() - last > idle_timeout:
            raise TimeoutError(f"SSH command did not terminate for {idle_timeout:.0f} s")
        time.sleep(0.03)
    if reader is not None:
        reader._drain_stderr()
        stderr = reader.stderr.decode("utf-8", "replace").strip()
    else:
        stderr = ""
    return channel.recv_exit_status(), stderr


def _safe_tar_member_relative(name: str, expected_root_name: str) -> str | None:
    name = (name or "").replace("\\", "/")
    while name.startswith("./"):
        name = name[2:]
    if name.startswith("/"):
        raise RuntimeError(f"Unsafe absolute TAR member: {name}")
    parts = [p for p in name.split("/") if p not in ("", ".")]
    if any(p == ".." for p in parts):
        raise RuntimeError(f"Unsafe TAR traversal member: {name}")
    if not parts:
        return None
    if parts[0] != expected_root_name:
        raise RuntimeError(f"Unexpected TAR root member: {name}")
    rel = "/".join(parts[1:])
    return rel or None


def create_config_backup_from_tar(fileobj, root: str, partial_path: Path, printer_name: str,
                                  cancel: threading.Event, estimate: dict[str, int] | None = None,
                                  progress: Callable[[dict[str, Any]], None] | None = None) -> dict[str, Any]:
    root = validate_backup_root(root).rstrip("/")
    root_name = root.rsplit("/", 1)[-1]
    estimate = estimate or {}
    estimate_bytes = int(estimate.get("bytes_estimate", 0))
    estimate_files = int(estimate.get("files", 0))
    files_meta: list[dict[str, Any]] = []
    symlinks: list[dict[str, str]] = []
    copied = 0
    dirs = 0
    partial_path.parent.mkdir(parents=True, exist_ok=True)
    partial_path.unlink(missing_ok=True)
    if cancel.is_set():
        raise BackupCancelled("Backup cancelled")
    try:
        with zipfile.ZipFile(partial_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as zf:
            with tarfile.open(fileobj=fileobj, mode="r|*") as tf:
                for member in tf:
                    if cancel.is_set():
                        raise BackupCancelled("Backup cancelled")
                    rel = _safe_tar_member_relative(member.name, root_name)
                    if member.isdir():
                        dirs += 1
                        if dirs > MAX_BACKUP_DIRS:
                            raise RuntimeError(f"Backup safety limit exceeded: more than {MAX_BACKUP_DIRS} directories")
                        continue
                    if rel is None:
                        continue
                    if member.issym() or member.islnk():
                        symlinks.append({"path": rel, "target": member.linkname or ""})
                        continue
                    if not member.isfile():
                        continue
                    size = int(member.size or 0)
                    if len(files_meta) + 1 > MAX_BACKUP_FILES:
                        raise RuntimeError(f"Backup safety limit exceeded: more than {MAX_BACKUP_FILES} files")
                    if copied + size > MAX_BACKUP_BYTES:
                        raise RuntimeError(f"Backup safety limit exceeded: more than {MAX_BACKUP_BYTES // (1024*1024)} MiB")
                    src = tf.extractfile(member)
                    if src is None:
                        raise RuntimeError(f"Unable to read TAR member: {member.name}")
                    arc = f"config/{rel}"
                    with src, zf.open(arc, "w") as dst:
                        file_written = 0
                        while True:
                            if cancel.is_set():
                                raise BackupCancelled("Backup cancelled")
                            chunk = src.read(256 * 1024)
                            if not chunk:
                                break
                            dst.write(chunk)
                            file_written += len(chunk)
                            copied += len(chunk)
                            if copied > MAX_BACKUP_BYTES:
                                raise RuntimeError(f"Backup safety limit exceeded: more than {MAX_BACKUP_BYTES // (1024*1024)} MiB")
                            if progress:
                                progress({"phase": "copy", "index": len(files_meta) + 1,
                                          "file_count": estimate_files, "file": rel,
                                          "copied": copied, "bytes_total": estimate_bytes,
                                          "file_size": size})
                    if file_written != size:
                        raise RuntimeError(f"Incomplete TAR member: {member.name} ({file_written}/{size} bytes)")
                    files_meta.append({"path": rel, "size": size})
            manifest: dict[str, Any] = {
                "application": APP_NAME, "version": VERSION, "created": now_local().isoformat(),
                "printer_name": sanitize_name(printer_name), "source_root": root,
                "transport": "ssh_tar_stream", "files": files_meta, "symlinks": symlinks,
            }
            zf.writestr("FDM_AI_LAB_BACKUP_MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        return {"root": root, "files": len(files_meta), "symlinks": len(symlinks), "bytes": copied,
                "partial": str(partial_path)}
    except Exception:
        partial_path.unlink(missing_ok=True)
        raise


def verify_and_finalize_backup(partial_path: Path, final_path: Path,
                               progress: Callable[[dict[str, Any]], None] | None = None) -> None:
    if progress:
        progress({"phase": "stage", "stage": "verify", "output": str(partial_path)})
    with zipfile.ZipFile(partial_path, "r") as verify_zip:
        bad = verify_zip.testzip()
        if bad is not None:
            raise RuntimeError(f"ZIP verification failed at member: {bad}")
        if "FDM_AI_LAB_BACKUP_MANIFEST.json" not in verify_zip.namelist():
            raise RuntimeError("ZIP verification failed: backup manifest is missing")
    os.replace(partial_path, final_path)


def generate_rsa_key(private_path: Path, bits: int = 3072) -> tuple[Path, Path]:
    if paramiko is None:
        raise RuntimeError("paramiko is not installed")
    private_path.parent.mkdir(parents=True, exist_ok=True)
    if private_path.exists():
        raise FileExistsError(str(private_path))
    key = paramiko.RSAKey.generate(bits=bits)
    key.write_private_key_file(str(private_path))
    public_path = Path(str(private_path) + ".pub")
    public_path.write_text(f"{key.get_name()} {key.get_base64()} fdm-ai-lab-k2-plus\n", encoding="ascii")
    return private_path, public_path


def install_public_key(host: str, port: int, username: str, password: str, public_key_file: Path) -> str:
    if not password:
        raise ValueError("A password is required for first-time key installation")
    pub = public_key_file.read_text(encoding="ascii").strip()
    client = ssh_connect(host, port, username, password)
    try:
        rc, home, err = ssh_exec_text(client, 'printf "%s" "$HOME"')
        if rc != 0 or not home.strip():
            raise RuntimeError(err or "Unable to detect remote HOME")
        home = home.strip()
        qpub = shlex.quote(pub)
        command = (
            'umask 077; mkdir -p "$HOME/.ssh"; touch "$HOME/.ssh/authorized_keys"; '
            'chmod 700 "$HOME/.ssh"; chmod 600 "$HOME/.ssh/authorized_keys"; '
            f'grep -qxF -- {qpub} "$HOME/.ssh/authorized_keys" 2>/dev/null || '
            f'printf "%s\\n" {qpub} >> "$HOME/.ssh/authorized_keys"'
        )
        rc, _out, err = ssh_exec_text(client, command, timeout=SSH_IO_TIMEOUT)
        if rc != 0:
            raise RuntimeError(err or "Unable to update authorized_keys")
        return home
    finally:
        client.close()


class ConsoleLoggerThread(threading.Thread):
    def __init__(self, host: str, port: int, output_file: Path, ui_queue: queue.Queue, stop_event: threading.Event):
        super().__init__(daemon=True)
        self.host, self.port, self.output_file, self.ui_queue, self.stop_event = host, int(port), output_file, ui_queue, stop_event
        self.seen: set[str] = set()

    def emit(self, kind: str, text: str) -> None:
        self.ui_queue.put(("console", kind, text))

    def run(self) -> None:
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            initial = http_json(self.host, self.port, "/server/gcode_store?count=1000", timeout=5)
            for x in extract_store(initial):
                self.seen.add(record_key(x))
        except Exception as e:
            self.emit("system", f"LOGGER_INITIAL_HISTORY_WARNING: {e}")
        self.emit("system", f"LOGGER_START VERSION={VERSION}")
        try:
            with self.output_file.open("a", encoding="utf-8", buffering=1) as f:
                while not self.stop_event.is_set():
                    ts = now_local()
                    try:
                        store = http_json(self.host, self.port, "/server/gcode_store?count=1000", timeout=5)
                        for x in extract_store(store):
                            k = record_key(x)
                            if k in self.seen:
                                continue
                            self.seen.add(k)
                            line = f"{ts.isoformat()}  {record_text(x)}"
                            f.write(line + "\n")
                            self.emit("console", line)
                    except Exception as e:
                        self.emit("error", f"LOGGER_POLL_ERROR: {e}")
                    self.stop_event.wait(POLL_SECONDS)
        except Exception as e:
            self.emit("error", f"LOGGER_FATAL: {e}")
        finally:
            self.emit("system", "LOGGER_STOP")


class App:
    def __init__(self, root):
        self.root = root
        self.root.title(f"FDM AI Lab — K2 Plus Console Logger V{VERSION}")
        self.root.geometry("1320x860")
        self.root.minsize(1080, 720)
        self.settings = load_settings()
        self.lang = tk.StringVar(value=self.settings.get("language", "ru") if self.settings.get("language", "ru") in I18N else "ru")
        self.ui_queue: queue.Queue = queue.Queue()
        self.logger_thread: ConsoleLoggerThread | None = None
        self.logger_stop = threading.Event()
        self.log_started_at: dt.datetime | None = None
        self.console_started_at = now_local()
        self._last_auto_log_name = ""
        self.backup_cancel = threading.Event()
        self.backup_running = False
        self.backup_client = None
        self.backup_channel = None
        self.backup_run_id = 0
        self._bindings: list[tuple[Any, str]] = []
        self._build_vars()
        self._build_ui()
        self._apply_language()
        self._refresh_auto_log_name(True)
        self._poll_ui_queue()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def t(self, key: str) -> str:
        return I18N[self.lang.get()].get(key, key)

    def _build_vars(self):
        home = Path.home()
        self.printer_name = tk.StringVar(value=self.settings.get("printer_name", DEFAULT_PRINTER_NAME))
        self.remember_connection = tk.BooleanVar(value=bool(self.settings.get("remember_connection", False)))
        remembered = self.remember_connection.get()
        self.host = tk.StringVar(value=self.settings.get("host", "") if remembered else "")
        self.moonraker_port = tk.StringVar(value=str(self.settings.get("moonraker_port", DEFAULT_MOONRAKER_PORT) if remembered else DEFAULT_MOONRAKER_PORT))
        self.ssh_port = tk.StringVar(value=str(self.settings.get("ssh_port", DEFAULT_SSH_PORT) if remembered else DEFAULT_SSH_PORT))
        self.ssh_user = tk.StringVar(value=self.settings.get("ssh_user", DEFAULT_USER) if remembered else DEFAULT_USER)
        self.ssh_password = tk.StringVar(value=DEFAULT_PASSWORD)
        self.show_password = tk.BooleanVar(value=False)
        self.key_path = tk.StringVar(value=self.settings.get("key_path", "") if remembered else "")
        self.log_folder = tk.StringVar(value=self.settings.get("log_folder") or str(home / "Documents" / "FDM_AI_Lab" / "K2_Console_Logs"))
        self.log_name = tk.StringVar(value="")
        self.backup_folder = tk.StringVar(value=self.settings.get("backup_folder") or str(home / "Documents" / "FDM_AI_Lab" / "K2_Backups"))
        self.config_path = tk.StringVar(value=self.settings.get("config_path") or CANONICAL_CONFIG_ROOT)
        self.key_folder = tk.StringVar(value=self.settings.get("key_folder") or str(home / ".ssh"))
        self.key_name = tk.StringVar(value=self.settings.get("key_name", "fdm_ai_lab_k2_plus"))
        self.moonraker_status = tk.StringVar(value="")
        self.ssh_status = tk.StringVar(value="")
        self.logger_status = tk.StringVar(value="")
        self.footer_status = tk.StringVar(value="")
        self.backup_status = tk.StringVar(value="")

    def _section(self, parent, row: int, col: int, title_key: str, colspan: int = 1):
        frame = ctk.CTkFrame(parent, corner_radius=8)
        frame.grid(row=row, column=col, columnspan=colspan, padx=8, pady=8, sticky="nsew")
        frame.grid_columnconfigure(1, weight=1)
        title = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=14, weight="bold"), anchor="w")
        title.grid(row=0, column=0, columnspan=3, padx=12, pady=(10, 5), sticky="ew")
        self._bindings.append((title, title_key))
        return frame

    def _field(self, parent, row: int, label_key: str, var: tk.StringVar, browse: Callable | None = None,
               show: str | None = None, hint: str | None = None):
        label = ctk.CTkLabel(parent, text="", anchor="w")
        label.grid(row=row, column=0, padx=(12, 8), pady=5, sticky="w")
        self._bindings.append((label, label_key))
        ent = ctk.CTkEntry(parent, textvariable=var, show=show or "", height=30)
        ent.grid(row=row, column=1, padx=4, pady=5, sticky="ew")
        if browse:

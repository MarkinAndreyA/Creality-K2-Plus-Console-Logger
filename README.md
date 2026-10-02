# Creality K2 Plus Console Logger by FDM AI Lab — V2.3.0

Standalone Windows GUI logger for Creality K2 Plus / Moonraker.

## Features

- Russian / English interface;
- Moonraker + SSH connection test;
- live Moonraker `gcode_store` console logger;
- log and console snapshot export;
- configuration Backup of `/mnt/UDISK/printer_data/config` through regular SSH TAR streaming;
- Pause / Resume through Moonraker;
- RSA-3072 SSH key generation and public-key installation;
- privacy-safe connection persistence: host/SSH state is remembered only after explicit opt-in; password is never persisted.

## V2.3.0 Backup

SFTP is not used.

`SSH → config-root check → find/du inventory → remote TAR stream → local ZIP → ZIP verify → atomic rename`

Backup is read-only on the printer. The resulting ZIP may contain sensitive printer configuration and must be kept private unless separately sanitized.

## Known limitations — V2.3.0

Long-running console-logging sessions have known performance/scalability debt in the current implementation:

- the logger polls `/server/gcode_store?count=1000` every 0.50 s;
- each logger instance keeps an in-memory `seen` set for the full session without a retention limit;
- the Log textbox also grows for the full session;
- new console lines are inserted into the GUI and scrolled individually.

Because these structures are unbounded and GUI updates are per-line, memory/UI work can grow with session length. This limitation affects the console-logger path; it does not change the SSH TAR Backup workflow described above.

## Documentation

- [README_RU.md](README_RU.md) — полное руководство пользователя на русском;
- [README_ENG.md](README_ENG.md) — full English user manual;
- [SECURITY.md](SECURITY.md) — security and privacy notes;
- [CHANGELOG.md](CHANGELOG.md) — version history;
- [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) — third-party software notices.

The original DOCX manuals are preparation sources and are not published in the repository.

## Distribution

The public repository contains Python source and Markdown documentation. The Windows EXE is published as a Release asset.

The internal build/compilation block is intentionally not part of the public repository.

## Project license

No project LICENSE is provided. Third-party components remain subject to their own licenses listed in `THIRD_PARTY_NOTICES.md`.

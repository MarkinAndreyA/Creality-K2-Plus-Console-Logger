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

## Distribution

The public repository contains Python source and documentation. The Windows EXE is published as a release asset.

The internal build/compilation block is intentionally not part of the public repository.

See:
- `docs/K2_Plus_Console_Logger_Manual_RU_V2.3.0.docx`
- `docs/K2_Plus_Console_Logger_Manual_EN_V2.3.0.docx`
- `SECURITY.md`
- `CHANGELOG.md`


Russian documentation: `README_RU.md`.
- `THIRD_PARTY_NOTICES.md`

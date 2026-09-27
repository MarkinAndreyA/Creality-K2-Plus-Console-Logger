# Creality K2 Plus Console Logger by FDM AI Lab V2.3.0

## RU

V2.3.0 переводит Backup конфигурации с SFTP на обычный SSH TAR stream после того, как на K2 Plus было подтверждено зависание SFTP subsystem при исправном SSH.

Основные изменения:
- SFTP удалён из Backup;
- canonical source: `/mnt/UDISK/printer_data/config`;
- read-only remote `tar` / `busybox tar` stream;
- локальный ZIP с `.partial → verify → atomic rename`;
- Cancel закрывает активный SSH channel/client и освобождает GUI;
- безопасная проверка TAR paths и ограничения объёма;
- установка SSH public key также не зависит от SFTP;
- host/SSH state сохраняется только при явном Remember connection; password не сохраняется.

### Download

- `K2PlusConsoleLogger.exe` — Windows x64 executable.

Python source и документация находятся в репозитории.

**Важно:** Backup может содержать credentials, network configuration и другие чувствительные данные принтера. Не публикуйте Backup, реальные settings/logs, SSH keys или machine-specific connection data без отдельной очистки.

---

## EN

V2.3.0 moves configuration Backup from SFTP to a regular SSH TAR stream after K2 Plus testing showed that the SFTP subsystem may stall while regular SSH remains healthy.

Key changes:
- SFTP removed from Backup;
- canonical source: `/mnt/UDISK/printer_data/config`;
- read-only remote `tar` / `busybox tar` stream;
- local ZIP with `.partial → verify → atomic rename`;
- Cancel closes the active SSH channel/client and releases the GUI;
- safe TAR-path validation and size limits;
- SSH public-key installation no longer depends on SFTP;
- host/SSH state is persisted only after explicit Remember connection opt-in; password is never persisted.

### Download

- `K2PlusConsoleLogger.exe` — Windows x64 executable.

Python source and documentation are available in the repository.

**Important:** Backup archives may contain credentials, network configuration, or other sensitive printer data. Do not publish Backup archives, real settings/logs, SSH keys, or machine-specific connection data without a separate sanitation pass.

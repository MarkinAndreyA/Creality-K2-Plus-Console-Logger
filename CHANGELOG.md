# Changelog

## V2.3.0

- Removed SFTP from the configuration Backup path after target K2 Plus testing proved that the SFTP subsystem request can stall even when ordinary SSH is healthy.
- Backup now uses a single read-only SSH TAR stream with `tar` and `busybox tar` fallback.
- Added shell preflight for config-root existence plus `find` / `du` inventory.
- Added safe TAR member validation and traversal blocking before writing ZIP members.
- Preserved `.zip.partial` → verify → atomic final ZIP behavior.
- Cancel now closes the active SSH channel and client, releases the GUI immediately, and invalidates stale worker callbacks.
- Added SSH TAR idle timeout and existing 1000-dir / 5000-file / 64-MiB safety limits.
- Public-key installation no longer depends on SFTP; `authorized_keys` is updated through the regular SSH shell.
- Added TAR→ZIP, manifest, traversal and pre-cancel regression self-tests.

## V2.2.0

- Added explicit Backup-stage reporting and canonical `/mnt/UDISK/printer_data/config` root.
- Added connection-state privacy migration and opt-in Remember connection.
- Added `.partial` / ZIP verification and Backup safety limits.

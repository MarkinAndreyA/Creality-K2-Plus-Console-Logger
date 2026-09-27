# Creality K2 Plus Console Logger

**FDM AI Lab · User Manual — EN · Version 2.3.0**

> **Purpose of this document**  
> This guide is written for both regular and advanced users. The released Windows EXE is recommended for normal use. Python source is published separately for audit and development; the internal compilation block is intentionally not part of the public package.

# 1. What the application does

Creality K2 Plus Console Logger by FDM AI Lab is a standalone Windows GUI utility for Creality K2 Plus systems exposed through Moonraker and SSH. It combines live console logging, file snapshots, connectivity checks, configuration backup, Pause/Resume controls, and SSH-key management.

- Live Moonraker `gcode_store` view with local `.log` recording.
- Russian / English interface.
- Independent Moonraker and regular SSH connectivity tests.
- ZIP backup of `/mnt/UDISK/printer_data/config` through an SSH TAR stream, with no SFTP dependency.
- RSA-3072 SSH key generation and public-key installation.
- Pause / Resume through Moonraker REST.
- Automatic file names containing printer name and full local timestamp.

> **Safety model**  
> Logging and Backup are read operations. Public-key installation modifies `~/.ssh/authorized_keys`, while Pause/Resume changes print state. Those actions only occur after explicit user interaction.

# 2. Before the first run

| **Field**      | **Default**                    | **Notes**                                                    |
|----------------|--------------------------------|--------------------------------------------------------------|
| Printer name   | K2_Plus                        | Used in generated file names.                                |
| IP / hostname  | blank                          | Enter your K2 Plus address.                                  |
| Moonraker port | 7125                           | Default API port in the current project contour.             |
| SSH port       | 22                             | Standard SSH.                                                |
| SSH login      | root                           | Vendor/default value required by this project.               |
| SSH password   | creality_2024                  | Vendor/default value; editable. Never persisted to settings. |
| Config path    | /mnt/UDISK/printer_data/config | Canonical K2 Plus config root.                               |

If key authentication is used, select the private SSH key. When the key field is blank, password authentication is used.

> **Connection privacy**  
> Remember connection is OFF by default. With it disabled, host/IP, SSH user, ports and key path are not silently restored on later runs. The SSH password is never persisted.

# 3. Main tab

## 3.1. Connection

1.  Set a printer name. This only affects generated local file names.

2.  Enter the printer IP address or hostname.

3.  Review Moonraker and SSH ports.

4.  Keep `root / creality_2024` or enter your own SSH credentials.

5.  Optionally select a private SSH key.

6.  Click Connection test.

A successful test reports `Moonraker: PASS` and `SSH: PASS` independently. Failure of one transport does not automatically imply failure of the other.

> **Moonraker PASS but SSH FAIL**  
> Check SSH port, credentials or private key. Moonraker console logging can still work without SSH, but Backup and key installation require SSH.

## 3.2. Console logging

7.  Choose the log folder.

8.  Keep the generated file name or enter a custom one.

9.  Click Start Logger.

10. Open the Log tab to watch accumulated console output.

11. Click Stop Logger when the diagnostic session is complete.

The logger polls Moonraker and records new `gcode_store` entries while suppressing records it has already seen.

`log_K2_Plus_20260925_010205_044+0500.log`

The full timestamp contains date, time, milliseconds and local UTC offset.

## 3.3. Pause / Resume

The single button is state-aware. The application queries `print_stats.state`:

- `printing` → user is asked to confirm Pause;
- `paused` → user is asked to confirm Resume;
- any other state → no command is sent.

> **Printer-control action**  
> Pause and Resume require confirmation. Use them only when you understand the current print state.

## 3.4. Configuration Backup

V2.3.0 does not use SFTP. Backup runs over a normal SSH exec channel and TAR stream, avoiding the K2 Plus SFTP-subsystem stall observed during testing.

12. Choose a local Backup folder.

13. Keep `Config path = /mnt/UDISK/printer_data/config` when using the canonical K2 Plus location.

14. Click Create ZIP Backup and confirm the sensitive-data warning.

15. Follow the stages and progress bar.

16. After verification, a standard ZIP is published. During the operation the file exists only as `.zip.partial`.

SSH → config-root check → find/du inventory → TAR over SSH → local ZIP → ZIP verify → atomic rename

| **Stage**         | **Operation**                                                          |
|-------------------|------------------------------------------------------------------------|
| SSH connection    | A regular SSH session is opened.                                       |
| Config-root check | The selected remote directory is checked.                              |
| Inventory         | `find`/`du` estimate file count, directory count and size.         |
| TAR over SSH      | Remote `tar` or `busybox tar` reads the config and streams stdout. |
| Local ZIP         | The TAR stream is safely parsed and written into ZIP.                  |
| ZIP verify        | ZIP integrity and manifest are checked before atomic finalization.     |

Safety limits: 5000 files, 1000 directories and 64 MiB of source data. Absolute/traversal TAR paths are rejected; symlinks are not dereferenced.

> **Backups may contain secrets**  
> `printer_data/config` may include passwords, network parameters, keys or other sensitive configuration. Do not publish a Backup unless it has been separately sanitized.

Cancel closes the active SSH channel/client, releases the GUI, and invalidates callbacks from the cancelled Backup run.

## 3.5. SSH key management

17. Choose a key folder and key name.

18. Generate key creates a local RSA-3072 key pair.

19. Generate + install adds the public key to `~/.ssh/authorized_keys` after confirmation, then verifies login using the new private key.

20. Install public key uses an existing private key and the adjacent `<private>.pub` file.

> **Important**  
> The private key stays local. Only the public key is installed. Public-key installation is a printer write and requires explicit confirmation.

# 4. Log tab

The Log tab displays the accumulated console state for the current session. It supports:

- copy selected text;
- copy all text;
- save the accumulated console to a separate snapshot file;
- clear the visible view without deleting the already written main log file.

`console_snapshot_K2_Plus_20260925_010205_044+0500_20260925_011530_212+0500.log`

The first snapshot timestamp marks the beginning of the accumulated console session; the second marks snapshot creation.

# 5. Automatic file names

| **Artifact** | **Pattern**                                                                   |
|--------------|-------------------------------------------------------------------------------|
| Main log     | `log_<printer>_<full_timestamp>.log`                                  |
| Snapshot     | `console_snapshot_<printer>_<start_timestamp>_<end_timestamp>.log` |
| Backup       | `backup_<printer>_<full_timestamp>.zip`                               |

Printer names are sanitized before being inserted into file names.

# 6. Persistent settings

Settings are stored under `%LOCALAPPDATA%\FDM_AI_Lab\K2_Plus_Console_Logger\settings.json`.

| **Data**                                                    | **Persisted?**                              |
|-------------------------------------------------------------|---------------------------------------------|
| Language, printer name, log/Backup/key folders, config path | Yes                                         |
| IP/hostname, Moonraker/SSH ports, SSH user, key path        | Only when Remember connection is enabled    |
| SSH password                                                | No                                          |
| Console content                                             | Only in explicitly saved log/snapshot files |

# 7. Troubleshooting

| **Symptom**               | **Check**                                                                                                             |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------|
| Moonraker FAIL            | IP/hostname, port 7125, network path and Moonraker availability.                                                      |
| SSH FAIL                  | Port 22, login/password, private key and SSH access on the printer.                                                   |
| Config root not found     | Canonical `/mnt/UDISK/printer_data/config` or a manually entered absolute remote path.                              |
| Backup timeout/stall      | Check current stage; Cancel should close the active channel. Verify regular SSH and `tar`/`busybox` availability. |
| Public-key install FAIL   | Check password authentication, write access to `~/.ssh`, and the `.pub` file next to the private key.             |
| Pause/Resume does nothing | Verify `print_stats.state`; control is only sent for `printing` or `paused`.                                    |

# 8. Advanced notes

## 8.1. Transport split

- Moonraker REST: connectivity, `gcode_store` logger, Pause/Resume.
- Regular SSH: connectivity, configuration Backup, public-key installation.
- SFTP is not used by the V2.3.0 Backup path.

## 8.2. Backup security model

The remote side performs read-only directory checks, `find`/`du`, and `tar -cf -`. No remote archive is created. The local side validates TAR member names and rejects absolute paths or `..`; regular files are written under `config/…`; symlinks are recorded in the manifest but are not dereferenced.

## 8.3. Public source policy

Python source is published for audit and development. The released EXE is intended for normal use. The project's internal build/compilation block is intentionally excluded from the public GitHub transfer package.

> **Hardware acceptance**  
> This guide documents V2.3.0 behavior. A function should only be marked hardware-proven after target K2 Plus validation. Source self-tests are not a substitute for physical acceptance.

# 9. Quick workflow

1. Launch the EXE.

2. Enter the K2 Plus IP address and run Connection test.

3. Confirm PASS for the transports required by your task.

4. Choose the log folder and start Logger.

5. Reproduce the print or diagnostic event.

6. Save a snapshot from the Log tab if needed.

7. Create a private ZIP Backup when required.

8. Stop Logger and retain the resulting artifacts.

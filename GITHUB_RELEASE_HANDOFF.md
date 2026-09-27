# GitHub publication HANDOFF — K2 Plus Console Logger V2.3.0

## Canonical public content

Publish the Python source and Markdown documentation as the source/documentation basis for the repository.

The Python source is intentionally public:
- `src/k2_plus_console_logger.py`

The two user manuals are published as Markdown:
- `README_RU.md`
- `README_ENG.md`

The original Word/DOCX manuals are preparation sources and are **not** part of the GitHub publication scope.

The compiled Windows EXE is intentionally distributed as a GitHub Release asset and must be supplied separately by the user:
- `K2PlusConsoleLogger.exe`

## Explicitly excluded

Do NOT publish or reconstruct the internal compilation block:
- `BUILD_ONEFILE_WINDOWS.cmd`
- PyInstaller spec/build scripts
- internal build environment / CI build recipe
- local build logs and evidence artifacts

Do not create a public compilation workflow unless the user separately changes this policy.

Do not publish the DOCX manuals in the repository or Release assets unless the user separately changes this policy.

## Release identity

Product: Creality K2 Plus Console Logger by FDM AI Lab
Version: V2.3.0

Suggested tag: `v2.3.0`

Suggested release title:
`Creality K2 Plus Console Logger by FDM AI Lab V2.3.0`

Release asset:
`K2PlusConsoleLogger.exe`

## Privacy / security gate before PUBLIC publication

Do not include:
- real printer IP/hostname, MAC/VLAN or private network topology;
- real `settings.json`;
- logs, console snapshots or configuration backups;
- private/public SSH key files;
- user home paths or machine-specific paths;
- tokens, cookies, API keys or other credentials.

The source intentionally contains vendor/default credentials `root / creality_2024` as a product default. Treat them as documented vendor/default values, not as a personal secret.

Configuration Backup archives are private by default because printer config can contain credentials and network data.

## Acceptance wording

Do not describe target-hardware behavior as PROVEN unless it was explicitly verified on the target K2 Plus. Source self-tests and static QA are not physical hardware acceptance.

## Project license decision

Owner decision for V2.3.0: **No project LICENSE**.

Do not create a `LICENSE` file or assign a project-wide open-source license unless the owner separately changes this decision. Third-party software remains governed by its own license terms.

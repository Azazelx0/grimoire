# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.3] - 2026-03-12
### Fixed
- Fixed the interactive Default Credentials menu where selecting "List all vendors" simply printed text and quit. It now opens an interactive, searchable menu allowing the user to select a vendor to view its specific credentials.

## [2.2.2] - 2026-03-12
### Changed
- Fixed leftover `alecto` references in wizard export defaults and example scripts after transitioning to the dynamic Default Credentials module.

## [2.2.1] - 2026-03-12
### Fixed
- Fixed an issue where accessing the Default Credentials module from the interactive wizard menu would crash (`NameError`) due to an orphaned function reference during migration.

## [2.2.0] - 2026-03-12
### Added
- **Dynamic Default Credentials**: Migrated the static `alecto.py` database to a dynamic module (`default_creds.py`) that fetches records from GitHub/online cheat sheets.
- Offline Fallback caching to elegantly handle network drops and air-gapped scenarios in the Default Credentials module.
- New `--default-creds` CLI flag and interactive `defcreds` REPL command replacing the legacy `--alecto` commands.

### Changed
- Refactored `wizard.py` default credential choices to reflect the new dynamic module naming.
- Cleaned up obsolete static Alecto references from the codebase (`alecto.py`).

## [2.1.0] - 2026-03-12
### Added
- **OSINT Scraper Expansion**: Added scraping support for Instagram, X (Twitter), and LinkedIn to extract contextual keywords without requiring an API key. 
- **Interactive Post-Processing Menu**: The `grimoire` command loop now has a robust post-generation menu to dynamically apply mutations, passwords policies, deduping, and wordlist analysis without dropping back to the shell.
- **`grimoire update` Command**: A built-in self-updater (`updater.py`) capable of pulling the latest GitHub repository commits and reinstalling the CLI seamlessly.
- **Chain Builder Wizard**: Interactively design mutation chains directly from the main menu.
- **Hashcat Rule Parsing**: Added Hashcat `.rule` support to the Crawl Wizard.

### Changed
- Refactored `cli.py` to fix structural block issues and delineate between interactive wizards vs CLI flags cleanly.
- Overhauled `wizard.py` to support shared interactive workflows (Mutations, Policies, Export format selection).

### Removed
- Unused duplicate handler functions during codebase synchronization.

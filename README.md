# Python Generator for Laravel + Vue 3 Template

CLI script to generate a new project from:

- Template repo: `https://github.com/okazakikyo/Base-Vue-Vite-Laravel.git`
- Stack: Laravel + Vue 3 + Vite

## Prerequisites

Supported environments:

- macOS
- Linux
- Windows 10/11 (`PowerShell` or `CMD`)

## Requirements Before Running The Script

Install and verify these tools first:

- Python `3.9+`
- Git `2.30+`
- PHP `8.2+`
- Composer `2+`
- Node.js `18+`
- Database:
  - `MySQL 8+` if your project uses MySQL
  - or `SQLite 3+` if you want lightweight local development
- One JavaScript package manager:
  - `npm` `9+` (default)
  - or `pnpm`
  - or `yarn`

Recommended checks:

```bash
python3 --version
git --version
php --version
composer --version
node --version
npm --version
```

Database checks:

```bash
mysql --version
sqlite3 --version
```

Windows:

```powershell
py --version
git --version
php --version
composer --version
node --version
npm --version
```

For Laravel setup to work smoothly, make sure:

- PHP CLI is callable directly from terminal
- Composer is available in `PATH`
- Node.js and the selected JS package manager are available in `PATH`
- MySQL server is installed and running if you use MySQL
- or SQLite is installed if you use SQLite
- The template repo can be cloned from GitHub
- You have write permission to the `--target-dir`

Required commands in `PATH`:

- `git`
- `php`
- `composer`
- `node`
- One JS package manager: `npm` (default), `pnpm`, or `yarn`

## Quick Start

```bash
python3 generate_template.py my-project
```

Windows:

```powershell
py generate_template.py my-project
```

This will:

1. Clone template repo (default branch `main`)
2. Create `./my-project`
3. Remove template git history (`.git`)
4. Update project metadata (`.env`, `composer.json`, `package.json`, `README.md` if present)
5. Run full setup (`composer install`, `npm install`, `php artisan key:generate`)

## CLI Usage

```bash
python3 generate_template.py <project_name> [options]
```

Options:

- `--target-dir <path>`: parent directory for new project (default: current directory)
- `--repo <url>`: template repository URL
- `--branch <name>`: template branch (default: `main`)
- `--js-pm <npm|pnpm|yarn>`: JavaScript package manager (default: `npm`)
- `--with-migrate`: run `php artisan migrate --force` after setup
- `--no-install`: skip `composer install` and JS install
- `--dry-run`: print actions only, do not execute
- `--force`: remove target folder if it exists

## Common Commands to Run Source

Inside the generated project:

```bash
php artisan serve
npm run dev
```

If using `pnpm` or `yarn`, replace `npm run dev` accordingly.

## Example Commands

```bash
# Basic
python3 generate_template.py demo-app

# Use pnpm and run migration
python3 generate_template.py demo-app --js-pm pnpm --with-migrate

# Preview without executing
python3 generate_template.py demo-app --dry-run

# Overwrite existing target folder
python3 generate_template.py demo-app --force
```

Windows PowerShell examples:

```powershell
# Basic
py generate_template.py demo-app

# Use pnpm and run migration
py generate_template.py demo-app --js-pm pnpm --with-migrate

# Preview without executing
py generate_template.py demo-app --dry-run
```

## Exit Codes

- `0`: success
- `1`: business/runtime error (invalid name, target exists, command failure)
- `2`: missing dependency (`git/php/composer/node/npm/...`)

## Troubleshooting

- `Missing required command(s)`:
   - Install missing tools and confirm with `which <command>`.
   - On Windows, confirm with `where <command>`.

- `composer install` fails:
   - Check PHP/Composer version compatibility and required PHP extensions.

- JS install fails:
   - Verify Node.js version and lockfile compatibility.

- `php artisan key:generate` fails:
   - Ensure `.env` exists (script copies from `.env.example` when available).

- Permission issues:
   - Ensure you have write permissions on `--target-dir`.
   - On Windows, close any Explorer/editor window that is locking the target folder before using `--force`.

## Notes

- Works on macOS/Linux/Windows.
- On Windows, the script resolves common wrappers such as `composer.bat`, `npm.cmd`, `pnpm.cmd`, and `yarn.cmd` automatically when they are available in `PATH`.
- Git history from template is detached (new project does not keep template `.git`).

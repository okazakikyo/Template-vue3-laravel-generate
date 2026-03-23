# Python Generator for Laravel + Vue 3 Template

CLI script to generate a new project from:

- Template repo: `https://github.com/okazakikyo/Base-Vue-Vite-Laravel.git`
- Stack: Laravel + Vue 3 + Vite

## Prerequisites

macOS/Linux environment with commands in `PATH`:

- `git`
- `php`
- `composer`
- `node`
- One JS package manager: `npm` (default), `pnpm`, or `yarn`

## Quick Start

```bash
python3 generate_template.py my-project
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

## Exit Codes

- `0`: success
- `1`: business/runtime error (invalid name, target exists, command failure)
- `2`: missing dependency (`git/php/composer/node/npm/...`)

## Troubleshooting

- `Missing required command(s)`:
   - Install missing tools and confirm with `which <command>`.

- `composer install` fails:
   - Check PHP/Composer version compatibility and required PHP extensions.

- JS install fails:
   - Verify Node.js version and lockfile compatibility.

- `php artisan key:generate` fails:
   - Ensure `.env` exists (script copies from `.env.example` when available).

- Permission issues:
   - Ensure you have write permissions on `--target-dir`.

## Notes

- Designed for macOS/Linux.
- Windows support is not prioritized in this initial version.
- Git history from template is detached (new project does not keep template `.git`).

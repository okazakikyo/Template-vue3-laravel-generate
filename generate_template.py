#!/usr/bin/env python3
"""Generate a Laravel + Vue 3 project from a GitHub template repository."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterable

DEFAULT_REPO = "https://github.com/okazakikyo/Base-Vue-Vite-Laravel.git"
DEFAULT_BRANCH = "main"
VALID_JS_PMS = ("npm", "pnpm", "yarn")


class AppError(Exception):
    """Business-logic error."""


class MissingDependencyError(Exception):
    """Required command not available."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Laravel + Vue project from a GitHub template."
    )
    parser.add_argument("project_name", help="New project directory name.")
    parser.add_argument(
        "--target-dir",
        default=".",
        help="Directory where the new project will be created (default: current dir).",
    )
    parser.add_argument("--repo", default=DEFAULT_REPO, help="Template repository URL.")
    parser.add_argument(
        "--branch", default=DEFAULT_BRANCH, help="Template branch to clone."
    )
    parser.add_argument(
        "--js-pm",
        choices=VALID_JS_PMS,
        default="npm",
        help="JavaScript package manager to use.",
    )
    parser.add_argument(
        "--with-migrate",
        action="store_true",
        help="Run 'php artisan migrate --force' after setup.",
    )
    parser.add_argument(
        "--no-install",
        action="store_true",
        help="Skip composer install and JS package install.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned actions without executing them.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Remove target directory if it already exists.",
    )
    return parser.parse_args()


def log(msg: str) -> None:
    print(f"[INFO] {msg}")


def warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def run_cmd(cmd: list[str], cwd: Path | None = None, dry_run: bool = False) -> None:
    pretty = " ".join(cmd)
    where = f" (cwd={cwd})" if cwd else ""
    log(f"Run: {pretty}{where}")
    if dry_run:
        return

    try:
        subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True, text=True)
    except subprocess.CalledProcessError as exc:
        raise AppError(
            f"Command failed: {pretty}\n"
            "Please check your environment and dependencies, then try again."
        ) from exc


def validate_project_name(name: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
        raise AppError(
            "Invalid project_name. Use only letters, numbers, '-' or '_'."
        )


def normalize_kebab_name(name: str) -> str:
    normalized = name.lower().replace("_", "-")
    normalized = re.sub(r"-+", "-", normalized).strip("-")
    if not normalized:
        raise AppError("project_name must contain at least one alphanumeric character.")
    return normalized


def check_dependencies(js_pm: str, no_install: bool) -> None:
    required = ["git", "php"]
    if not no_install:
        required.extend(["composer", "node", js_pm])

    missing = [cmd for cmd in required if shutil.which(cmd) is None]
    if missing:
        missing_str = ", ".join(sorted(set(missing)))
        raise MissingDependencyError(
            f"Missing required command(s): {missing_str}. Install them and retry."
        )


def ensure_target_dir(target_project_dir: Path, force: bool, dry_run: bool) -> None:
    if target_project_dir.exists():
        if not force:
            raise AppError(
                f"Target directory already exists: {target_project_dir}. Use --force to overwrite."
            )
        log(f"Target exists and --force is set: removing {target_project_dir}")
        if not dry_run:
            shutil.rmtree(target_project_dir)

    log(f"Creating project directory: {target_project_dir}")
    if not dry_run:
        target_project_dir.mkdir(parents=True, exist_ok=True)


def copy_template(repo: str, branch: str, project_dir: Path, dry_run: bool) -> None:
    with tempfile.TemporaryDirectory(prefix="tpl-vue-laravel-") as temp_dir:
        tmp_path = Path(temp_dir)
        clone_dir = tmp_path / "template"

        run_cmd(["git", "clone", "--depth", "1", "--branch", branch, repo, str(clone_dir)], dry_run=dry_run)

        if dry_run:
            log(f"Would copy template content from {clone_dir} -> {project_dir}")
            log("Would detach git history by removing .git")
            return

        for item in clone_dir.iterdir():
            destination = project_dir / item.name
            if item.name == ".git":
                continue
            if item.is_dir():
                shutil.copytree(item, destination, dirs_exist_ok=True)
            else:
                shutil.copy2(item, destination)

        git_dir = project_dir / ".git"
        if git_dir.exists():
            shutil.rmtree(git_dir)


def update_env_app_name(env_path: Path, project_name: str, dry_run: bool) -> None:
    quoted_name = f'"{project_name}"'
    content = env_path.read_text(encoding="utf-8")
    if re.search(r"^APP_NAME=", content, flags=re.MULTILINE):
        new_content = re.sub(
            r"^APP_NAME=.*$", f"APP_NAME={quoted_name}", content, flags=re.MULTILINE
        )
    else:
        new_content = f"APP_NAME={quoted_name}\n{content}"

    if dry_run:
        log(f"Would update APP_NAME in {env_path}")
        return
    env_path.write_text(new_content, encoding="utf-8")


def update_json_name(json_path: Path, value: str, dry_run: bool) -> None:
    raw = json_path.read_text(encoding="utf-8")
    data = json.loads(raw)
    data["name"] = value
    if dry_run:
        log(f"Would update name in {json_path} -> {value}")
        return
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def maybe_update_readme(readme_path: Path, project_name: str, dry_run: bool) -> None:
    if not readme_path.exists():
        return
    content = readme_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    if not lines:
        return

    if lines[0].startswith("#"):
        lines[0] = f"# {project_name}"
    else:
        lines.insert(0, f"# {project_name}")

    if dry_run:
        log(f"Would update first heading in {readme_path}")
        return
    readme_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def ensure_env_file(project_dir: Path, dry_run: bool) -> Path | None:
    env_path = project_dir / ".env"
    if env_path.exists():
        return env_path

    env_example = project_dir / ".env.example"
    if not env_example.exists():
        warn("Neither .env nor .env.example exists; skipping APP_NAME update and key generation.")
        return None

    log(".env not found. Copying .env.example -> .env")
    if not dry_run:
        shutil.copy2(env_example, env_path)
    return env_path


def update_project_metadata(project_dir: Path, project_name: str, dry_run: bool) -> None:
    kebab_name = normalize_kebab_name(project_name)

    if dry_run:
        log("Would ensure .env exists (copy from .env.example if missing)")
        log(f'Would set APP_NAME="{project_name}" in .env')
        log(f"Would update composer.json name -> laravel/{kebab_name}")
        log(f"Would update package.json name -> {kebab_name}")
        log("Would update README.md first heading to project name if file exists")
        return

    env_path = ensure_env_file(project_dir, dry_run)
    if env_path is not None:
        if env_path.exists():
            update_env_app_name(env_path, project_name, dry_run)

    composer_path = project_dir / "composer.json"
    if composer_path.exists():
        update_json_name(composer_path, f"laravel/{kebab_name}", dry_run)
    else:
        warn("composer.json not found; skipping composer package name update.")

    package_path = project_dir / "package.json"
    if package_path.exists():
        update_json_name(package_path, kebab_name, dry_run)
    else:
        warn("package.json not found; skipping JS package name update.")

    maybe_update_readme(project_dir / "README.md", project_name, dry_run)


def setup_project(
    project_dir: Path,
    js_pm: str,
    no_install: bool,
    with_migrate: bool,
    dry_run: bool,
) -> None:
    if not no_install:
        run_cmd(["composer", "install"], cwd=project_dir, dry_run=dry_run)
        run_cmd([js_pm, "install"], cwd=project_dir, dry_run=dry_run)

    env_exists = (project_dir / ".env").exists() or dry_run
    if env_exists:
        run_cmd(["php", "artisan", "key:generate"], cwd=project_dir, dry_run=dry_run)
        if with_migrate:
            run_cmd(["php", "artisan", "migrate", "--force"], cwd=project_dir, dry_run=dry_run)
    else:
        warn("Skipping artisan commands because .env is missing.")


def print_next_steps(project_name: str, js_pm: str) -> None:
    print("\n=== Next steps ===")
    print(f"cd {project_name}")
    print("php artisan serve")
    print(f"{js_pm} run dev")


def run(argv: Iterable[str] | None = None) -> int:
    _ = argv
    args = parse_args()
    validate_project_name(args.project_name)

    target_dir = Path(args.target_dir).expanduser().resolve()
    project_dir = target_dir / args.project_name

    check_dependencies(args.js_pm, args.no_install)
    ensure_target_dir(project_dir, force=args.force, dry_run=args.dry_run)
    copy_template(args.repo, args.branch, project_dir, dry_run=args.dry_run)
    update_project_metadata(project_dir, args.project_name, dry_run=args.dry_run)
    setup_project(
        project_dir,
        js_pm=args.js_pm,
        no_install=args.no_install,
        with_migrate=args.with_migrate,
        dry_run=args.dry_run,
    )
    print_next_steps(args.project_name, args.js_pm)
    return 0


def main() -> None:
    try:
        code = run()
    except MissingDependencyError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(2)
    except AppError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[ERROR] Interrupted by user.", file=sys.stderr)
        sys.exit(1)

    sys.exit(code)


if __name__ == "__main__":
    main()

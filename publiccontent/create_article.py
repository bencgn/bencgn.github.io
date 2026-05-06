#!/usr/bin/env python3
"""Create a Public Content article folder and sync content.json."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "content.json"
ALLOWED_CATEGORIES = ("Kỹ Năng", "Sản Phẩm", "Tool", "Sáng Tạo")
DEFAULT_IMAGE = "assets/images/article-interior.svg"


for stream in (sys.stdin, sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")


def prompt_missing(label: str, current: str | None, default: str | None = None) -> str:
    if current:
        return current.strip()
    if default is not None and not sys.stdin.isatty():
        return default

    suffix = f" [{default}]" if default else ""
    try:
        value = input(f"{label}{suffix}: ").strip()
    except EOFError:
        if default is not None:
            return default
        raise SystemExit(f"Missing required value: {label}") from None
    if value:
        return value
    if default is not None:
        return default
    raise SystemExit(f"Missing required value: {label}")


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        return {"items": []}

    with MANIFEST_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data.get("items"), list):
        data["items"] = []

    return data


def write_manifest(data: dict) -> None:
    with MANIFEST_PATH.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def validate_date(value: str) -> str:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise SystemExit("Date must use YYYY-MM-DD, for example 2026-05-06.") from exc
    return value


def validate_category(value: str) -> str:
    if value not in ALLOWED_CATEGORIES:
        choices = ", ".join(ALLOWED_CATEGORIES)
        raise SystemExit(f"Category must be one of: {choices}")
    return value


def next_folder_code(items: list[dict]) -> str:
    numbers = []

    for item in items:
        folder = str(item.get("folder", ""))
        match = re.fullmatch(r"conten(1+)", folder)
        if match:
            numbers.append(len(match.group(1)))

    for path in ROOT.iterdir():
        if not path.is_dir():
            continue
        match = re.fullmatch(r"conten(1+)", path.name)
        if match:
            numbers.append(len(match.group(1)))

    return "conten" + ("1" * (max(numbers, default=0) + 1))


def article_html(title: str, title_vi: str, category: str, folder: str, article_date: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="vi">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title_vi or title}</title>
  </head>
  <body>
    <main>
      <p>{category} · {article_date}</p>
      <h1>{title_vi or title}</h1>
      <p>Folder code: {folder}</p>
      <article>
        <p>Viết nội dung bài ở đây hoặc cập nhật file content.md.</p>
      </article>
      <p><a href="../../#articles">Back to Public Content</a></p>
    </main>
  </body>
</html>
"""


def article_markdown(title: str, title_vi: str, category: str, folder: str, article_date: str) -> str:
    return f"""# {title_vi or title}

- Title EN: {title}
- Folder: {folder}
- Date: {article_date}
- Category: {category}

Viết nội dung bài ở đây.
"""


def create_article(args: argparse.Namespace) -> None:
    manifest = load_manifest()
    items = manifest["items"]

    folder = args.folder or next_folder_code(items)
    folder_path = ROOT / folder

    if folder_path.exists() and not args.force:
        raise SystemExit(f"Folder already exists: {folder}. Use --force to update files.")

    title = prompt_missing("Title EN", args.title)
    title_vi = prompt_missing("Title VI", args.title_vi, title)
    article_date = validate_date(prompt_missing("Date YYYY-MM-DD", args.date, date.today().isoformat()))

    print("Categories:")
    for index, category_name in enumerate(ALLOWED_CATEGORIES, start=1):
        print(f"  {index}. {category_name}")

    category_value = args.category
    if category_value and category_value.isdigit():
        category_index = int(category_value) - 1
        if 0 <= category_index < len(ALLOWED_CATEGORIES):
            category_value = ALLOWED_CATEGORIES[category_index]

    category_value = validate_category(prompt_missing("Category", category_value, ALLOWED_CATEGORIES[0]))
    image = prompt_missing("Image path", args.image, DEFAULT_IMAGE)

    item = {
        "title": title,
        "titleVi": title_vi,
        "folder": folder,
        "date": article_date,
        "category": category_value,
        "image": image,
    }

    existing_index = next((index for index, row in enumerate(items) if row.get("folder") == folder), None)
    if existing_index is None:
        items.append(item)
    else:
        items[existing_index] = item

    items.sort(key=lambda row: row.get("date", ""), reverse=True)

    if args.dry_run:
        print(json.dumps(item, ensure_ascii=False, indent=2))
        print(f"Dry run only. No files changed. Target folder: {folder_path}")
        return

    folder_path.mkdir(parents=True, exist_ok=True)
    (folder_path / "index.html").write_text(
        article_html(title, title_vi, category_value, folder, article_date),
        encoding="utf-8",
        newline="\n",
    )
    (folder_path / "content.md").write_text(
        article_markdown(title, title_vi, category_value, folder, article_date),
        encoding="utf-8",
        newline="\n",
    )
    write_manifest(manifest)

    print(f"Created article: {folder}")
    print(f"Updated manifest: {MANIFEST_PATH}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a folder under publiccontent and sync it into content.json."
    )
    parser.add_argument("--title", help="English title.")
    parser.add_argument("--title-vi", help="Vietnamese title.")
    parser.add_argument("--folder", help="Folder code, for example conten11111. Auto-generated if omitted.")
    parser.add_argument("--date", help="Publish date in YYYY-MM-DD format. Defaults to today.")
    parser.add_argument("--category", help="Category name or number: Kỹ Năng, Sản Phẩm, Tool, Sáng Tạo.")
    parser.add_argument("--image", help=f"Card image path. Defaults to {DEFAULT_IMAGE}.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing article folder and manifest item.")
    parser.add_argument("--dry-run", action="store_true", help="Print the new item without writing files.")
    return parser


if __name__ == "__main__":
    create_article(build_parser().parse_args())

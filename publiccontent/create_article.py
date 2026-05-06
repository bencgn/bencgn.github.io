#!/usr/bin/env python3
"""GUI/CLI tool to create Public Content articles and sync content.json."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "content.json"
ALLOWED_CATEGORIES = ("Kỹ Năng", "Sản Phẩm", "Tool", "Sáng Tạo")
DEFAULT_IMAGE = "assets/images/article-interior.svg"


for stream in (sys.stdin, sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")


@dataclass
class ArticleInput:
    title: str
    title_vi: str
    folder: str
    article_date: str
    category: str
    image: str
    force: bool = False


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
        raise ValueError("Ngày phải theo định dạng YYYY-MM-DD, ví dụ 2026-05-06.") from exc
    return value


def normalize_category(value: str) -> str:
    value = value.strip()
    if value.isdigit():
        category_index = int(value) - 1
        if 0 <= category_index < len(ALLOWED_CATEGORIES):
            value = ALLOWED_CATEGORIES[category_index]

    if value not in ALLOWED_CATEGORIES:
        choices = ", ".join(ALLOWED_CATEGORIES)
        raise ValueError(f"Thể loại chỉ được là: {choices}")
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
    display_title = title_vi or title
    return f"""<!DOCTYPE html>
<html lang="vi">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{display_title}</title>
  </head>
  <body>
    <main>
      <p>{category} · {article_date}</p>
      <h1>{display_title}</h1>
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


def build_article_input(
    title: str,
    title_vi: str,
    folder: str | None,
    article_date: str,
    category: str,
    image: str,
    force: bool = False,
) -> ArticleInput:
    manifest = load_manifest()
    items = manifest["items"]
    safe_title = title.strip()
    safe_title_vi = title_vi.strip() or safe_title
    safe_folder = (folder or next_folder_code(items)).strip()

    if not safe_title:
        raise ValueError("Cần nhập Title EN.")
    if not re.fullmatch(r"conten1+", safe_folder):
        raise ValueError("Folder phải có dạng conten1, conten11, conten111...")

    return ArticleInput(
        title=safe_title,
        title_vi=safe_title_vi,
        folder=safe_folder,
        article_date=validate_date(article_date.strip()),
        category=normalize_category(category),
        image=(image.strip() or DEFAULT_IMAGE),
        force=force,
    )


def save_article(article: ArticleInput, dry_run: bool = False) -> tuple[dict, Path]:
    manifest = load_manifest()
    items = manifest["items"]
    folder_path = ROOT / article.folder

    if folder_path.exists() and not article.force:
        raise FileExistsError(f"Folder đã tồn tại: {article.folder}. Bật Force overwrite để ghi đè.")

    item = {
        "title": article.title,
        "titleVi": article.title_vi,
        "folder": article.folder,
        "date": article.article_date,
        "category": article.category,
        "image": article.image,
    }

    existing_index = next((index for index, row in enumerate(items) if row.get("folder") == article.folder), None)
    if existing_index is None:
        items.append(item)
    else:
        items[existing_index] = item

    items.sort(key=lambda row: row.get("date", ""), reverse=True)

    if dry_run:
        return item, folder_path

    folder_path.mkdir(parents=True, exist_ok=True)
    (folder_path / "index.html").write_text(
        article_html(article.title, article.title_vi, article.category, article.folder, article.article_date),
        encoding="utf-8",
        newline="\n",
    )
    (folder_path / "content.md").write_text(
        article_markdown(article.title, article.title_vi, article.category, article.folder, article.article_date),
        encoding="utf-8",
        newline="\n",
    )
    write_manifest(manifest)

    return item, folder_path


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


def run_cli(args: argparse.Namespace) -> None:
    manifest = load_manifest()
    default_folder = next_folder_code(manifest["items"])

    print("Categories:")
    for index, category_name in enumerate(ALLOWED_CATEGORIES, start=1):
        print(f"  {index}. {category_name}")

    try:
        article = build_article_input(
            title=prompt_missing("Title EN", args.title),
            title_vi=prompt_missing("Title VI", args.title_vi, args.title or ""),
            folder=args.folder or default_folder,
            article_date=prompt_missing("Date YYYY-MM-DD", args.date, date.today().isoformat()),
            category=prompt_missing("Category", args.category, ALLOWED_CATEGORIES[0]),
            image=prompt_missing("Image path", args.image, DEFAULT_IMAGE),
            force=args.force,
        )
        item, folder_path = save_article(article, dry_run=args.dry_run)
    except (ValueError, FileExistsError) as exc:
        raise SystemExit(str(exc)) from exc

    if args.dry_run:
        print(json.dumps(item, ensure_ascii=False, indent=2))
        print(f"Dry run only. No files changed. Target folder: {folder_path}")
        return

    print(f"Created article: {article.folder}")
    print(f"Updated manifest: {MANIFEST_PATH}")


def run_gui() -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    root = tk.Tk()
    root.title("BenCGN Public Content")
    root.geometry("720x560")
    root.minsize(620, 500)

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TFrame", background="#2b0603")
    style.configure("Panel.TFrame", background="#3a0a05")
    style.configure("TLabel", background="#3a0a05", foreground="#f6dfb9", font=("Segoe UI", 10))
    style.configure("Title.TLabel", background="#2b0603", foreground="#f1d69d", font=("Segoe UI", 18, "bold"))
    style.configure("Hint.TLabel", background="#3a0a05", foreground="#c79d74", font=("Segoe UI", 9))
    style.configure("TButton", font=("Segoe UI", 10, "bold"))
    style.configure("Accent.TButton", background="#a62b1d", foreground="#f6dfb9")

    shell = ttk.Frame(root, padding=22)
    shell.pack(fill="both", expand=True)

    ttk.Label(shell, text="Create Public Content", style="Title.TLabel").pack(anchor="w")
    ttk.Label(
        shell,
        text="Tạo folder bài viết và đồng bộ publiccontent/content.json",
        style="Title.TLabel",
        font=("Segoe UI", 10),
    ).pack(anchor="w", pady=(2, 18))

    panel = ttk.Frame(shell, style="Panel.TFrame", padding=18)
    panel.pack(fill="both", expand=True)
    panel.columnconfigure(1, weight=1)

    manifest = load_manifest()
    folder_var = tk.StringVar(value=next_folder_code(manifest["items"]))
    title_var = tk.StringVar()
    title_vi_var = tk.StringVar()
    date_var = tk.StringVar(value=date.today().isoformat())
    category_var = tk.StringVar(value=ALLOWED_CATEGORIES[0])
    image_var = tk.StringVar(value=DEFAULT_IMAGE)
    force_var = tk.BooleanVar(value=False)
    status_var = tk.StringVar(value="Sẵn sàng tạo bài mới.")

    fields = [
        ("Title EN", title_var),
        ("Title VI", title_vi_var),
        ("Folder", folder_var),
        ("Date", date_var),
    ]

    for row_index, (label, variable) in enumerate(fields):
        ttk.Label(panel, text=label).grid(row=row_index, column=0, sticky="w", padx=(0, 14), pady=8)
        ttk.Entry(panel, textvariable=variable).grid(row=row_index, column=1, sticky="ew", pady=8)

    ttk.Label(panel, text="Category").grid(row=4, column=0, sticky="w", padx=(0, 14), pady=8)
    ttk.Combobox(panel, textvariable=category_var, values=ALLOWED_CATEGORIES, state="readonly").grid(
        row=4, column=1, sticky="ew", pady=8
    )

    ttk.Label(panel, text="Image").grid(row=5, column=0, sticky="w", padx=(0, 14), pady=8)
    image_row = ttk.Frame(panel, style="Panel.TFrame")
    image_row.grid(row=5, column=1, sticky="ew", pady=8)
    image_row.columnconfigure(0, weight=1)
    ttk.Entry(image_row, textvariable=image_var).grid(row=0, column=0, sticky="ew")

    def browse_image() -> None:
        path = filedialog.askopenfilename(
            title="Choose image",
            filetypes=(("Image files", "*.svg *.png *.jpg *.jpeg *.webp"), ("All files", "*.*")),
        )
        if not path:
            return
        try:
            image_var.set(Path(path).resolve().relative_to(ROOT.parent).as_posix())
        except ValueError:
            image_var.set(Path(path).as_posix())

    ttk.Button(image_row, text="Browse", command=browse_image).grid(row=0, column=1, padx=(8, 0))

    ttk.Checkbutton(panel, text="Force overwrite nếu folder đã tồn tại", variable=force_var).grid(
        row=6, column=1, sticky="w", pady=(6, 10)
    )

    ttk.Label(
        panel,
        text="Folder tự tăng theo dạng conten1, conten11, conten111...",
        style="Hint.TLabel",
    ).grid(row=7, column=1, sticky="w", pady=(0, 12))

    status_label = ttk.Label(panel, textvariable=status_var, style="Hint.TLabel", wraplength=520)
    status_label.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(8, 12))

    def reset_form() -> None:
        fresh_manifest = load_manifest()
        title_var.set("")
        title_vi_var.set("")
        folder_var.set(next_folder_code(fresh_manifest["items"]))
        date_var.set(date.today().isoformat())
        category_var.set(ALLOWED_CATEGORIES[0])
        image_var.set(DEFAULT_IMAGE)
        force_var.set(False)
        status_var.set("Sẵn sàng tạo bài mới.")

    def create_from_form() -> None:
        try:
            article = build_article_input(
                title=title_var.get(),
                title_vi=title_vi_var.get(),
                folder=folder_var.get(),
                article_date=date_var.get(),
                category=category_var.get(),
                image=image_var.get(),
                force=force_var.get(),
            )
            _, folder_path = save_article(article)
        except (ValueError, FileExistsError, OSError, json.JSONDecodeError) as exc:
            messagebox.showerror("Không tạo được bài", str(exc))
            status_var.set(f"Lỗi: {exc}")
            return

        status_var.set(f"Đã tạo {article.folder} và cập nhật content.json.")
        messagebox.showinfo("Đã tạo bài", f"Đã tạo bài tại:\n{folder_path}")
        reset_form()

    button_row = ttk.Frame(panel, style="Panel.TFrame")
    button_row.grid(row=9, column=1, sticky="e", pady=(8, 0))
    ttk.Button(button_row, text="Reset", command=reset_form).grid(row=0, column=0, padx=(0, 8))
    ttk.Button(button_row, text="Create Article", style="Accent.TButton", command=create_from_form).grid(row=0, column=1)

    root.mainloop()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a folder under publiccontent and sync it into content.json."
    )
    parser.add_argument("--gui", action="store_true", help="Open the desktop GUI app.")
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
    parsed_args = build_parser().parse_args()
    if parsed_args.gui or len(sys.argv) == 1:
        run_gui()
    else:
        run_cli(parsed_args)

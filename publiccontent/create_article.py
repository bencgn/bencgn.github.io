#!/usr/bin/env python3
"""GUI/CLI tool to create and edit Public Content articles."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "content.json"
ALLOWED_CATEGORIES = ("Kỹ Năng", "Sản Phẩm", "Tool", "Sáng Tạo")
CONTENT_TYPES = ("Bài Viết", "Link")
CONTENT_TYPE_VALUES = {
    "Bài Viết": "article",
    "Link": "link",
    "article": "article",
    "link": "link",
}
CONTENT_TYPE_LABELS = {
    "article": "Bài Viết",
    "link": "Link",
}
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
    content_type: str = "article"
    link_url: str = ""
    body: str = ""
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


def normalize_content_type(value: str) -> str:
    value = (value or "Bài Viết").strip()
    if value not in CONTENT_TYPE_VALUES:
        choices = ", ".join(CONTENT_TYPES)
        raise ValueError(f"Loại content chỉ được là: {choices}")
    return CONTENT_TYPE_VALUES[value]


def content_type_label(value: str) -> str:
    return CONTENT_TYPE_LABELS.get(value, "Bài Viết")


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


def default_article_body(title: str, title_vi: str, category: str, folder: str, article_date: str) -> str:
    return f"""# {title_vi or title}

- Title EN: {title}
- Folder: {folder}
- Date: {article_date}
- Category: {category}

Viết nội dung bài ở đây.
"""


def article_markdown(title: str, title_vi: str, category: str, folder: str, article_date: str, body: str = "") -> str:
    return body.strip() + "\n" if body.strip() else default_article_body(title, title_vi, category, folder, article_date)


def read_article_body(folder: str) -> str:
    path = ROOT / folder / "content.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def build_article_input(
    title: str,
    title_vi: str,
    folder: str | None,
    article_date: str,
    category: str,
    image: str,
    content_type: str = "Bài Viết",
    link_url: str = "",
    body: str = "",
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
        content_type=normalize_content_type(content_type),
        link_url=link_url.strip(),
        body=body,
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
        "contentType": article.content_type,
        "linkUrl": article.link_url,
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
        article_markdown(article.title, article.title_vi, article.category, article.folder, article.article_date, article.body),
        encoding="utf-8",
        newline="\n",
    )
    write_manifest(manifest)

    return item, folder_path


def delete_article(folder: str) -> Path:
    manifest = load_manifest()
    items = manifest["items"]
    safe_folder = folder.strip()

    if not re.fullmatch(r"conten1+", safe_folder):
        raise ValueError("Folder phải có dạng conten1, conten11, conten111...")

    folder_path = (ROOT / safe_folder).resolve()
    root_path = ROOT.resolve()

    if folder_path.parent != root_path:
        raise ValueError("Chỉ được xóa folder nằm trực tiếp trong publiccontent.")

    remaining_items = [item for item in items if item.get("folder") != safe_folder]
    if len(remaining_items) == len(items):
        raise ValueError(f"Không tìm thấy content trong manifest: {safe_folder}")

    manifest["items"] = remaining_items

    if folder_path.exists():
        if not folder_path.is_dir():
            raise ValueError(f"Đường dẫn không phải folder: {folder_path}")
        shutil.rmtree(folder_path)

    write_manifest(manifest)
    return folder_path


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
        body = ""
        if args.body_file:
            body = Path(args.body_file).read_text(encoding="utf-8")

        article = build_article_input(
            title=prompt_missing("Title EN", args.title),
            title_vi=prompt_missing("Title VI", args.title_vi, args.title or ""),
            folder=args.folder or default_folder,
            article_date=prompt_missing("Date YYYY-MM-DD", args.date, date.today().isoformat()),
            category=prompt_missing("Category", args.category, ALLOWED_CATEGORIES[0]),
            image=prompt_missing("Image path", args.image, DEFAULT_IMAGE),
            content_type=prompt_missing("Content type", args.content_type, CONTENT_TYPES[0]),
            link_url=args.link_url or "",
            body=body,
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
    root.geometry("980x620")
    root.minsize(860, 560)

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TFrame", background="#2b0603")
    style.configure("Panel.TFrame", background="#3a0a05")
    style.configure("TLabel", background="#3a0a05", foreground="#f6dfb9", font=("Segoe UI", 10))
    style.configure("Title.TLabel", background="#2b0603", foreground="#f1d69d", font=("Segoe UI", 18, "bold"))
    style.configure("Hint.TLabel", background="#3a0a05", foreground="#c79d74", font=("Segoe UI", 9))
    style.configure("TButton", font=("Segoe UI", 10, "bold"))
    style.configure("Accent.TButton", background="#a62b1d", foreground="#f6dfb9")
    style.configure("Treeview", rowheight=26, font=("Segoe UI", 9))
    style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    shell = ttk.Frame(root, padding=20)
    shell.pack(fill="both", expand=True)

    ttk.Label(shell, text="Public Content Manager", style="Title.TLabel").pack(anchor="w")
    ttk.Label(
        shell,
        text="Xem data hiện có, edit bài viết, tạo folder mới và đồng bộ publiccontent/content.json",
        style="Title.TLabel",
        font=("Segoe UI", 10),
    ).pack(anchor="w", pady=(2, 16))

    layout = ttk.Frame(shell)
    layout.pack(fill="both", expand=True)
    layout.columnconfigure(0, weight=1)
    layout.columnconfigure(1, weight=1)
    layout.rowconfigure(0, weight=1)

    list_panel = ttk.Frame(layout, style="Panel.TFrame", padding=14)
    list_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    list_panel.rowconfigure(1, weight=1)
    list_panel.columnconfigure(0, weight=1)

    ttk.Label(list_panel, text="Data Public Content").grid(row=0, column=0, sticky="w", pady=(0, 8))
    columns = ("folder", "date", "kind", "category", "title")
    tree = ttk.Treeview(list_panel, columns=columns, show="headings", selectmode="browse")
    tree.heading("folder", text="Folder")
    tree.heading("date", text="Date")
    tree.heading("kind", text="Type")
    tree.heading("category", text="Category")
    tree.heading("title", text="Title VI")
    tree.column("folder", width=82, anchor="w")
    tree.column("date", width=88, anchor="w")
    tree.column("kind", width=70, anchor="w")
    tree.column("category", width=86, anchor="w")
    tree.column("title", width=220, anchor="w")
    tree.grid(row=1, column=0, sticky="nsew")

    scrollbar = ttk.Scrollbar(list_panel, orient="vertical", command=tree.yview)
    scrollbar.grid(row=1, column=1, sticky="ns")
    tree.configure(yscrollcommand=scrollbar.set)

    form_panel = ttk.Frame(layout, style="Panel.TFrame", padding=14)
    form_panel.grid(row=0, column=1, sticky="nsew")
    form_panel.columnconfigure(1, weight=1)

    title_var = tk.StringVar()
    title_vi_var = tk.StringVar()
    folder_var = tk.StringVar()
    date_var = tk.StringVar(value=date.today().isoformat())
    category_var = tk.StringVar(value=ALLOWED_CATEGORIES[0])
    image_var = tk.StringVar(value=DEFAULT_IMAGE)
    content_type_var = tk.StringVar(value=CONTENT_TYPES[0])
    link_url_var = tk.StringVar()
    force_var = tk.BooleanVar(value=False)
    mode_var = tk.StringVar(value="create")
    status_var = tk.StringVar(value="Chọn bài bên trái để edit, hoặc tạo bài mới.")

    def manifest_items() -> list[dict]:
        return load_manifest()["items"]

    def refresh_tree(select_folder: str | None = None) -> None:
        tree.delete(*tree.get_children())
        selected_item = None
        for item in manifest_items():
            folder = str(item.get("folder", ""))
            title_vi = str(item.get("titleVi") or item.get("title") or "")
            row_id = tree.insert(
                "",
                "end",
                iid=folder,
                values=(
                    folder,
                    item.get("date", ""),
                    content_type_label(str(item.get("contentType", "article"))),
                    item.get("category", ""),
                    title_vi,
                ),
            )
            if select_folder and folder == select_folder:
                selected_item = row_id

        if selected_item:
            tree.selection_set(selected_item)
            tree.see(selected_item)

    def next_folder() -> str:
        return next_folder_code(manifest_items())

    def set_mode(mode: str) -> None:
        mode_var.set(mode)
        if mode == "edit":
            folder_entry.state(["readonly"])
            force_var.set(True)
            status_var.set("Edit mode: sửa dữ liệu rồi bấm Update Selected.")
        else:
            folder_entry.state(["!readonly"])
            force_var.set(False)
            status_var.set("Create mode: nhập dữ liệu rồi bấm Create New.")

    def clear_form() -> None:
        title_var.set("")
        title_vi_var.set("")
        folder_var.set(next_folder())
        date_var.set(date.today().isoformat())
        category_var.set(ALLOWED_CATEGORIES[0])
        image_var.set(DEFAULT_IMAGE)
        content_type_var.set(CONTENT_TYPES[0])
        link_url_var.set("")
        content_text.delete("1.0", "end")
        content_text.insert(
            "1.0",
            "# Tiêu đề bài viết\n\nViết nội dung ở đây. Có thể dùng **chữ đậm**, *chữ nghiêng* và ảnh:\n\n![Alt text](assets/images/article-interior.svg)\n",
        )
        tree.selection_remove(tree.selection())
        set_mode("create")

    def load_selected() -> None:
        selected = tree.selection()
        if not selected:
            return
        folder = selected[0]
        item = next((row for row in manifest_items() if row.get("folder") == folder), None)
        if not item:
            return
        title_var.set(str(item.get("title", "")))
        title_vi_var.set(str(item.get("titleVi", "")))
        folder_var.set(str(item.get("folder", "")))
        date_var.set(str(item.get("date", "")))
        category_var.set(str(item.get("category", ALLOWED_CATEGORIES[0])))
        image_var.set(str(item.get("image", DEFAULT_IMAGE)))
        content_type_var.set(content_type_label(str(item.get("contentType", "article"))))
        link_url_var.set(str(item.get("linkUrl", "")))
        content_text.delete("1.0", "end")
        content_text.insert("1.0", read_article_body(folder))
        set_mode("edit")

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

    def insert_content_snippet(snippet: str) -> None:
        try:
            content_text.insert("insert", snippet)
        except tk.TclError:
            content_text.insert("end", snippet)
        content_text.focus_set()

    def insert_image_snippet() -> None:
        path = filedialog.askopenfilename(
            title="Choose image for content",
            filetypes=(("Image files", "*.svg *.png *.jpg *.jpeg *.webp"), ("All files", "*.*")),
        )
        if not path:
            insert_content_snippet("![Mô tả ảnh](assets/images/article-interior.svg)")
            return
        try:
            image_path = Path(path).resolve().relative_to(ROOT.parent).as_posix()
        except ValueError:
            image_path = Path(path).as_posix()
        insert_content_snippet(f"![Mô tả ảnh]({image_path})")

    def article_from_form(force: bool) -> ArticleInput:
        return build_article_input(
            title=title_var.get(),
            title_vi=title_vi_var.get(),
            folder=folder_var.get(),
            article_date=date_var.get(),
            category=category_var.get(),
            image=image_var.get(),
            content_type=content_type_var.get(),
            link_url=link_url_var.get(),
            body=content_text.get("1.0", "end").strip(),
            force=force,
        )

    def create_new() -> None:
        try:
            article = article_from_form(force=force_var.get())
            _, folder_path = save_article(article)
        except (ValueError, FileExistsError, OSError, json.JSONDecodeError) as exc:
            messagebox.showerror("Không tạo được bài", str(exc))
            status_var.set(f"Lỗi: {exc}")
            return
        refresh_tree(article.folder)
        clear_form()
        status_var.set(f"Đã tạo {article.folder} và cập nhật content.json.")
        messagebox.showinfo("Đã tạo bài", f"Đã tạo bài tại:\n{folder_path}")

    def update_selected() -> None:
        if mode_var.get() != "edit":
            messagebox.showwarning("Chưa chọn bài", "Chọn một bài trong bảng bên trái trước khi update.")
            return
        try:
            article = article_from_form(force=True)
            _, folder_path = save_article(article)
        except (ValueError, FileExistsError, OSError, json.JSONDecodeError) as exc:
            messagebox.showerror("Không update được bài", str(exc))
            status_var.set(f"Lỗi: {exc}")
            return
        refresh_tree(article.folder)
        load_selected()
        status_var.set(f"Đã update {article.folder} và đồng bộ content.json.")
        messagebox.showinfo("Đã update", f"Đã update bài:\n{folder_path}")

    def delete_selected() -> None:
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn bài", "Chọn một bài trong bảng bên trái trước khi xóa.")
            return

        folder = selected[0]
        item = next((row for row in manifest_items() if row.get("folder") == folder), None)
        title = str(item.get("titleVi") or item.get("title") or folder) if item else folder

        confirmed = messagebox.askyesno(
            "Xóa content?",
            f"Xóa bài này khỏi content.json và xóa folder?\n\n{folder}\n{title}",
        )
        if not confirmed:
            return

        try:
            folder_path = delete_article(folder)
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            messagebox.showerror("Không xóa được bài", str(exc))
            status_var.set(f"Lỗi: {exc}")
            return

        refresh_tree()
        clear_form()
        status_var.set(f"Đã xóa {folder} và đồng bộ content.json.")
        messagebox.showinfo("Đã xóa", f"Đã xóa:\n{folder_path}")

    fields = [
        ("Title EN", title_var),
        ("Title VI", title_vi_var),
        ("Folder", folder_var),
        ("Date", date_var),
    ]
    for row_index, (label, variable) in enumerate(fields):
        ttk.Label(form_panel, text=label).grid(row=row_index, column=0, sticky="w", padx=(0, 12), pady=7)
        entry = ttk.Entry(form_panel, textvariable=variable)
        entry.grid(row=row_index, column=1, sticky="ew", pady=7)
        if label == "Folder":
            folder_entry = entry

    ttk.Label(form_panel, text="Category").grid(row=4, column=0, sticky="w", padx=(0, 12), pady=7)
    ttk.Combobox(form_panel, textvariable=category_var, values=ALLOWED_CATEGORIES, state="readonly").grid(
        row=4, column=1, sticky="ew", pady=7
    )

    ttk.Label(form_panel, text="Type").grid(row=5, column=0, sticky="w", padx=(0, 12), pady=7)
    ttk.Combobox(form_panel, textvariable=content_type_var, values=CONTENT_TYPES, state="readonly").grid(
        row=5, column=1, sticky="ew", pady=7
    )

    ttk.Label(form_panel, text="Link URL").grid(row=6, column=0, sticky="w", padx=(0, 12), pady=7)
    ttk.Entry(form_panel, textvariable=link_url_var).grid(row=6, column=1, sticky="ew", pady=7)

    ttk.Label(form_panel, text="Image").grid(row=7, column=0, sticky="w", padx=(0, 12), pady=7)
    image_row = ttk.Frame(form_panel, style="Panel.TFrame")
    image_row.grid(row=7, column=1, sticky="ew", pady=7)
    image_row.columnconfigure(0, weight=1)
    ttk.Entry(image_row, textvariable=image_var).grid(row=0, column=0, sticky="ew")
    ttk.Button(image_row, text="Browse", command=browse_image).grid(row=0, column=1, padx=(8, 0))

    ttk.Label(form_panel, text="Content").grid(row=8, column=0, sticky="nw", padx=(0, 12), pady=7)
    content_frame = ttk.Frame(form_panel, style="Panel.TFrame")
    content_frame.grid(row=8, column=1, sticky="nsew", pady=7)
    content_frame.columnconfigure(0, weight=1)
    content_frame.rowconfigure(1, weight=1)
    form_panel.rowconfigure(8, weight=1)
    snippet_row = ttk.Frame(content_frame, style="Panel.TFrame")
    snippet_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
    ttk.Button(snippet_row, text="H1 chữ to", command=lambda: insert_content_snippet("# Tiêu đề lớn\n")).grid(row=0, column=0, padx=(0, 6))
    ttk.Button(snippet_row, text="H2 mục", command=lambda: insert_content_snippet("## Mục nội dung\n")).grid(row=0, column=1, padx=(0, 6))
    ttk.Button(snippet_row, text="Đậm", command=lambda: insert_content_snippet("**chữ đậm**")).grid(row=0, column=2, padx=(0, 6))
    ttk.Button(snippet_row, text="Nghiêng", command=lambda: insert_content_snippet("*chữ nghiêng*")).grid(row=0, column=3, padx=(0, 6))
    ttk.Button(snippet_row, text="Bullet", command=lambda: insert_content_snippet("- Ý nội dung\n")).grid(row=0, column=4, padx=(0, 6))
    ttk.Button(snippet_row, text="Chèn ảnh", command=insert_image_snippet).grid(row=0, column=5)
    content_text = tk.Text(
        content_frame,
        height=11,
        wrap="word",
        bg="#2b0603",
        fg="#f6dfb9",
        insertbackground="#f6dfb9",
        relief="flat",
        padx=10,
        pady=8,
        font=("Consolas", 10),
    )
    content_text.grid(row=1, column=0, sticky="nsew")
    content_scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=content_text.yview)
    content_scrollbar.grid(row=1, column=1, sticky="ns")
    content_text.configure(yscrollcommand=content_scrollbar.set)

    ttk.Checkbutton(form_panel, text="Force overwrite khi tạo mới", variable=force_var).grid(
        row=9, column=1, sticky="w", pady=(4, 8)
    )
    ttk.Label(form_panel, textvariable=status_var, style="Hint.TLabel", wraplength=420).grid(
        row=10, column=0, columnspan=2, sticky="ew", pady=(8, 12)
    )

    button_row = ttk.Frame(form_panel, style="Panel.TFrame")
    button_row.grid(row=11, column=0, columnspan=2, sticky="e", pady=(8, 0))
    ttk.Button(button_row, text="New Blank", command=clear_form).grid(row=0, column=0, padx=(0, 8))
    ttk.Button(button_row, text="Refresh Data", command=refresh_tree).grid(row=0, column=1, padx=(0, 8))
    ttk.Button(button_row, text="Delete Selected", command=delete_selected).grid(row=0, column=2, padx=(0, 8))
    ttk.Button(button_row, text="Update Selected", command=update_selected).grid(row=0, column=3, padx=(0, 8))
    ttk.Button(button_row, text="Create New", style="Accent.TButton", command=create_new).grid(row=0, column=4)

    tree.bind("<<TreeviewSelect>>", lambda _event: load_selected())
    refresh_tree()
    clear_form()
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
    parser.add_argument("--content-type", help="Content type: Bài Viết or Link.")
    parser.add_argument("--link-url", help="External URL used when content type is Link.")
    parser.add_argument("--body-file", help="Markdown file to write into content.md.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing article folder and manifest item.")
    parser.add_argument("--dry-run", action="store_true", help="Print the new item without writing files.")
    return parser


if __name__ == "__main__":
    parsed_args = build_parser().parse_args()
    if parsed_args.gui or len(sys.argv) == 1:
        run_gui()
    else:
        run_cli(parsed_args)

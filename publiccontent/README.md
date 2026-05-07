# Public Content

`publiccontent/` là nơi quản lý các nội dung hiển thị trong section **Public Content** ở trang chủ. Trang chủ không hard-code danh sách bài ở HTML; JavaScript sẽ đọc `publiccontent/content.json`, render card, rồi khi người dùng bấm vào card thì mở popup/modal và đọc thêm nội dung từ từng folder.

## Luồng hoạt động

1. Trang chủ gọi `fetch("publiccontent/content.json")`.
2. Mỗi item trong `items` được render thành một card ở section Public Content.
3. Ngôn ngữ hiện tại quyết định tiêu đề và category hiển thị:
   - EN dùng `title`.
   - VI dùng `titleVi` nếu có.
   - `category` được map sang nhãn EN/VI trong `js/main.js`.
4. Khi bấm vào card, trang mở modal:
   - Ảnh lấy từ `image`.
   - Tiêu đề lấy từ `title` hoặc `titleVi`.
   - Ngày lấy từ `date`.
   - Nếu trang đang ở EN, nội dung ưu tiên đọc từ `publiccontent/<folder>/content.en.md`.
   - Nếu trang đang ở VI, nội dung đọc từ `publiccontent/<folder>/content.md`.
   - Nếu thiếu `content.en.md`, frontend tự fallback về `content.md`.
5. Nếu item có `contentType: "link"` và có `linkUrl`, card sẽ có thêm nút `OPEN CONTENT`. Nút này đi thẳng tới link public bên ngoài hoặc project demo.

## Cấu trúc thư mục

```text
publiccontent/
  README.md
  content.json
  create_article.py
  open_article_gui.bat
  conten1/
    index.html
    content.md
    content.en.md
  conten11/
    index.html
    content.md
```

`content.json` là manifest chính. Các folder `conten1`, `conten11`, `conten111...` chứa nội dung chi tiết của từng item.

## Format của `content.json`

```json
{
  "items": [
    {
      "title": "HSK Visualized",
      "titleVi": "Từ Vựng HSK Visualized",
      "folder": "conten1",
      "date": "2026-05-12",
      "category": "Sản Phẩm",
      "image": "assets/images/2.png",
      "contentType": "link",
      "linkUrl": "https://example.com"
    }
  ]
}
```

Các field:

- `title`: tiêu đề tiếng Anh.
- `titleVi`: tiêu đề tiếng Việt.
- `folder`: folder chứa `content.md`, ví dụ `conten1`.
- `date`: ngày đăng dạng `YYYY-MM-DD`.
- `category`: một trong các nhóm `Kỹ Năng`, `Sản Phẩm`, `Tool`, `Sáng Tạo`.
- `image`: ảnh đại diện cho card, tính từ root website, ví dụ `assets/images/2.png`.
- `contentType`: dùng `article` hoặc `link`.
- `linkUrl`: URL public khi `contentType` là `link`; để rỗng nếu là bài viết thường.

## Phân biệt `article` và `link`

`article`:

- Dùng khi muốn người đọc xem nội dung ngay trong popup.
- Card không hiện nút `OPEN CONTENT`.
- Nội dung tiếng Việt nằm trong `publiccontent/<folder>/content.md`.
- Nội dung tiếng Anh nằm trong `publiccontent/<folder>/content.en.md`.

`link`:

- Dùng khi nội dung là demo, tool, sản phẩm, hoặc trang public riêng.
- Card hiện nút `OPEN CONTENT` để đi tới `linkUrl`.
- Vẫn nên có cả `content.md` và `content.en.md` để popup có mô tả ngắn đúng ngôn ngữ trước khi người dùng mở link.

## Nội dung trong `content.md`

Mỗi folder content nên có file:

```text
publiccontent/<folder>/content.md
publiccontent/<folder>/content.en.md
```

Quy ước hiện tại:

- `content.md`: nội dung tiếng Việt.
- `content.en.md`: nội dung tiếng Anh.
- Nếu chưa có bản EN, trang EN sẽ tự dùng tạm `content.md`.

Frontend hỗ trợ markdown cơ bản:

```md
# Tiêu đề lớn

Đoạn văn bình thường, có thể dùng **chữ đậm** và *chữ nghiêng*.

## Mục nội dung

- Ý thứ nhất
- Ý thứ hai

![Mô tả ảnh](assets/images/article-interior.svg)
```

Lưu ý đường dẫn ảnh trong markdown cũng tính từ root website. Ví dụ dùng `assets/images/...` thay vì `../../assets/images/...`.

## Cách thêm hoặc sửa bằng GUI

Chạy từ root project:

```powershell
python publiccontent/create_article.py --gui
```

Hoặc double-click:

```text
publiccontent/open_article_gui.bat
```

Trong GUI:

- Bảng bên trái là dữ liệu đang có trong `content.json`.
- Chọn một item để sửa.
- Form bên phải sửa title, title VI, folder, date, category, type, link URL, image và markdown content.
- Vùng content có 2 tab: `Content VI (content.md)` và `Content EN (content.en.md)`.
- `Create New` tạo folder mới và thêm item vào `content.json`.
- `Update Selected` cập nhật item đang chọn và ghi lại `content.md`.
- `Delete Selected` xóa item khỏi `content.json` và xóa folder tương ứng.
- `New Blank` reset form để nhập item mới.

## Cách tạo nhanh bằng CLI

Ví dụ tạo một bài viết thường:

```powershell
python publiccontent/create_article.py `
  --title "New Creative Note" `
  --title-vi "Ghi chú sáng tạo mới" `
  --category "Sáng Tạo" `
  --date 2026-05-07 `
  --image assets/images/article-ink.svg `
  --content-type "Bài Viết" `
  --body-file publiccontent/conten111/content.md `
  --body-en-file publiccontent/conten111/content.en.md
```

Ví dụ tạo một item dạng link:

```powershell
python publiccontent/create_article.py `
  --title "Public Tool Demo" `
  --title-vi "Demo tool public" `
  --category Tool `
  --date 2026-05-07 `
  --image assets/images/2.png `
  --content-type Link `
  --link-url "https://example.com"
```

Nếu không truyền `--folder`, tool tự tạo folder tiếp theo theo dạng:

```text
conten1
conten11
conten111
conten1111
```

Dùng `--dry-run` để xem dữ liệu sẽ tạo mà không ghi file:

```powershell
python publiccontent/create_article.py --title "Test" --title-vi "Test" --category Tool --dry-run
```

## Quy tắc khi cập nhật thủ công

- Luôn thêm item vào `content.json` nếu muốn nó xuất hiện ngoài trang chủ.
- Luôn tạo folder đúng với field `folder`.
- Folder phải có dạng `conten1+`, ví dụ `conten1`, `conten11`, `conten111`.
- Mỗi folder nên có `content.md`; nếu thiếu, modal sẽ báo chưa có nội dung.
- Mỗi folder nên có `content.en.md`; nếu thiếu, trang EN sẽ fallback về `content.md`.
- Dùng category đúng chính tả để frontend dịch nhãn chính xác.
- Sau khi sửa `content.json`, reload trang để kiểm tra card mới.

## Checklist trước khi publish

- `content.json` là JSON hợp lệ.
- `date` đúng dạng `YYYY-MM-DD`.
- `image` mở được trên website.
- `content.md` hiển thị ổn trong popup.
- `content.en.md` hiển thị đúng khi chuyển sang EN.
- Nếu là `link`, `linkUrl` mở đúng trang public.
- Kiểm tra cả EN và VI vì title/category/date có thay đổi theo ngôn ngữ.

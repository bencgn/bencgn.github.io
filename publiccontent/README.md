# Public Content

Trang chu render cac bai trong `Public Content` tu file `publiccontent/content.json`.

## Cau truc

```text
publiccontent/
  content.json
  conten1/
    index.html
    content.md
  conten11/
    index.html
    content.md
```

## Dinh dang content.json

Moi item gom cac truong:

- `title`: tieu de tieng Anh.
- `titleVi`: tieu de tieng Viet.
- `folder`: ma thu muc bai viet, vi du `conten1`.
- `date`: ngay dang theo dinh dang `YYYY-MM-DD`.
- `category`: chi dung mot trong 4 gia tri `Kỹ Năng`, `Sản Phẩm`, `Tool`, `Sáng Tạo`.
- `image`: duong dan anh dai dien.
- `contentType`: `article` hoac `link`.
- `linkUrl`: URL se mo khi `contentType` la `link`.

Khi them bai moi, tao them thu muc trong `publiccontent/`, sau do them item vao `content.json`.

## Tao bai bang Python tool

Chay tu thu muc goc project:

```powershell
python publiccontent/create_article.py
```

Lenh tren se mo GUI app. Ben trai la data Public Content dang co, ben phai la form tao/sua bai.

- Chon mot bai ben trai de load vao form.
- Sua title, date, category, image va noi dung markdown trong o `Content`.
- Chon `Type`: `Bai Viet` de an nut open, hoac `Link` de hien nut `OPEN CONTENT` trong popup.
- Neu chon `Link`, nhap URL vao `Link URL`.
- Bam `Update Selected` de cap nhat bai dang chon va dong bo `content.json`.
- Bam `Delete Selected` de xoa bai dang chon khoi `content.json` va xoa folder bai viet.
- Bam `New Blank` roi `Create New` de tao bai moi.

O `Content` ho tro markdown co ban:

```md
# Tieu de
Chu **dam**, chu *nghieng*.
![Mo ta anh](assets/images/article-interior.svg)
```

Trong GUI, hang nut tren o `Content` co san cac mau chen nhanh:

- `H1 chu to`: chen title lon.
- `H2 muc`: chen heading muc.
- `Dam`: chen `**chu dam**`.
- `Nghieng`: chen `*chu nghieng*`.
- `Bullet`: chen dong danh sach.
- `Chen anh`: chon anh va chen markdown image.

Tren Windows co the double-click:

```text
publiccontent/open_article_gui.bat
```

Neu muon mo GUI ro rang bang tham so:

```powershell
python publiccontent/create_article.py --gui
```

Neu muon tao nhanh bang mot lenh CLI:

```powershell
python publiccontent/create_article.py `
  --title "New Tool Note" `
  --title-vi "Ghi chu tool moi" `
  --category Tool `
  --date 2026-05-06 `
  --image assets/images/article-ink.svg
```

Neu khong truyen `--folder`, tool tu tao ma tiep theo dang `conten11111`. Tool se tao:

```text
publiccontent/conten11111/index.html
publiccontent/conten11111/content.md
```

va tu cap nhat `publiccontent/content.json`.

Dung `--dry-run` de xem truoc ma khong ghi file:

```powershell
python publiccontent/create_article.py --title "Test" --title-vi "Test" --category Tool --dry-run
```

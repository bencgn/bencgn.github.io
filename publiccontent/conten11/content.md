# Hệ thống sản phẩm chọn lọc chia sẻ công khai

Bài demo thứ hai mô phỏng một bản ghi sản phẩm. Popup có thể hiển thị **nội dung dài**, chữ nhấn mạnh và hình minh họa mà không cần mở trang mới.

![Không gian sân trong](assets/images/article-courtyard.svg)

## Cấu trúc chia sẻ

Một bài public content nên có phần mở đầu ngắn, một ảnh đại diện, rồi các mục nội dung theo từng nhóm. Phần này có thể dùng **bold**, *italic*, và danh sách ngắn.

- **Mục tiêu:** ghi lại thứ có thể tái sử dụng.
- **Trạng thái:** *demo*, đang sẵn sàng để thay bằng nội dung thật.
- **Nguồn dữ liệu:** đồng bộ từ `publiccontent/content.json` và `content.md`.

## Ghi chú

Khi tạo bài bằng GUI Python, phần nội dung trong ô editor sẽ được lưu lại vào đúng file `content.md` của folder bài viết.

# IDC Harness — Hỗ trợ Quản trị hệ thống IDC

Hệ thống trợ lý AI phục vụ vận hành trung tâm dữ liệu (IDC): tra cứu SOP/tài liệu kỹ thuật, hỗ trợ xử lý sự cố, tư vấn dựa trên kho tri thức riêng của trung tâm (brain IDC), với kênh xuất chính là bot Telegram chỉ-đọc và bảng điều khiển web là nơi quản trị/duy nhất được ghi dữ liệu.

## Cấu trúc chính

- `server/` — máy chủ FastAPI: chat đa mô hình (API + CLI: Claude Code, Codex, Grok, Antigravity), MCP Hub với phân quyền theo kênh, kho tri thức (Second Brain) dạng vault Obsidian, workflow/Kanban, việc nền, ghi chú, tạo ảnh, giọng nói.
- `dashboard/` — giao diện web quản trị.
- `brains/` — dữ liệu tri thức (không nằm trong repo code; đồng bộ riêng). Brain **IDC** chứa cây tri thức hạ tầng trung tâm dữ liệu: sources 00–15, wiki 01–17 (điện, UPS, làm mát, PCCC, mạng, an ninh, vận hành...).
- `system/` — định nghĩa agent, skill và plugin hệ thống.

## Chạy trên Windows

1. Chạy `setup.bat` (cài đặt lần đầu).
2. Tạo file `.env` ở thư mục gốc nếu cần đổi cổng, ví dụ: `JAVIS_PORT=6868`.
3. Chạy `start-idc.bat` (chạy nền) hoặc `IDC-Harness.bat` (mở như ứng dụng), rồi mở http://localhost:6868.
4. Dừng hệ thống: `stop-idc.bat`.

## Nguồn gốc

Hệ thống được phát triển trên nền một khung mã nguồn mở theo giấy phép MIT; thông tin ghi công và giấy phép xem tại `NOTICE.md` và `LICENSE`.

## Giấy phép

MIT — xem `LICENSE`.

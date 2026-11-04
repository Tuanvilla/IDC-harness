# IDC Harness — ghi chú cho trợ lý lập trình

Repo này là hệ thống IDC Harness — trợ lý vận hành trung tâm dữ liệu IDC (dashboard quản trị + bot Telegram chỉ đọc, kho tri thức vault theo miền hạ tầng 00–17).

Nguyên tắc khi sửa:

- Kênh Telegram bị ghim quyền chỉ-đọc (suggest) ở `_muc_quyen_luot_chat` trong `server/main.py` — không nới lại.
- Các module chatbot/kênh xã hội đã bị cắt ở tầng route/khởi động; thư viện sót lại trên đĩa là nợ kỹ thuật "đợt 2b", đừng nối lại.
- Định danh nội bộ giữ nguyên tên gốc (module `javis_core`, plugin `javis-*`, biến môi trường `JAVIS_*`, file log `server/javis.log`) — đây là plumbing, đổi tên sẽ vỡ hệ thống.
- `brains/` là dữ liệu, gitignore theo thiết kế; không commit dữ liệu brain vào repo code.

# Nhật ký thay đổi — IDC Harness

## 1.0.0 — 2026-11-04

- Khởi tạo IDC Harness cho vận hành trung tâm dữ liệu IDC (ghi công mã nguồn mở: xem `NOTICE.md`).
- Cắt bỏ: chatbot khách hàng và hộp thư hội thoại, các kênh Messenger/Threads/WhatsApp/Slack/Discord/Lark/Zalo OA & Zalo cá nhân, tích hợp marketing/quảng cáo, cây tài liệu của dự án gốc.
- Ghim kênh Telegram ở quyền chỉ-đọc (suggest) qua cơ chế phân quyền của MCP Hub — bot chỉ trả lời/tư vấn, không ghi dữ liệu; dashboard là mặt phẳng ghi duy nhất.
- Nạp brain IDC: tri thức hạ tầng trung tâm dữ liệu (sources 00–15, wiki 01–17, gồm sơ đồ một sợi điện và danh mục UPS).
- Đổi nhận diện: tiêu đề dashboard, tên các script khởi động (`start-idc`, `stop-idc`, `IDC-Harness.bat`), kênh cập nhật trỏ về repo này.

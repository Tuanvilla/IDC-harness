# Nhật ký thay đổi — IDC Harness

## 1.0.1 — 2026-11-11

### Bot Telegram nhanh và chuẩn hơn
- Trả lời nhanh hơn hẳn: câu tra cứu thường về trong khoảng 10 giây (trước đây khoảng 26 giây).
- Câu trả lời trình bày theo từng mục, dễ đọc; thiết bị UPS luôn được gọi đúng là "UPS".
- Bot tự giới thiệu là em Thảo, trợ lý IDC.

### Làm việc trong nhóm trực
- Bot chỉ trả lời khi được gọi (@nhắc tên, trả lời vào tin nhắn của bot, hoặc gọi tên trợ lý) — không chen vào trò chuyện thường.
- Nhiều người hỏi cùng lúc: bot trả lời lần lượt theo thứ tự, không bỏ sót câu nào, và gọi đúng tên từng người hỏi.
- Các lệnh trong nhóm (ví dụ /stop@IDC_Help_Bot) hoạt động đúng như trong chat riêng.

### Cài đặt và vận hành
- Bộ cài Windows cho phép chọn thư mục cài đặt.
- Tên gói ChatGPT/Grok/Claude trên dashboard hiển thị đúng tên gói bạn đang dùng.
- Đăng nhập dashboard bền hơn, ít phải đăng nhập lại.

### Bạn cần làm sau khi cập nhật
- Chỉ cần bấm nút Cập nhật trên dashboard và chờ hệ thống tự khởi động lại — dữ liệu và cài đặt của bạn được giữ nguyên.
- Nếu bot trong nhóm từng gọi sai tên người hỏi, gõ /reset một lần trong nhóm để xoá lịch sử phiên cũ.

## 1.0.0 — 2026-11-04

- Khởi tạo IDC Harness cho vận hành trung tâm dữ liệu IDC (ghi công mã nguồn mở: xem `NOTICE.md`).
- Cắt bỏ: chatbot khách hàng và hộp thư hội thoại, các kênh Messenger/Threads/WhatsApp/Slack/Discord/Lark/Zalo OA & Zalo cá nhân, tích hợp marketing/quảng cáo, cây tài liệu của dự án gốc.
- Ghim kênh Telegram ở quyền chỉ-đọc (suggest) qua cơ chế phân quyền của MCP Hub — bot chỉ trả lời/tư vấn, không ghi dữ liệu; dashboard là mặt phẳng ghi duy nhất.
- Nạp brain IDC: tri thức hạ tầng trung tâm dữ liệu (sources 00–15, wiki 01–17, gồm sơ đồ một sợi điện và danh mục UPS).
- Đổi nhận diện: tiêu đề dashboard, tên các script khởi động (`start-idc`, `stop-idc`, `IDC-Harness.bat`), kênh cập nhật trỏ về repo này.

# Nhật ký thay đổi — IDC Harness

## 1.1.0 — 2026-11-11

### Cập nhật thông minh và chắc chắn hơn
- Claude Agent SDK (gói IDC Harness dùng để điều khiển Claude Code) giờ TỰ cập nhật mỗi ngày trong cùng dòng phiên bản: chỉ lấy bản đã phát hành ít nhất ba ngày, cài xong chạy thử kiểm chứng, lỗi thì tự quay về bản cũ. Bản này cũng nâng SDK qua mốc đã vá lỗ hổng bảo mật CVE-2026-96620.
- Sau khi cập nhật và khởi động lại, dashboard mở lại đúng brain anh đang chọn, không còn nguy cơ rớt về brain mặc định như trước.
- Bấm Cập nhật lúc đang có một lượt cập nhật khác: thông báo giờ nói rõ đang ở bước nào, còn khoảng bao lâu thì bấm lại được, kèm nhật ký cập nhật mới nhất để biết nó đang chạy thật hay đã treo.

### Bạn cần làm sau khi cập nhật
- Không cần làm gì thêm. Riêng máy nào vẫn đang ở bản cũ mà nút Cập nhật từng bị treo: cập nhật thủ công một lần bằng git pull như hướng dẫn ở bản 1.0.2, từ bản sau dùng nút bình thường.

## 1.0.3 — 2026-11-11

### Bot trong nhóm trực: /stop đúng người và chống treo lượt
- Lệnh /stop giờ chỉ dừng đúng yêu cầu của người gõ lệnh: không còn làm hỏng câu hỏi của người khác đang chạy hay đang chờ.
- Chủ bot vẫn dùng /stop để dừng toàn bộ như trước.
- Nếu một câu hỏi chạy quá 3 phút mà chưa xong, bot tự dừng lượt đó, báo cho người hỏi biết, rồi trả lời người tiếp theo — cả nhóm không còn bị một câu hỏi treo làm đứng theo.

### Bạn cần làm sau khi cập nhật
- Không cần làm gì thêm. Trong nhóm, ai muốn rút lại yêu cầu của mình chỉ cần gõ /stop.

## 1.0.2 — 2026-11-11

### Sửa lỗi cập nhật
- Sửa lỗi nút "Cập nhật ngay" bị treo ở bước dừng server trên Windows: quá trình cập nhật nay tự dừng và khởi động lại gọn gàng, không còn đứng im không báo lỗi.
- Mọi bước cập nhật đều có giới hạn thời gian chờ — nếu mạng hoặc một bước nào đó bị kẹt, hệ thống báo lỗi rõ ràng thay vì treo vô hạn.

### Bạn cần làm sau khi cập nhật
- Nếu nút Cập nhật trên máy bạn vẫn chạy tốt, cứ bấm cập nhật như thường.
- Nếu nút Cập nhật từng bị treo (màn hình cập nhật đứng im nhiều phút), lần này hãy cập nhật thủ công một lần: tắt IDC Harness, mở thư mục cài đặt, mở cửa sổ lệnh tại đó và chạy `git pull`, rồi mở lại chương trình. Từ các bản sau, nút Cập nhật sẽ hoạt động bình thường.

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

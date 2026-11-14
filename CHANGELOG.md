# Nhật ký thay đổi — IDC Harness

## 1.4.2 — 2026-11-14

### Giấc mơ: tự thử lại khi model nền trả lời chậm

- Giấc mơ đêm qua đã đọc được 5 phiên nhưng chết ở bước phân tích vì model nền (Gemini qua API miễn phí) trả lời quá chậm, quá 120 giây mà chưa gửi chữ nào về nên đường truyền tự ngắt. Từ bản này, giấc mơ sẽ tự thử lại một lần sau 20 giây khi gọi model gặp sự cố (kể cả bước phân tích lẫn bước kiểm chứng), thay vì bỏ cả lần chạy ngay từ lỗi đầu tiên.
- Bản tóm tắt phiên đưa cho model cũng gọn lại một chút (từ 24.000 xuống 16.000 ký tự) để model nền trả lời nhanh hơn.

### Bạn cần làm sau khi cập nhật

- Mở trang Tự học, bấm "Chạy giấc mơ ngay" một lần nữa. Nếu lần chạy vẫn lỗi thì gửi lại cho em câu lỗi mới hiện trên panel - nếu nó vẫn là lỗi hết giờ thì mình sẽ đổi model nền sang một model trả lời nhanh hơn (ví dụ gemini-2.5-flash hoặc Groq).

## 1.4.1 — 2026-11-14

### Sửa lỗi giấc mơ: lần chạy hỏng giờ nói rõ lý do

- Giấc mơ đêm qua đôi khi đọc phiên xong mà không ra đề xuất nào, lại không nói rõ vì sao. Từ bản này, khi một lần chạy giấc mơ gặp lỗi, hệ ghi lại đúng câu lỗi của model (ví dụ model báo không tồn tại hay hết lượt) thay vì chỉ ghi tên lỗi chung chung, và ghi luôn số phiên nó đã thấy - anh mở lịch sử chạy là biết ngay nó dừng ở bước nào.
- Sửa lỗi giấc mơ có thể bỏ sót phiên chat: trước đây nó lọc phiên theo đúng một cách viết tên brain, trong khi chat trên dashboard và chat Telegram lưu tên brain theo hai kiểu khác nhau. Giờ nó nhận cả hai kiểu nên không còn phiên nào bị bỏ qua.
- Mục giấc mơ trên trang Tự học giờ hiện luôn trạng thái lần chạy gần nhất (lúc nào, xong hay lỗi, thấy bao nhiêu phiên, ra bao nhiêu đề xuất) để anh khỏi phải đoán.
- Nếu vòng kiểm chứng bằng model gặp sự cố, các đề xuất đã qua kiểm chứng bằng trích dẫn gốc vẫn được giữ lại (đánh dấu "chưa kiểm chứng") thay vì bị bỏ hết trong im lặng.

### Bạn cần làm sau khi cập nhật

- Mở trang Tự học, bấm "Chạy giấc mơ ngay" một lần nữa. Nếu vẫn lỗi, mục giấc mơ giờ sẽ hiện đúng câu lỗi để anh gửi lại cho em chẩn đoán tiếp.

## 1.4.0 — 2026-11-14

### Giấc mơ đêm qua: hệ tự rút bài học từ nhật ký phiên
- Mỗi đêm lúc 02:00, hệ đọc lại nhật ký trò chuyện trong ngày rồi rút ra các đề xuất ghi nhớ (sự kiện đã kiểm chứng, bài học từ sự cố, thông tin cũ cần sửa) - theo đúng mô hình "dreaming" mà Anthropic công bố cho agent của họ.
- Đề xuất chỉ nằm trong kho chờ duyệt riêng; KHÔNG có đường nào tự ghi thẳng vào kho tri thức. Anh xem từng đề xuất trên trang Tự học (kèm trích dẫn gốc làm bằng chứng) rồi bấm Áp dụng thì nội dung mới vào wiki/memory - đúng một lần, có kiểm tra file đích còn nguyên như lúc đề xuất được viết hay không.
- Chế độ của giấc mơ chỉ có "Đề xuất" và "Chạy thử", không có "Tự động": kể cả ai đó vô tình đặt cấu hình thành tự động, hệ cũng tự hạ xuống Đề xuất.
- Đề xuất không bao giờ nhắm vào thư mục nguồn (sources/) - tài liệu gốc là dữ kiện chuẩn, giấc mơ không được viết lại.

### Bạn cần làm sau khi cập nhật
- Mở trang Tự học, xem mục "Giấc mơ đêm qua" và bấm "Chạy giấc mơ ngay" một lần để thử ngay trong ngày (không cần chờ tới 02:00 đêm).
- Kiểm tra luôn chế độ "Tự học" trên cùng trang: nếu đang ở "Tự động" thì hai hệ tự học cũ vẫn tự ghi vào brain mà không qua duyệt (đó là mặc định cũ của chúng). Nếu anh muốn mọi ghi nhớ đều phải qua tay mình thì chuyển sang "Đề xuất".

## 1.3.0 — 2026-11-11

### Cập nhật nhanh hơn hẳn
- Lúc bấm Cập nhật, hệ giờ TẢI VÀ GỘP MÃ MỚI TRƯỚC trong lúc bản đang chạy vẫn phục vụ bình thường; chỉ tới khi mọi thứ sẵn sàng mới dừng để đổi sang bản mới. Thời gian hệ thống ngừng phục vụ co lại còn đúng đoạn đổi ca và khởi động lại.
- Nếu bản mới không thay đổi danh sách thư viện, bước cài thư viện được BỎ QUA hoàn toàn thay vì chạy lại từ đầu như trước - đây vốn là bước ngốn thời gian nhất của mỗi lần cập nhật.
- Ngay khi vòng dò bản mới phát hiện có bản mới (cơ chế ở 1.2.0), hệ âm thầm tải trước mã và thư viện cần thiết về máy. Tới lúc anh bấm Cập nhật, phần tải coi như đã xong.
- Bước kiểm tra sức khoẻ sau khi bật bản mới cũng nhạy hơn: server lên là biết gần như ngay, không phải chờ thêm vài giây.

### Bạn cần làm sau khi cập nhật
- Không cần làm gì. Các lần cập nhật từ nay sẽ tự ngắn lại theo cách mới; riêng lần lên 1.3.0 này vẫn đi theo quy trình cũ một lần cuối.

## 1.2.1 — 2026-11-11

### Bảo mật
- Bot Telegram chuyển sang chặn kiểu "chưa cho phép là không vào": trước đây nếu danh sách chat được phép (whitelist) bị để trống, bot sẽ trả lời MỌI người nhắn tới. Từ bản này, whitelist trống nghĩa là bot không trả lời ai cả. Danh sách đã điền sẵn thì dùng như cũ, không đổi gì.
- Kho gói không còn tự nối vào kho của bên thứ ba ở bản cài mới. Gói là mã chạy trên máy nên từ nay quản trị muốn dùng kho nào thì tự điền địa chỉ kho đó; chưa điền thì mục kho để trống, cài gói từ tệp vẫn hoạt động bình thường.
- Sửa đường dẫn báo lỗi bảo mật và nhãn thông tin bản Docker về đúng kho IDC Harness (trước đây còn trỏ sang kho của dự án gốc, dễ gửi nhầm).
- Bổ sung kiểm thử tự động ghim chặt cam kết "Telegram chỉ đọc": mọi phiên Telegram đều bị giới hạn ở mức chỉ đọc và đề xuất, kiểm tra tự chạy mỗi lần sửa mã để không ai vô tình nới quyền về sau.

### Bạn cần làm sau khi cập nhật
- Kiểm tra nhanh trong Cài đặt: danh sách chat Telegram được phép phải có ít nhất ID của anh (và ID nhóm trực nếu dùng nhóm). Nếu để trống, bot sẽ im lặng với tất cả mọi người cho tới khi điền.
- Nếu anh đang dùng Kho gói: điền địa chỉ kho của anh trong Cài đặt, mục Gói. Chưa dùng thì bỏ qua.

## 1.2.0 — 2026-11-11

### Báo bản mới chủ động
- IDC Harness giờ TỰ kiểm tra bản mới mỗi 30 phút. Khi có bản mới, anh nhận được một tin trong hòm thư trên dashboard và một tin nhắn Telegram từ bot, kèm vài điểm chính của bản đó. Mỗi phiên bản chỉ báo đúng một lần, không nhắc lại làm phiền.
- Chuông thông báo trên dashboard tự làm mới khi tab đang mở: có tin mới là huy hiệu chuông lên số ngay, không cần tải lại trang.

### Bạn cần làm sau khi cập nhật
- Không cần làm gì thêm. Muốn tắt loại tin này, chỉnh trong chính sách thông báo của hệ như các tin hệ thống khác.

## 1.1.1 — 2026-11-11

### Sửa lỗi huỷ lịch trong chat và dọn tên gọi hiển thị
- Sửa lỗi ra lệnh huỷ lịch/nhắc hẹn trong chat có lúc báo lỗi khó hiểu và không huỷ được gì: nếu bộ công cụ của phiên bị thiếu công cụ lịch (hay gặp ngay sau khi khởi động lại), hệ thống tự dò lại một lần bằng danh sách mới trước khi bỏ cuộc. Khi vẫn chưa huỷ được, thông báo nói rõ là chưa có gì bị huỷ và chỉ cách xử lý tiếp, không còn hiện tên kỹ thuật.
- Dọn nốt chữ "Javis" còn sót trong các đoạn chữ hiển thị cho người dùng (mô tả plugin, thông báo, từ điển giao diện) thành "IDC Harness". Tên kỹ thuật bên trong (tên công cụ, thư mục dữ liệu, biến môi trường) giữ nguyên để hệ thống chạy ổn định, không ảnh hưởng dữ liệu hiện có.

### Bạn cần làm sau khi cập nhật
- Không cần làm gì thêm.

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

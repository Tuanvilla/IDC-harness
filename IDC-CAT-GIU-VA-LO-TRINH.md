# IDC HARNESS — BẢN ĐỒ CẮT / GIỮ VÀ LỘ TRÌNH

- **Ngày bắt đầu:** 04/11/2026
- **Chỉ đạo của chủ dự án:** Xây dựng **hẳn lại mới từ đầu, bỏ hoàn toàn repo cũ**
  (`ho-tro-quan-tri-idc`). Bê **nguyên cấu trúc Javis OS** của minhquy
  (https://github.com/blogminhquy/javis-os, MIT), chỉ cắt bỏ phần marketing,
  mạng xã hội và những thứ không liên quan tới công việc **hỗ trợ, quản lý
  hệ thống hạ tầng IDC**.
- **Nền:** Javis OS **0.461.0** (commit upstream `a3d6ac0`), xuất sạch
  (git archive) vào repo mới này ngày 04/11/2026. LICENSE và ghi công
  tác giả gốc giữ nguyên theo giấy phép MIT.
- **Mục tiêu hệ thống:** harness đấu nối linh hoạt các model AI vào Vault
  Obsidian (`sources/` → `wiki/`) chứa **dữ liệu hạ tầng của trung tâm IDC**;
  đầu ra chính là **Telegram bot** trả lời, tư vấn, hỗ trợ, giải đáp dựa trên
  kiến thức của hệ thống.

## ĐÃ CẮT — Đợt 1 (04/11/2026, các thành phần tách rời, cắt xong hệ vẫn chạy)

| Thành phần | Loại |
|---|---|
| Plugin `fb-monitor-apify`, `meta-ads-graph`, `meta-pages-graph` | Marketing/quảng cáo Facebook |
| Plugin `image-chatgpt` | Sinh ảnh (ngoài mục tiêu) |
| Skill `html-to-webcake` | Landing page/marketing |
| Connector catalog: `google-ads`, `google-analytics`, `google-search-console`, `botcake`, `substack`, `composio` (cả bản VI + EN) | Marketing/bán hàng |
| Tài liệu chatbot bán hàng, hội thoại khách, Messenger, Slack/WhatsApp, Discord/Lark (docs VI + EN) | Kênh với khách/người ngoài |

Catalog connector còn giữ: zalo (để dành, chưa dùng), google-sheets,
google-workspace, google-tasks, google-calendar, gmail, google-keep,
notebooklm — các mẫu này nằm yên cho tới khi được kết nối thật.

## ĐÃ NẠP — Brain IDC

`brains/IDC/` chứa dữ liệu hạ tầng IDC (chuyển từ vault của hệ thống cũ —
đây là DỮ LIỆU của trung tâm, không phải code): `sources/` cây 00–15,
`wiki/` cây 01–17 kèm trang sơ đồ một sợi và danh mục UPS đã chưng cất,
`memory/MEMORY.md`, 3 kỹ năng riêng của IDC (tra-cuu-sop,
verification-before-completion, meeting-action-items). Khi server khởi
động lần đầu, system sync của Javis tự cài thêm 5 kỹ năng hệ thống
(query-wiki, ingest-source, lint-wiki, notes, javis-builder) vào brain.
Theo thiết kế của Javis, `brains/` không commit vào repo code — brain sao
lưu qua cơ chế đồng bộ GitHub riêng của Javis (kho vault riêng, vd
IDCBackup).

## GIỮ LẠI theo quyết định của chủ dự án (04/11/2026, 20:13)

**Sinh ảnh** (gồm plugin `image-chatgpt` đã khôi phục sau đợt 1),
**voice call/live**, **ghi chú (notes)**, **STT/nghe giọng nói** — KHÔNG
cắt. Các mục này đã được rút khỏi danh sách cắt đợt 2.

## ĐÃ CẮT — Đợt 2 (04/11/2026 tối, phẫu thuật trong `main.py`)

1. **Toàn bộ route kênh khách/người ngoài trong `main.py`** (xoá ~2.500
   dòng theo khối banner): khối kênh điều khiển Slack/WhatsApp của chủ +
   webhook WhatsApp; Messenger (webhook, setup wizard, OAuth Facebook,
   Instagram, comments); Threads (webhook, OAuth, comments); Zalo OA
   (webhook); toàn bộ khối **Bot chuyên trách** (`/chatbots` CRUD, tài
   khoản kênh) + đăng ký route Hộp thư hội thoại; 5 route reply-policy
   còn sót ở cuối file; route QR đăng nhập Zalo cá nhân
   (`/connect/zalo/*`); route phụ Substack (`/connect/substack/resolve-uid`).
2. **Module đã xoá hẳn:** `channels/` chỉ còn `__init__.py` với sổ đăng ký
   rỗng (Messenger, Threads, WhatsApp, Slack, Lark, Zalo OA, Zalo cá nhân,
   Zalo Bot-khách, Telegram-khách, API channel); `routes/channels.py`,
   `routes/conversations.py`; `messenger_*`, `threads_*`, `whatsapp_bot`,
   `slack_bot`, `discord_bot`, `lark_bot`, `zalo_oa_bot`,
   `zalo_personal_channel`, `zalo_login`, `zalo_friend_intake`,
   `zalo_phone_lookup`, `conversation_actions`, `botcake_mcp`,
   `substack_mcp` (kèm dọn `_INTERNAL` trong `mcp_client.py`).
3. **Vô hiệu hoá ở điểm khởi động:** `owner_channels.ALL = ()` (Slack/
   WhatsApp/Discord/Lark không còn là kênh điều khiển); gỡ khối khởi
   động bộ giám sát chatbot + vòng đọc Zalo cá nhân khỏi startup, gỡ
   tick tự soát reply-policy khỏi scheduler, gỡ stop Zalo cá nhân khỏi
   shutdown.
4. **Dashboard:** trang Hội thoại (và Chatbot, vốn đã ẩn) bị ẩn khỏi
   thanh điều hướng bằng chính cơ chế `RAIL_AN` của Javis.
5. **Kết quả đo được:** route 612 → **541** (không còn route nào thuộc
   chatbot/conversations/messenger/threads/whatsapp/zalo-oa/channels);
   `route_table.json` đã chụp lại và test bảng route đạt; server boot
   thật: `/health` + `/` 200, `/chatbots` 404 đúng ý.

**Còn lại đợt 2b (chưa gỡ hẳn):** các module thư viện của chatbot
(`chatbot_*.py`, `conversations.py`, `channel_accounts.py`,
`customer_conversations.py`...) vẫn nằm trong `server/` nhưng **không
còn đường vào**: không route, không khởi động poller, sổ kênh rỗng,
trang UI ẩn. Chúng còn được `main.py` tham chiếu ở vài đường phụ của
vỏ trả lời (nhánh `bot` không bao giờ được gọi khi không tạo được bot).
Gỡ hẳn khỏi `main.py` là một ca phẫu thuật riêng, làm khi hệ đã chạy
ổn định trên máy chủ dự án. Nhóm thử nghiệm `improvement_*`,
`resonance_*`, Adaptive Context Runtime: giữ nguyên, quyết sau cùng.
`youtube_read`, branding/tên miền, share links, nhóm Code/terminal:
chưa đụng tới ở đợt này.

## ĐÃ GHIM — Telegram chỉ đọc (04/11/2026 tối)

Kênh Telegram của Javis nguyên bản là kênh *chủ nhân toàn quyền*. Đã
ghim cứng ở tầng cơ chế theo mô hình quản trị đã chốt (Telegram chỉ trả
lời/tư vấn/giải đáp; dashboard là mặt ghi/cấu hình duy nhất):

- `_muc_quyen_luot_chat`: phiên nào mang channel `telegram` thì trần
  quyền là `suggest` — MCP Hub ép readonly cho mọi connector ở mode này.
- Đường engine API (`_tg_answer_engine`): truyền channel thật vào hàm
  tính mức quyền (trước đây truyền `None`).
- Engine CLI trong cùng vỏ: Claude qua `_apply_mcp(mode)`, Grok/
  Antigravity qua `cli.mode` + hub, **Codex qua sandbox hệ điều hành
  `read-only`** — đều nhận `_muc_tg = suggest` khi lượt là Telegram của
  chủ. Kiểm chứng trực tiếp: telegram → `suggest`, web → `full`,
  zalo → `full`.

## TRẠNG THÁI KIỂM CHỨNG (04/11/2026)

- Toàn bộ `server/` + `system/plugins/` biên dịch sạch (compileall).
- `import main` thành công: 612 route đăng ký.
- Khởi động thật trên cổng 7781: `/health` và `/` trả 200; server nhận
  brain IDC và tự cài kỹ năng hệ thống vào brain.
- Chưa cấu hình model/bot trong bản mới này (settings sạch như Javis gốc):
  cấu hình ở đợt 2 cùng lúc với việc ghim quyền Telegram.
- **Cập nhật sau đợt 2 (04/11 tối):** import sạch, route 541, boot thật
  cổng 7781 đạt (`/health`, `/` 200; `/chatbots` 404), ghim Telegram chỉ
  đọc đã kiểm chứng bằng hàm tính mức quyền. Bước tiếp theo: tạo repo
  GitHub mới cho hệ này — **dừng và chờ chủ dự án** theo yêu cầu của anh.

## QUYẾT ĐỊNH ĐÃ THAY THẾ

Chỉ đạo này thay thế quyết định ngày 03/11/2026 ("viết mới dạng modular,
dùng lại chọn lọc vài module nhỏ") và toàn bộ hướng xây trên repo
`ho-tro-quan-tri-idc` (bao gồm cả đợt R1 vừa làm trên repo đó). Repo cũ
được giữ nguyên trạng trên GitHub cho tới khi hệ thống mới này chạy được
đầu-cuối và anh xác nhận bỏ hẳn.

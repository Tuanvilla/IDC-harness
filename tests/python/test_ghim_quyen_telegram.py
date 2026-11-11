"""Ghim cam kết cốt lõi của IDC Harness: kênh Telegram CHỈ ĐỌC, và cổng whitelist
chặn theo kiểu fail-closed.

    python tests/python/test_ghim_quyen_telegram.py

Không cần API key, không chạm mạng: chỉ gọi hàm quyết quyền của server, cổng
whitelist của bot và bộ chuẩn hoá chat_id.

Vì sao có tệp này (2026-11-11, bản 1.2.1): một bản rà soát độc lập chỉ ra rằng
(a) mức quyền Telegram được quyết ở HAI nơi viết khác nhau - hàm ghim theo phiên
`_muc_quyen_luot_chat` (xét startswith "telegram") và biến cục bộ trong
`_tg_answer_engine` - mà không có test hồi quy nào khẳng định lượt Telegram
phải ra `suggest`; (b) whitelist rỗng từng nghĩa là cho phép MỌI người. Tệp này
ghim cả hai cam kết: Telegram luôn `suggest`, whitelist rỗng thì không ai vào.
"""
from _paths import ROOT, SERVER  # noqa: E402,F401  - nạp server/ vào sys.path
import os
import tempfile
from pathlib import Path

state = tempfile.mkdtemp(prefix="idc-ghim-quyen-")
os.environ["JAVIS_STATE_DIR"] = state
os.environ["BRAINS_DIR"] = str(Path(state) / "brains")
os.environ["JAVIS_SESSIONS_DB"] = str(Path(state) / "sessions.db")

import main  # noqa: E402
from telegram_bot import TelegramBot, parse_chat_ids  # noqa: E402

_fails = []


def check(name, cond, them=""):
    print(("ok   " if cond else "FAIL ") + name + ((f"  [{them!r}]") if them and not cond else ""))
    if not cond:
        _fails.append(name)


# ---- 1. Mức quyền theo phiên: Telegram luôn là suggest (chỉ đọc) ----
check("phiên telegram, câu hỏi thường -> suggest",
      main._muc_quyen_luot_chat({"channel": "telegram"}, "UPS pha 1 là gì?") == "suggest")
check("phiên telegram, tin /plan -> vẫn suggest",
      main._muc_quyen_luot_chat({"channel": "telegram"}, "/plan dọn kho") == "suggest")
check("channel telegram kèm hậu tố (nhóm) -> suggest (startswith)",
      main._muc_quyen_luot_chat({"channel": "telegram:nhom"}, "chào") == "suggest")
check("phiên web thường -> full (dashboard là mặt ghi duy nhất)",
      main._muc_quyen_luot_chat({"channel": "web"}, "chào") == "full")
check("không có channel -> full như hành vi cũ",
      main._muc_quyen_luot_chat({}, "chào") == "full")
check("phiên zalo của chủ -> full (chủ chốt giữ nguyên, không lẫn với Telegram)",
      main._muc_quyen_luot_chat({"channel": "zalo"}, "chào") == "full")


# ---- 2. Cổng whitelist: fail-closed ----
async def _tra_loi_gia(text, meta, progress):
    return ""


bot_rong = TelegramBot("token-gia", "", _tra_loi_gia)
check("whitelist rỗng: chat riêng của bất kỳ ai cũng bị chặn",
      bot_rong._duoc_dung("817052927") is False)
check("whitelist rỗng: nhóm cũng bị chặn",
      bot_rong._duoc_dung("-1004477318775") is False)

bot_co = TelegramBot("token-gia", "817052927, -1004477318775", _tra_loi_gia)
check("có whitelist: chủ được dùng",
      bot_co._duoc_dung("817052927") is True)
check("có whitelist: nhóm trực được dùng",
      bot_co._duoc_dung("-1004477318775") is True)
check("có whitelist: người lạ bị chặn",
      bot_co._duoc_dung("123456789") is False)


# ---- 3. Chuẩn hoá whitelist: giữ nguyên hành vi parse ----
check("parse: chuỗi rỗng -> danh sách rỗng",
      parse_chat_ids("") == [])
check("parse: nhiều id cách nhau bởi phẩy/chấm phẩy/khoảng trắng",
      parse_chat_ids("1, 2;3  4") == ["1", "2", "3", "4"])
check("parse: giữ dấu trừ của id nhóm",
      parse_chat_ids("-1004477318775") == ["-1004477318775"])


# ---- 4. Không em dash trong các file vừa chạm (luật toàn dự án) ----
for f in (SERVER / "telegram_bot.py", SERVER / "bot_gateway.py", Path(__file__)):
    check(f"không em dash: {f.name}", chr(0x2014) not in f.read_text(encoding="utf-8"))

if _fails:
    print(f"\nFAIL - test_ghim_quyen_telegram: {len(_fails)} lỗi")
    raise SystemExit(1)
print("\nOK - test_ghim_quyen_telegram: tất cả pass")

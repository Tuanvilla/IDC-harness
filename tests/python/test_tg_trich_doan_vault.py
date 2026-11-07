"""Lượt Telegram nạp sẵn trích đoạn vault + trần độ dài mềm (chủ chốt 2026-11-07).

    python tests/run.py tg_trich_doan_vault      (KHÔNG mạng)

Bối cảnh: chủ phàn nàn bot Telegram trả lời chậm mà vẫn phải giữ đủ cấu trúc
thông tin. Đọc đường đi một lượt thì thủ phạm là engine one-shot phải tự chạy
công cụ đọc file cho gần như mọi câu tra cứu - mỗi vòng công cụ tốn vài giây.
Bản sửa có hai nửa, file này canh cả hai:

1. `_tg_trich_doan_vault()` chấm điểm file wiki/ + sources/ theo từ khoá câu
   hỏi và trích sẵn tối đa 3 file khớp nhất vào prompt, để model trả lời trong
   MỘT vòng. Canh: câu tra cứu thật thì có trích đoạn kèm đúng file; câu xã
   giao thì KHÔNG nạp gì (nhồi tài liệu bừa vừa tốn prompt vừa loãng); tổng
   trích đoạn không vượt trần ký tự; file dài bị cắt quanh vùng khớp.
2. Dấu đặt tại nguồn trong `_tg_answer_engine`: khối trình bày Telegram có
   dòng ĐỘ DÀI (gói ~1.500 ký tự, giữ đủ mục/số liệu) và có lời gọi nạp trích
   đoạn. Sửa hụt dấu này là tính năng chết lặng lẽ như từng xảy ra với hệ
   tiết kiệm trước 0.23.1.
"""
from _paths import ROOT, SERVER  # noqa: E402,F401  - nạp server/ vào sys.path
import tempfile
from pathlib import Path

import main

# ---------- dựng brain mẫu ----------
goc = Path(tempfile.mkdtemp(prefix="brain-tg-td-"))
(goc / "wiki" / "03 - UPS").mkdir(parents=True)
(goc / "wiki" / "02 - Lam mat").mkdir(parents=True)
(goc / "sources" / "00 - Tong quan").mkdir(parents=True)

(goc / "wiki" / "03 - UPS" / "Danh Muc UPS.md").write_text(
    "# Danh mục UPS IDC\n\n"
    "- 4 UPS Liebert NX300 300 kVA tại phòng UPS tầng 1.\n"
    "- 13 UPS EXL S1 400 kVA.\n"
    "- 2 UPS EXM 200 kVA và 1 UPS MGE 60 kVA.\n"
    "Tổng cộng 20 UPS độc lập, chưa kể nhóm UPS5,6 qua tủ HĐB/MDP.\n",
    encoding="utf-8")
(goc / "wiki" / "02 - Lam mat" / "Chiller.md").write_text(
    "# Hệ thống làm mát\n\nChiller ly tâm cấp lạnh cho các phòng máy. "
    "Nhiệt độ phòng duy trì 22 độ C, độ ẩm 50%.\n",
    encoding="utf-8")
# File dài > trần mỗi file: vùng khớp nằm sâu ở giữa.
noi_dung_dai = ("Dòng đệm không liên quan.\n" * 200) + \
    "UPS NX300 300 kVA cần thay ắc quy sau 5 năm sử dụng.\n" + \
    ("Dòng đệm cuối trang.\n" * 200)
(goc / "sources" / "00 - Tong quan" / "Tai Lieu Dai.md").write_text(
    noi_dung_dai, encoding="utf-8")

# ---------- 1. câu tra cứu thật -> có trích đoạn, đúng file ----------
khoi = main._tg_trich_doan_vault(str(goc), "IDC có bao nhiêu UPS NX300 300 kVA")
assert khoi, "câu tra cứu UPS phải nạp được trích đoạn"
assert "ĐÃ NẠP SẴN" in khoi
assert "Danh Muc UPS.md" in khoi, khoi[:400]
assert "NX300" in khoi

# ---------- 2. câu xã giao -> không nạp gì ----------
assert main._tg_trich_doan_vault(str(goc), "chào em, hôm nay khỏe không") == ""
assert main._tg_trich_doan_vault(str(goc), "cảm ơn em nhiều nhé") == ""
# câu toàn từ dừng -> không có từ khoá -> rỗng
assert main._tg_trich_doan_vault(str(goc), "thế nào rồi") == ""

# ---------- 3. trần: tối đa 3 file, mỗi file bị cắt, tổng có trần ----------
khoi_dai = main._tg_trich_doan_vault(str(goc), "UPS NX300 300 kVA thay ắc quy")
assert "thay ắc quy" in khoi_dai or "thay ac quy" in khoi_dai.lower() or \
    "ắc quy" in khoi_dai, "vùng khớp sâu trong file dài vẫn phải lọt vào trích đoạn"
assert khoi_dai.count("### ") <= 3, "không nạp quá 3 file"
assert len(khoi_dai) <= 12000 + 1500, f"trích đoạn vượt trần: {len(khoi_dai)}"

# ---------- 4. brain trống/không tồn tại -> rỗng, không văng lỗi ----------
assert main._tg_trich_doan_vault(str(goc / "khong-co"), "UPS NX300") == ""
assert main._tg_trich_doan_vault("", "UPS NX300 300 kVA") == ""

# ---------- 5. dấu đặt tại nguồn trong _tg_answer_engine ----------
src = (SERVER / "main.py").read_text(encoding="utf-8")
eng = src[src.index("async def _tg_answer_engine("):src.index("async def _tg_help_text(")]
assert "ĐỘ DÀI" in eng and "1.500 ký tự" in eng, "thiếu trần độ dài mềm trong khối trình bày Telegram"
assert "_tg_trich_doan_vault" in eng, "thiếu lời gọi nạp trích đoạn trong _tg_answer_engine"

print("OK test_tg_trich_doan_vault: nạp trích đoạn đúng file, xã giao không nạp, trần ký tự giữ, dấu nguồn đủ")

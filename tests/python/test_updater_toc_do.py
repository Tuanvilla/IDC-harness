"""Tối ưu tốc độ cập nhật (1.3.0): bỏ qua pip khi requirements.txt không đổi,
và hàm tải trước của vòng dò bản mới chịu được máy không có .git.

    python tests/python/test_updater_toc_do.py

Không chạm mạng, không chạy pip thật: `updater.run` được thay bằng hàm giả trả
nội dung requirements theo kịch bản, ROOT của updater trỏ vào thư mục tạm.

Cam kết an toàn của `pip_can_bo_qua`: chỉ True khi CHỨNG MINH được hai bản
giống hệt; mọi mơ hồ đều False (cứ cài như cũ). Ba ca False dưới đây quan trọng
không kém ca True - nới lỏng chúng là server mới có ngày thiếu thư viện.
"""
from _paths import ROOT, SERVER  # noqa: E402,F401  - nạp server/ vào sys.path
import os
import subprocess
import sys
import tempfile
from pathlib import Path

state = tempfile.mkdtemp(prefix="idc-updater-tocdo-")
os.environ["JAVIS_STATE_DIR"] = state
os.environ["BRAINS_DIR"] = str(Path(state) / "brains")
os.environ["JAVIS_SESSIONS_DB"] = str(Path(state) / "sessions.db")

import updater  # noqa: E402

_fails = []


def check(name, cond, them=""):
    print(("ok   " if cond else "FAIL ") + name + ((f"  [{them!r}]") if them and not cond else ""))
    if not cond:
        _fails.append(name)


NOI_DUNG = "requests==2.32.0\nhttpx>=0.27\n"


def _run_gia(noi_dung_cu, loi=False):
    def _f(cmd, timeout_s=300):
        if loi:
            return subprocess.CompletedProcess(cmd, 1, "", "fatal: path not in tree")
        return subprocess.CompletedProcess(cmd, 0, noi_dung_cu, "")
    return _f


goc_run, goc_root = updater.run, updater.ROOT
try:
    with tempfile.TemporaryDirectory() as td:
        goc_moi = Path(td)
        updater.ROOT = goc_moi

        (goc_moi / "requirements.txt").write_text(NOI_DUNG, encoding="utf-8")
        updater.run = _run_gia(NOI_DUNG)
        check("requirements giống hệt -> bỏ qua pip được",
              updater.pip_can_bo_qua("abc123") is True)

        updater.run = _run_gia(NOI_DUNG.replace("\n", "\r\n"))
        check("khác nhau chỉ ở kiểu xuống dòng CRLF/LF -> vẫn coi như giống",
              updater.pip_can_bo_qua("abc123") is True)

        updater.run = _run_gia("requests==2.31.0\nhttpx>=0.27\n")
        check("requirements khác nội dung -> KHÔNG bỏ qua",
              updater.pip_can_bo_qua("abc123") is False)

        updater.run = _run_gia("", loi=True)
        check("đọc requirements của bản cũ lỗi -> KHÔNG bỏ qua (an toàn trước)",
              updater.pip_can_bo_qua("abc123") is False)

        updater.run = _run_gia(NOI_DUNG)
        check("thiếu sha bản cũ -> KHÔNG bỏ qua",
              updater.pip_can_bo_qua("") is False)

        (goc_moi / "requirements.txt").unlink()
        check("đọc requirements của bản mới lỗi -> KHÔNG bỏ qua",
              updater.pip_can_bo_qua("abc123") is False)
finally:
    updater.run, updater.ROOT = goc_run, goc_root


# ---- Tải trước: máy không có .git thì im lặng bỏ qua, không nổ ----
import main  # noqa: E402

goc_proj = main.PROJECT_ROOT
try:
    with tempfile.TemporaryDirectory() as td:
        main.PROJECT_ROOT = Path(td)
        try:
            main._tai_truoc_ban_moi()
            check("tải trước trên máy không có .git: bỏ qua êm, không lỗi", True)
        except Exception as e:  # noqa: BLE001
            check("tải trước trên máy không có .git: bỏ qua êm, không lỗi", False, e)
finally:
    main.PROJECT_ROOT = goc_proj


# ---- Chuỗi pha trong bản kế hoạch khô phải khớp luồng mới ----
check("hàm tải trước tồn tại trong main", callable(getattr(main, "_tai_truoc_ban_moi", None)))
src_updater = (SERVER / "updater.py").read_text(encoding="utf-8")
check("updater còn đủ hai tối ưu: bỏ qua pip + dừng server sau khi gộp",
      "pip_can_bo_qua" in src_updater and "pip_bo_qua" in src_updater)

# main.py không nằm trong canary này: file 28 nghìn dòng còn sẵn vài em dash ở
# chú thích cũ (vd quanh _muc_quyen_luot_chat), không thuộc đợt sửa này.
for f in (SERVER / "updater.py", Path(__file__)):
    check(f"không em dash: {f.name}", chr(0x2014) not in f.read_text(encoding="utf-8"))

if _fails:
    print(f"\nFAIL - test_updater_toc_do: {len(_fails)} lỗi")
    raise SystemExit(1)
print("\nOK - test_updater_toc_do: tất cả pass")

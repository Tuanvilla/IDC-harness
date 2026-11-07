# Dung IDC Harness - CHI giet tien trinh cua IDC Harness: chu port 6868 (kem cay tien
# trinh cua no) + python chay tu thu muc nay. TUYET DOI khong quet theo mau chung
# 'server\main.py': Javis OS (D:\javis-os, port 7777) cung chay 'python.exe
# server\main.py' y het, ban cu cua script nay da giet ca Javis OS moi lan dung
# IDC Harness (phat hien 2026-11-07).
$killed = $false
$root = $PSScriptRoot

# 1) Chu port 6868: python con cua venv moi la thang giu port (python venv chi la
# launcher). Giet kem cay tien trinh con; tien trinh cha (launcher + cmd boc ngoai)
# tu thoat khi thang giu port chet.
$portPids = Get-NetTCPConnection -LocalPort 6868 -State Listen -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty OwningProcess -Unique
foreach ($p in $portPids) {
  if ($p -and $p -ne 0) {
    taskkill /F /T /PID $p >$null 2>&1
    if (-not $?) {
      Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
    }
    Write-Host "  - Da tat PID $p (chu port 6868)"
    $killed = $true
  }
}

# 2) Phong ho: python chay bang DUONG DAN TUYET DOI tu thu muc nay (vai luong khoi
# dong truyen duong dan day du thay vi 'server\main.py' tuong doi). Chi gioi han
# trong $root cua chinh script nay - khong dung tien trinh cua thu muc khac.
Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue | Where-Object {
  $_.CommandLine -and ($_.CommandLine -like "*$root*")
} | ForEach-Object {
  Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
  Write-Host "  - Da tat python PID $($_.ProcessId) (chay tu $root)"
  $killed = $true
}

if (-not $killed) { Write-Host '  (Khong thay server nao dang chay)' }
exit 0

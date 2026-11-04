#!/bin/bash
# ============================================================
# IDC Harness - one-line install for macOS, no "cannot be opened" block
#
#   curl -fsSL https://raw.githubusercontent.com/Tuanvilla/IDC-harness/main/packaging/macos/get-idc.sh | bash
#
# Downloads the same IDC-Harness-macOS.dmg the website links to, copies IDC Harness.app into
# Applications, then runs its first-time install right here in this Terminal window.
# Why no Gatekeeper prompt: macOS only checks files a browser saved (they carry a quarantine
# flag), and the app is not signed with an Apple Developer ID yet. A file curl downloads
# carries no such flag.
# ============================================================
set -euo pipefail

URL="https://github.com/Tuanvilla/IDC-harness/releases/download/desktop/IDC-Harness-macOS.dmg"
[ "$(uname -s)" = "Darwin" ] || { echo "This installer is for macOS. On Linux run ./install.sh from the repo."; exit 1; }

TMP="$(mktemp -d)"
MNT=""
cleanup() { [ -n "${MNT}" ] && hdiutil detach -quiet "${MNT}" 2>/dev/null; rm -rf "${TMP}"; }
trap cleanup EXIT

echo ""
echo "  IDC Harness: dang tai bo cai... (downloading)"
curl -fL --progress-bar -o "${TMP}/IDC-Harness-macOS.dmg" "${URL}"
MNT="$(hdiutil attach -nobrowse -readonly "${TMP}/IDC-Harness-macOS.dmg" | awk -F'\t' '/\/Volumes\//{print $NF}')"
[ -d "${MNT}/IDC Harness.app" ] || { echo "The disk image has no IDC Harness.app"; exit 1; }

# /Applications when it is writable (an admin account), else ~/Applications.
DEST="/Applications"
[ -w "${DEST}" ] || { DEST="${HOME}/Applications"; mkdir -p "${DEST}"; }
# Replace only the app bundle; the brain lives in ~/IDCHarness and is never touched here.
rm -rf "${DEST}/IDC Harness.app"
cp -R "${MNT}/IDC Harness.app" "${DEST}/"
xattr -dr com.apple.quarantine "${DEST}/IDC Harness.app" 2>/dev/null || true
echo "  Da chep IDC Harness vao ${DEST} (copied to ${DEST})"

APP="${DEST}/IDC Harness.app"
if [ -d "${HOME}/IDCHarness/.git" ] && [ -x "${HOME}/IDCHarness/.venv/bin/python" ]; then
  echo "  IDC Harness da cai san, dang mo... (already installed, opening)"
  open "${APP}"
  exit 0
fi
# First install in THIS window. stdin is the curl pipe, so give the installer the keyboard
# back: install.sh asks for the IDC Harness admin account and may ask for the Mac password.
bash "${APP}/Contents/Resources/bootstrap.sh" < /dev/tty

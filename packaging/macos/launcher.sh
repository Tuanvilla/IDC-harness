#!/bin/bash
# ============================================================
# IDC Harness.app (the one inside IDC-Harness-macOS.dmg) - what a double-click runs.
#
# First run (no IDC Harness in ~/IDCHarness yet): opens Terminal on bootstrap.sh, which checks the Mac,
# installs what is missing and starts IDC Harness. Terminal on purpose: the first install takes
# minutes and may ask for the Mac password once, so the person must SEE what happens.
# Every run after that: bin/idc-start.sh, which only opens the window when IDC Harness is already
# up and starts it first when it is not. It never restarts a running server.
#
# Unlike the in-repo "IDC Harness.app" (which must stay inside the repo folder), this bundle can
# live in /Applications: it finds IDC Harness through IDC_HOME, default ~/IDCHarness.
# ============================================================
IDC_HOME="${IDC_HOME:-$HOME/IDCHarness}"
RES="$(cd "$(dirname "$0")/../Resources" && pwd)"

if [ -d "${IDC_HOME}/.git" ] && [ -x "${IDC_HOME}/.venv/bin/python" ] && [ -x "${IDC_HOME}/bin/idc-start.sh" ]; then
  exec "${IDC_HOME}/bin/idc-start.sh"
fi

# macOS asks once whether "IDC Harness" may control Terminal. If the person clicks Don't Allow
# (or the prompt never shows), osascript fails and nothing would happen at all: fall back to
# putting the command on the clipboard, opening Terminal, and saying "paste it".
# Not `open -a Terminal bootstrap.sh`: a script copied off the downloaded .dmg carries the
# quarantine flag, and Gatekeeper blocks it when it is opened through LaunchServices.
if ! osascript - "${RES}/bootstrap.sh" "${IDC_HOME}" <<'AS' >/dev/null 2>&1
on run argv
  tell application "Terminal"
    activate
    do script "IDC_HOME=" & quoted form of (item 2 of argv) & " bash " & quoted form of (item 1 of argv)
  end tell
end run
AS
then
  # %q escapes spaces and quotes in a form both bash and zsh (the Terminal default) accept.
  printf 'IDC_HOME=%q bash %q\n' "${IDC_HOME}" "${RES}/bootstrap.sh" | pbcopy
  open -a Terminal
  osascript -e 'display alert "IDC Harness" message "Terminal is open. Paste (Cmd+V) and press Enter to install IDC Harness.\n\nTerminal da mo. Dan (Cmd+V) roi bam Enter de cai IDC Harness."' >/dev/null 2>&1 || true
fi

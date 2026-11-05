; ============================================================
; IDC Harness - Windows installer (Inno Setup 6), builds dist\IDC-Harness-Setup.exe
;
;   iscc /DAppVersion=0.439.0 packaging\windows\idc-setup.iss
;
; CI builds it in .github/workflows/desktop-installers.yml and publishes it on the
; "desktop" release. The .exe stays small: it carries bootstrap.ps1 and the icon only, and
; bootstrap.ps1 clones the newest IDC Harness and runs install.ps1 (see the header of that file
; for why it is a git clone).
;
; Per user, no admin rights asked by the wizard itself (PrivilegesRequired=lowest). Installing
; Git, Python or Node through winget may still show one Windows permission prompt.
;
; This file is UTF-8 WITH BOM: Inno Setup reads a file without BOM in the ANSI codepage, and
; the Vietnamese messages below would turn into garbage.
; ============================================================

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId={{8F3C2A51-5D7E-4C0B-9E61-6A2D4B7C9E10}
AppName=IDC Harness
AppVersion={#AppVersion}
AppVerName=IDC Harness
AppPublisher=Nguyen Minh Quy
AppPublisherURL=https://github.com/Tuanvilla/IDC-harness
AppSupportURL=https://github.com/Tuanvilla/IDC-harness/issues
DefaultDirName={localappdata}\Programs\IDC Harness
; {app} is only the tiny stub holding bootstrap.ps1, so its page stays hidden. The folder
; that matters - where IDC Harness itself is cloned - is asked on a custom wizard page
; (InitializeWizard below), defaults to %USERPROFILE%\IDCHarness, and is persisted in the
; registry so the uninstaller can find it again.
DisableDirPage=yes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\..\dist
OutputBaseFilename=IDC-Harness-Setup
SetupIconFile=..\assets\idc.ico
UninstallDisplayIcon={app}\idc.ico
UninstallDisplayName=IDC Harness
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
CloseApplications=no
ShowLanguageDialog=auto
; IDC Harness logo in the wizard (packaging/make_icons.py draws them): the tall panel on the first and
; last page, the corner logo on the pages between. One file per display scale, Inno picks the
; closest, so the logo stays sharp on a 150% or 200% laptop screen.
WizardImageFile=..\assets\wizard-100.bmp,..\assets\wizard-125.bmp,..\assets\wizard-150.bmp,..\assets\wizard-175.bmp,..\assets\wizard-200.bmp,..\assets\wizard-225.bmp,..\assets\wizard-250.bmp
WizardSmallImageFile=..\assets\wizard-small-100.bmp,..\assets\wizard-small-125.bmp,..\assets\wizard-small-150.bmp,..\assets\wizard-small-175.bmp,..\assets\wizard-small-200.bmp,..\assets\wizard-small-225.bmp,..\assets\wizard-small-250.bmp
WizardImageStretch=no
VersionInfoCompany=Nguyen Minh Quy
VersionInfoDescription=IDC Harness Setup
VersionInfoProductName=IDC Harness
VersionInfoVersion={#AppVersion}
; Code signing, only when CI has a certificate (desktop-installers.yml passes /DSign and the
; matching /Sidc=... command). Without it the build stays unsigned, exactly as before.
#ifdef Sign
SignTool=idc
SignedUninstaller=yes
#endif

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
#if FileExists(AddBackslash(SourcePath) + "Vietnamese.isl")
Name: "vi"; MessagesFile: "Vietnamese.isl"
#endif

[CustomMessages]
en.DesktopIconTask=Put a IDC Harness icon on the Desktop
en.LaunchNow=Open IDC Harness now
en.StopApp=Stop IDC Harness
en.Bootstrapping=Checking this computer and installing what is missing (Git, Python, Node, AI brains). This takes a few minutes, follow the black window...
en.BootstrapFailed=Setup did not finish. The black window said what was missing.%n%nFix it, then run IDC-Harness-Setup.exe again: steps already done are skipped.%n%nLog: %1
en.DataKept=IDC Harness was removed from this computer.%n%nYour brain (notes, memory, settings) is kept in:%n%1%n%nDelete that folder by hand if you want everything gone.
en.PickDirTitle=Choose the IDC Harness folder
en.PickDirSub=IDC Harness itself, your brain (notes, memory, settings) and its updates all live in this folder. Pick any folder on any drive; it must be writable without administrator rights.
en.PickDirLabel=Install IDC Harness into:
#if FileExists(AddBackslash(SourcePath) + "Vietnamese.isl")
vi.DesktopIconTask=Đặt biểu tượng IDC Harness ra Desktop
vi.LaunchNow=Mở IDC Harness ngay
vi.StopApp=Tắt IDC Harness
vi.Bootstrapping=Đang kiểm tra máy và cài những gì còn thiếu (Git, Python, Node, các bộ não AI). Mất vài phút, theo dõi ở cửa sổ đen...
vi.BootstrapFailed=Cài đặt chưa xong. Cửa sổ đen đã ghi rõ máy còn thiếu gì.%n%nSửa xong thì chạy lại IDC-Harness-Setup.exe, các bước đã xong sẽ được bỏ qua.%n%nNhật ký: %1
vi.DataKept=Đã gỡ IDC Harness khỏi máy.%n%nBộ não của bạn (ghi chú, trí nhớ, cài đặt) vẫn được giữ ở:%n%1%n%nMuốn xoá sạch thì tự xoá thư mục đó.
vi.PickDirTitle=Chọn thư mục cài IDC Harness
vi.PickDirSub=IDC Harness, bộ não của bạn (ghi chú, trí nhớ, cài đặt) và các bản cập nhật đều nằm trong thư mục này. Chọn thư mục ở bất kỳ ổ đĩa nào, miễn là ghi được mà không cần quyền quản trị.
vi.PickDirLabel=Cài IDC Harness vào:
#endif

[Tasks]
Name: "desktopicon"; Description: "{cm:DesktopIconTask}"

[Files]
Source: "bootstrap.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\assets\idc.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; wscript + open-idc.vbs: no console window, and a second click only reopens the window
; instead of restarting the server (see the header of open-idc.vbs).
Name: "{autoprograms}\IDC Harness"; Filename: "{sys}\wscript.exe"; Parameters: "//nologo ""{code:CodeDir}\open-idc.vbs"""; WorkingDir: "{code:CodeDir}"; IconFilename: "{app}\idc.ico"
Name: "{autodesktop}\IDC Harness"; Filename: "{sys}\wscript.exe"; Parameters: "//nologo ""{code:CodeDir}\open-idc.vbs"""; WorkingDir: "{code:CodeDir}"; IconFilename: "{app}\idc.ico"; Tasks: desktopicon
Name: "{autoprograms}\{cm:StopApp}"; Filename: "{code:CodeDir}\stop-idc.bat"; WorkingDir: "{code:CodeDir}"; IconFilename: "{app}\idc.ico"

[Run]
Filename: "{sys}\wscript.exe"; Parameters: "//nologo ""{code:CodeDir}\open-idc.vbs"""; Description: "{cm:LaunchNow}"; Flags: postinstall nowait skipifsilent; Check: BootstrapOk

[UninstallDelete]
Type: files; Name: "{app}\install.log"

[Code]
var
  BootOk: Boolean;
  DirPage: TInputDirWizardPage;

{ Fallback home of the git clone (code + the user's brain). Must match the default -Dir of
  bootstrap.ps1. }
function DefaultCodeDir: String;
begin
  Result := ExpandConstant('{%USERPROFILE}') + '\IDCHarness';
end;

{ Where the git clone lives, in order: the folder picked on the wizard page (installer,
  after InitializeWizard); else the choice a previous install persisted (this is also how
  the UNINSTALLER finds it - it has no wizard page); else the default above. }
function CodeDir(Param: String): String;
begin
  if DirPage <> nil then
    Result := DirPage.Values[0]
  else if not (RegQueryStringValue(HKEY_CURRENT_USER, 'Software\IDC Harness', 'HomeDir', Result)
               and (Result <> '')) then
    Result := DefaultCodeDir;
end;

procedure InitializeWizard;
var
  Prev: String;
begin
  DirPage := CreateInputDirPage(wpWelcome,
    CustomMessage('PickDirTitle'), CustomMessage('PickDirSub'),
    CustomMessage('PickDirLabel'), False, '');
  DirPage.Add('');
  { Reinstalling? Preselect the folder the last install used, so the existing brain is
    found again instead of cloned fresh somewhere else. }
  if RegQueryStringValue(HKEY_CURRENT_USER, 'Software\IDC Harness', 'HomeDir', Prev)
     and (Prev <> '') then
    DirPage.Values[0] := Prev
  else
    DirPage.Values[0] := DefaultCodeDir;
end;

function BootstrapOk: Boolean;
begin
  Result := BootOk;
end;

function PowerShellExe: String;
begin
  Result := ExpandConstant('{sys}\WindowsPowerShell\v1.0\powershell.exe');
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  rc: Integer;
  args, log: String;
begin
  if CurStep = ssPostInstall then
  begin
    WizardForm.StatusLabel.Caption := CustomMessage('Bootstrapping');
    { Persist BEFORE bootstrap runs: if the install is interrupted, the uninstaller and
      the next setup run still know where the clone (and the brain) lives. }
    RegWriteStringValue(HKEY_CURRENT_USER, 'Software\IDC Harness', 'HomeDir', CodeDir(''));
    log := ExpandConstant('{app}\install.log');
    args := '-NoProfile -ExecutionPolicy Bypass -File "' + ExpandConstant('{app}\bootstrap.ps1') +
            '" -Dir "' + CodeDir('') + '" -LogFile "' + log + '"';
    BootOk := Exec(PowerShellExe, args, '', SW_SHOW, ewWaitUntilTerminated, rc) and (rc = 0);
    if not BootOk then
      SuppressibleMsgBox(FmtMessage(CustomMessage('BootstrapFailed'), [log]), mbError, MB_OK, IDOK);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  rc: Integer;
  stop: String;
begin
  if CurUninstallStep = usUninstall then
  begin
    stop := CodeDir('') + '\stop-idc.ps1';
    if FileExists(stop) then
      Exec(PowerShellExe, '-NoProfile -ExecutionPolicy Bypass -File "' + stop + '"', '', SW_HIDE, ewWaitUntilTerminated, rc);
    { Same entry install.ps1 and the dashboard toggle write (_AUTOSTART_NAME in server/main.py). }
    RegDeleteValue(HKEY_CURRENT_USER, 'Software\Microsoft\Windows\CurrentVersion\Run', 'IDCHarness');
  end;
  if CurUninstallStep = usPostUninstall then
    SuppressibleMsgBox(FmtMessage(CustomMessage('DataKept'), [CodeDir('')]), mbInformation, MB_OK, IDOK);
end;

; Inno Setup Script for WF EOL Tester
; Creates a Windows installer with all necessary files and shortcuts

#define MyAppName "WF EOL Tester"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "WaferFab"
#define MyAppExeName "WF_EOL_Tester.exe"
#define MyAppAssocName MyAppName + " File"
#define MyAppAssocExt ".wftest"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
; Basic application information
AppId={{WF-EOL-TESTER-2024}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output settings
OutputDir=build\installer
OutputBaseFilename=WF_EOL_Tester_Setup_{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Version information
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Installer
VersionInfoCopyright=Copyright (C) 2024 {#MyAppPublisher}

; Architecture (64-bit only)
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Uninstall settings
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

; License and readme (optional - uncomment if available)
;LicenseFile=LICENSE.txt
;InfoBeforeFile=README.md

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main executable and dependencies from PyInstaller output
Source: "dist\WF_EOL_Tester\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Configuration files (will be placed in app\configuration)
Source: "configuration\*"; DestDir: "{app}\configuration"; Flags: ignoreversion recursesubdirs createallsubdirs

; Driver files (AXL library)
Source: "src\driver\ajinextek\AXL(Library)\Library\64Bit\*.dll"; DestDir: "{app}\driver\AXL"; Flags: ignoreversion

[Icons]
; Start Menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop shortcut (if task selected)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Option to launch application after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up user-created files on uninstall (optional)
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\test_results"

[Code]
// Custom installation logic (optional)
procedure InitializeWizard;
begin
  // Custom wizard initialization if needed
end;

function InitializeSetup(): Boolean;
begin
  Result := True;

  // Check if .NET Framework is required (uncomment if needed)
  // if not IsDotNetInstalled(net45, 0) then
  // begin
  //   MsgBox('.NET Framework 4.5 or later is required.', mbInformation, MB_OK);
  //   Result := False;
  // end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Post-installation tasks
    // For example: Create initial configuration files
  end;
end;

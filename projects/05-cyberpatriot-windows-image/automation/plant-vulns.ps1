<#
.SYNOPSIS
  Creates a CyberPatriot-style Windows PRACTICE image (Project 05 solution / answer key).

.DESCRIPTION
  Introduces ~20 common misconfigurations, inert "persistence" markers, harmless noise and
  three forensic questions so a competitor can practise finding and fixing them. Persistence
  items only run `cmd.exe /c exit` or write a text file; nothing here is malware.

  RUN ONLY on the throwaway cp-windows VM, from an elevated PowerShell, after a snapshot:
    Set-ExecutionPolicy -Scope Process Bypass
    .\plant-vulns.ps1 -MainUser labadmin
#>
[CmdletBinding()]
param(
    [string]$MainUser = 'labadmin',
    [string]$ExpectedHost = 'CP-WINDOWS'
)
$ErrorActionPreference = 'Continue'

# ---- Safety guards ----
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) { Write-Error 'Run from an elevated PowerShell.'; exit 1 }
if ($env:COMPUTERNAME -ne $ExpectedHost) {
    Write-Error "Computer name is $env:COMPUTERNAME, expected $ExpectedHost. Rename-Computer $ExpectedHost (practice VM only), reboot, rerun."
    exit 1
}
$answer = Read-Host "This will intentionally WEAKEN this machine. Type PRACTICE to continue"
if ($answer -ne 'PRACTICE') { Write-Host 'Aborted.'; exit 1 }

function New-PracticeUser([string]$Name, [string]$Password) {
    if (-not (Get-LocalUser -Name $Name -ErrorAction SilentlyContinue)) {
        $sec = ConvertTo-SecureString $Password -AsPlainText -Force
        New-LocalUser -Name $Name -Password $sec -PasswordNeverExpires | Out-Null
    }
    Add-LocalGroupMember -Group 'Users' -Member $Name -ErrorAction SilentlyContinue
}

Write-Host '[*] Users: authorized noise + unauthorized accounts'
New-PracticeUser 'jlee'      'Welcome1!'      # authorized STANDARD user (README)
New-PracticeUser 'mgarcia'   'Welcome1!'      # authorized STANDARD user
New-PracticeUser 'svc_print' 'Printer2026!'   # authorized service account (noise: keep it!)
New-PracticeUser 'helpdesk2' 'Password1'      # 1: NOT authorized
Add-LocalGroupMember -Group 'Administrators' -Member 'helpdesk2' -ErrorAction SilentlyContinue
Add-LocalGroupMember -Group 'Administrators' -Member 'jlee' -ErrorAction SilentlyContinue   # 2: should be standard

Write-Host '[*] 3 enable Guest'
Enable-LocalUser -Name 'Guest' -ErrorAction SilentlyContinue

Write-Host '[*] 4 weak password + lockout policy'
net accounts /minpwlen:0 /maxpwage:unlimited /minpwage:0 /uniquepw:0 /lockoutthreshold:0 | Out-Null

Write-Host '[*] 5 disable logon auditing'
auditpol /set /subcategory:"Logon" /success:disable /failure:disable | Out-Null

Write-Host '[*] 6 firewall off'
Set-NetFirewallProfile -Profile Domain,Private,Public -Enabled False

Write-Host '[*] 7 RDP on WITHOUT Network Level Authentication (RDP itself is required: noise)'
$ts = 'HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server'
Set-ItemProperty -Path $ts -Name fDenyTSConnections -Value 0
Set-ItemProperty -Path "$ts\WinStations\RDP-Tcp" -Name UserAuthentication -Value 0

Write-Host '[*] 8 SMBv1 (may need a reboot; ignore if unavailable on this build)'
Enable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart -All -ErrorAction SilentlyContinue | Out-Null

Write-Host '[*] 9 world-writable share'
if (-not (Get-SmbShare -Name 'Files' -ErrorAction SilentlyContinue)) {
    New-SmbShare -Name 'Files' -Path 'C:\Users\Public' -FullAccess 'Everyone' | Out-Null
}

Write-Host '[*] 10 Remote Registry running'
Set-Service -Name RemoteRegistry -StartupType Automatic
Start-Service -Name RemoteRegistry -ErrorAction SilentlyContinue

Write-Host '[*] 11 scheduled task persistence (INERT)'
if (-not (Get-ScheduledTask -TaskName 'Updater' -ErrorAction SilentlyContinue)) {
    $action  = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument '/c exit'
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    Register-ScheduledTask -TaskName 'Updater' -Action $action -Trigger $trigger -User 'SYSTEM' -RunLevel Highest | Out-Null
}

Write-Host '[*] 12 Run-key persistence (INERT)'
Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run' -Name 'OneDriveHelper' -Value 'cmd.exe /c exit'

Write-Host '[*] 13 Defender exclusion on a user-writable folder'
Add-MpPreference -ExclusionPath 'C:\Users\Public' -ErrorAction SilentlyContinue

Write-Host '[*] 14 UAC: elevate admins without prompting'
Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System' -Name ConsentPromptBehaviorAdmin -Value 0

Write-Host '[*] 15 store LM hashes'
Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Lsa' -Name NoLMHash -Value 0

Write-Host '[*] 16 allow anonymous SAM enumeration'
Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Lsa' -Name RestrictAnonymousSAM -Value 0

Write-Host '[*] 17 prohibited media + plaintext password file'
New-Item -ItemType Directory -Force -Path 'C:\Users\Public\Music' | Out-Null
Set-Content -Path 'C:\Users\Public\Music\leaked_album.mp3' -Value 'not really an mp3'
$desk = "C:\Users\$MainUser\Desktop"
New-Item -ItemType Directory -Force -Path $desk | Out-Null
Set-Content -Path "$desk\passwords.txt" -Value "helpdesk2 / Password1`r`nvpn / Summer2026"

Write-Host '[*] Forensic questions'
Set-Content -Path "$desk\Forensic Question 1.txt" -Value @"
A scheduled task runs with the highest privileges every time someone logs on.
What is the name of the task?
ANSWER:
"@
Set-Content -Path "$desk\Forensic Question 2.txt" -Value @"
A folder has been excluded from Microsoft Defender scanning.
What is the full path of the excluded folder?
ANSWER:
"@
Set-Content -Path "$desk\Forensic Question 3.txt" -Value @"
Which unauthorized account was added to the local Administrators group?
ANSWER:
"@

Write-Host ''
Write-Host 'Done. Noise reminders: svc_print is authorized; RDP must stay ENABLED (with NLA).'
Write-Host 'Reboot once (SMBv1), then snapshot:  qm snapshot <vmid> planted'

<#
.SYNOPSIS
  Read-only Windows baseline audit (Project 05 PowerShell exercise, solution).
.DESCRIPTION
  Checks 10 controls and emits one object per control. Pipe it wherever you like:
    .\Audit-Windows.ps1 | Format-Table
    .\Audit-Windows.ps1 | Export-Csv audit.csv -NoTypeInformation
    .\Audit-Windows.ps1 | ConvertTo-Json | Set-Content audit.json
  Run elevated. Changes nothing.
#>
[CmdletBinding()]
param(
    [string[]]$AllowedAdmins = @('Administrator', 'labadmin')
)

function Result([string]$Id, [string]$Control, [bool]$Pass, [string]$Detail) {
    [pscustomobject]@{
        Id      = $Id
        Control = $Control
        Result  = if ($Pass) { 'PASS' } else { 'FAIL' }
        Detail  = $Detail
    }
}

# Parse `net accounts` into a hashtable (label -> value)
$net = @{}
foreach ($line in (net accounts)) {
    if ($line -match '^(.+?):\s+(.+)$') { $net[$Matches[1].Trim()] = $Matches[2].Trim() }
}

# ACC-01 Administrators group matches the allowlist
$admins = Get-LocalGroupMember -Group 'Administrators' | ForEach-Object { ($_.Name -split '\\')[-1] }
$extra  = @($admins | Where-Object { $_ -notin $AllowedAdmins })
Result 'ACC-01' 'Administrators match allowlist' ($extra.Count -eq 0) ("extra: " + ($extra -join ', '))

# ACC-02 Guest disabled
$guest = Get-LocalUser -Name 'Guest' -ErrorAction SilentlyContinue
Result 'ACC-02' 'Guest account disabled' (-not $guest.Enabled) "Enabled=$($guest.Enabled)"

# PWD-01 Minimum password length >= 10
$minLen = [int]($net['Minimum password length'])
Result 'PWD-01' 'Min password length >= 10' ($minLen -ge 10) "length=$minLen"

# PWD-02 Lockout threshold 1..10
$lockRaw = $net['Lockout threshold']
$lock = 0
$hasLock = [int]::TryParse($lockRaw, [ref]$lock) -and $lock -ge 1 -and $lock -le 10
Result 'PWD-02' 'Lockout threshold 1-10' $hasLock "threshold=$lockRaw"

# AUD-01 Logon auditing success + failure
$aud = (auditpol /get /subcategory:"Logon") -join ' '
Result 'AUD-01' 'Logon auditing S+F' ($aud -match 'Success and Failure') (($aud -replace '\s+', ' ').Trim())

# NET-01 Firewall on for all profiles
$fwOff = @(Get-NetFirewallProfile | Where-Object { -not $_.Enabled } | ForEach-Object Name)
Result 'NET-01' 'Firewall on (all profiles)' ($fwOff.Count -eq 0) ("disabled: " + ($fwOff -join ', '))

# NET-02 RDP off, or on with NLA
$ts  = Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server'
$nla = (Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp').UserAuthentication
$rdpOk = ($ts.fDenyTSConnections -eq 1) -or ($nla -eq 1)
Result 'NET-02' 'RDP disabled or NLA required' $rdpOk "fDenyTSConnections=$($ts.fDenyTSConnections) NLA=$nla"

# NET-03 SMBv1 disabled
$smb1 = Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -ErrorAction SilentlyContinue
Result 'NET-03' 'SMBv1 disabled' ($null -eq $smb1 -or $smb1.State -ne 'Enabled') "state=$($smb1.State)"

# PER-01 No non-Microsoft scheduled tasks running as SYSTEM at logon
$tasks = @(Get-ScheduledTask | Where-Object {
    $_.TaskPath -notlike '\Microsoft\*' -and $_.Principal.UserId -eq 'SYSTEM'
} | ForEach-Object TaskName)
Result 'PER-01' 'No custom SYSTEM tasks' ($tasks.Count -eq 0) ("tasks: " + ($tasks -join ', '))

# DEF-01 No Defender path exclusions
$excl = @((Get-MpPreference).ExclusionPath | Where-Object { $_ })
Result 'DEF-01' 'No Defender path exclusions' ($excl.Count -eq 0) ("exclusions: " + ($excl -join ', '))

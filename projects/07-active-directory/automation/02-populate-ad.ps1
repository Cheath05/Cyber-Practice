<#
.SYNOPSIS
  Populate lab.local with users/groups and INTENTIONAL training weaknesses (Project 07).
.DESCRIPTION
  Run elevated on dc01 after the forest is up. Creates a small, realistic org plus the
  misconfigurations you'll attack in Part B and fix in Part C. Lab use only. Every weakness is
  commented so you understand what you are planting. Passwords here are deliberately weak and
  are NOT secrets.
.EXAMPLE
  Set-ExecutionPolicy -Scope Process Bypass; .\02-populate-ad.ps1
#>
[CmdletBinding()]
param([string]$DnsRoot = 'lab.local')
$ErrorActionPreference = 'Stop'
Import-Module ActiveDirectory

if ((Get-ADDomain).DNSRoot -ne $DnsRoot) { throw "This is not the $DnsRoot domain." }
$answer = Read-Host "Populate $DnsRoot with intentionally vulnerable objects? Type PRACTICE"
if ($answer -ne 'PRACTICE') { return }

$base = (Get-ADDomain).DistinguishedName
foreach ($ou in 'Staff', 'IT', 'Servers') {
    if (-not (Get-ADOrganizationalUnit -Filter "Name -eq '$ou'" -ErrorAction SilentlyContinue)) {
        New-ADOrganizationalUnit -Name $ou -Path $base
    }
}
$staff = "OU=Staff,$base"; $it = "OU=IT,$base"
function Pw([string]$p) { ConvertTo-SecureString $p -AsPlainText -Force }

Write-Host '[*] Normal staff users'
$people = @(
    @{ Name = 'rwhite';  Display = 'Rachel White';  Pw = 'Autumn2026!' },
    @{ Name = 'tgreen';  Display = 'Tom Green';      Pw = 'Winter2026!' },
    @{ Name = 'achen';   Display = 'Amy Chen';       Pw = 'Spring2026!' }
)
foreach ($p in $people) {
    if (-not (Get-ADUser -Filter "SamAccountName -eq '$($p.Name)'" -EA SilentlyContinue)) {
        New-ADUser -Name $p.Display -SamAccountName $p.Name -AccountPassword (Pw $p.Pw) `
            -Path $staff -Enabled $true -ChangePasswordAtLogon $false
    }
}

Write-Host '[*] WEAKNESS 1: service account with an SPN and a weak password (Kerberoastable)'
if (-not (Get-ADUser -Filter "SamAccountName -eq 'svc_sql'" -EA SilentlyContinue)) {
    New-ADUser -Name 'svc_sql' -SamAccountName 'svc_sql' -AccountPassword (Pw 'Summer2026') `
        -Path $it -Enabled $true -PasswordNeverExpires $true
    Set-ADUser -Identity 'svc_sql' -ServicePrincipalNames @{Add = 'MSSQLSvc/sql01.lab.local:1433' }
}

Write-Host '[*] WEAKNESS 2: user with Kerberos pre-auth NOT required (AS-REP roastable)'
if (-not (Get-ADUser -Filter "SamAccountName -eq 'jmartin'" -EA SilentlyContinue)) {
    New-ADUser -Name 'Jo Martin' -SamAccountName 'jmartin' -AccountPassword (Pw 'Password123!') `
        -Path $staff -Enabled $true
}
Set-ADAccountControl -Identity 'jmartin' -DoesNotRequirePreAuth $true

Write-Host '[*] WEAKNESS 3: password stored in a user description (very common real mistake)'
Set-ADUser -Identity 'tgreen' -Description 'Temp account - password is Welcome2026!'

Write-Host '[*] WEAKNESS 4: attack path to Domain Admins via nested group'
if (-not (Get-ADGroup -Filter "Name -eq 'Helpdesk'" -EA SilentlyContinue)) {
    New-ADGroup -Name 'Helpdesk' -GroupScope Global -Path $it
}
Add-ADGroupMember -Identity 'Helpdesk' -Members 'rwhite'
# Helpdesk nested into a group that can reset privileged accounts -> BloodHound path.
Add-ADGroupMember -Identity 'Account Operators' -Members 'Helpdesk'

Write-Host ''
Write-Host 'Done. Snapshot dc01 and ws01 as ad-vulnerable, then start Part B.'
Write-Host 'Planted: svc_sql (Kerberoast), jmartin (AS-REP), tgreen description, Helpdesk->Account Operators.'

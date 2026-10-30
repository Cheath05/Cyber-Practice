<#
.SYNOPSIS
  Read-only Active Directory hygiene audit (Project 07 PowerShell exercise, solution).
.DESCRIPTION
  Reports common AD misconfigurations as objects. Needs the ActiveDirectory module (RSAT).
    .\Audit-AD.ps1 | Format-Table -AutoSize
    .\Audit-AD.ps1 | Export-Csv ad-audit.csv -NoTypeInformation
  Changes nothing.
#>
[CmdletBinding()]
param([int]$StaleDays = 90)
Import-Module ActiveDirectory

function Finding([string]$Check, [string]$Account, [string]$Severity, [string]$Detail) {
    [pscustomobject]@{ Check = $Check; Account = $Account; Severity = $Severity; Detail = $Detail }
}

# Kerberoastable: user accounts (not computers) with an SPN
Get-ADUser -Filter 'ServicePrincipalName -like "*"' -Properties ServicePrincipalName, PasswordLastSet |
    Where-Object { $_.SamAccountName -ne 'krbtgt' } |
    ForEach-Object {
        Finding 'Kerberoastable (user with SPN)' $_.SamAccountName 'High' `
            ("SPN: " + ($_.ServicePrincipalName -join '; ') + " | pwd set $($_.PasswordLastSet)")
    }

# AS-REP roastable: pre-authentication not required
Get-ADUser -Filter 'DoesNotRequirePreAuth -eq $true' -Properties DoesNotRequirePreAuth |
    ForEach-Object { Finding 'AS-REP roastable (no preauth)' $_.SamAccountName 'High' 'DoesNotRequirePreAuth = True' }

# Passwords that never expire (enabled accounts)
Get-ADUser -Filter 'PasswordNeverExpires -eq $true -and Enabled -eq $true' |
    ForEach-Object { Finding 'Password never expires' $_.SamAccountName 'Medium' 'PasswordNeverExpires = True' }

# Possible secrets in the description attribute
Get-ADUser -Filter * -Properties Description |
    Where-Object { $_.Description -match '(?i)pass(word)?|pwd|pw[:=]' } |
    ForEach-Object { Finding 'Possible password in description' $_.SamAccountName 'High' $_.Description }

# Stale enabled accounts
$cutoff = (Get-Date).AddDays(-$StaleDays)
Get-ADUser -Filter 'Enabled -eq $true' -Properties LastLogonDate |
    Where-Object { $_.LastLogonDate -and $_.LastLogonDate -lt $cutoff } |
    ForEach-Object { Finding "Stale account (>$StaleDays days)" $_.SamAccountName 'Low' "last logon $($_.LastLogonDate)" }

# Privileged group membership (review every name here)
foreach ($grp in 'Domain Admins', 'Enterprise Admins', 'Schema Admins', 'Account Operators') {
    Get-ADGroupMember -Identity $grp -Recursive -ErrorAction SilentlyContinue |
        ForEach-Object { Finding "Member of $grp" $_.SamAccountName 'Info' 'Confirm this access is required' }
}

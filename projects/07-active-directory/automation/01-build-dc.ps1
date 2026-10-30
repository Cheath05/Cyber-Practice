<#
.SYNOPSIS
  Promote this Server 2022 VM to a domain controller for a NEW forest lab.local (Project 07).
.DESCRIPTION
  Run elevated on dc01 (10.10.50.10) after setting the static IP and hostname. The VM reboots
  at the end. This is lab infrastructure for an isolated network; do not run it on a real network.
.EXAMPLE
  Set-ExecutionPolicy -Scope Process Bypass; .\01-build-dc.ps1
#>
[CmdletBinding()]
param(
    [string]$DomainName = 'lab.local',
    [string]$NetbiosName = 'LAB',
    [string]$ExpectedIp = '10.10.50.10'
)
$ErrorActionPreference = 'Stop'

$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '169.*' -and $_.IPAddress -ne '127.0.0.1' }).IPAddress
if ($ip -ne $ExpectedIp) {
    Write-Warning "This host's IP is $ip, expected $ExpectedIp. Set a static IP on the AD VLAN first."
    if ((Read-Host 'Continue anyway? (yes/no)') -ne 'yes') { return }
}

Write-Host '[*] Installing AD DS role...'
Install-WindowsFeature AD-Domain-Services -IncludeManagementTools

Write-Host '[*] A Directory Services Restore Mode (DSRM) password is required.'
$dsrm = Read-Host 'Enter a DSRM/Safe Mode password' -AsSecureString

Write-Host "[*] Promoting to a new forest: $DomainName (this reboots the VM)..."
Import-Module ADDSDeployment
Install-ADDSForest `
    -DomainName $DomainName `
    -DomainNetbiosName $NetbiosName `
    -InstallDns `
    -SafeModeAdministratorPassword $dsrm `
    -ForestMode 'WinThreshold' `
    -DomainMode 'WinThreshold' `
    -Force

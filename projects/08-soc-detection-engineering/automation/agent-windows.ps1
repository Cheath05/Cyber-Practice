<#
.SYNOPSIS
  Install the Wazuh agent + Sysmon on a lab Windows host and enable key audit subcategories (Project 08).
.DESCRIPTION
  Run elevated on dc01/ws01 with the AD TEMP egress rule ON. Pass the agent MSI URL that matches
  your manager version (from the Wazuh "Windows agent" docs page), e.g.
    .\agent-windows.ps1 -AgentMsiUrl 'https://packages.wazuh.com/4.x/windows/wazuh-agent-<VERSION>-1.msi'
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$AgentMsiUrl,
    [string]$Manager = '10.10.40.10',
    [string]$SysmonConfigUrl = 'https://raw.githubusercontent.com/SwiftOnSecurity/sysmon-config/master/sysmonconfig-export.xml'
)
$ErrorActionPreference = 'Stop'
$work = Join-Path $env:TEMP 'wazuh-setup'
New-Item -ItemType Directory -Force -Path $work | Out-Null

Write-Host '[*] Wazuh agent'
$msi = Join-Path $work 'wazuh-agent.msi'
Invoke-WebRequest -Uri $AgentMsiUrl -OutFile $msi
Start-Process msiexec.exe -Wait -ArgumentList "/i `"$msi`" /q WAZUH_MANAGER=$Manager"

Write-Host '[*] Sysmon (Sysinternals) with a community config'
$zip = Join-Path $work 'Sysmon.zip'
Invoke-WebRequest -Uri 'https://download.sysinternals.com/files/Sysmon.zip' -OutFile $zip
Expand-Archive -Path $zip -DestinationPath (Join-Path $work 'sysmon') -Force
$cfg = Join-Path $work 'sysmonconfig.xml'
Invoke-WebRequest -Uri $SysmonConfigUrl -OutFile $cfg
& (Join-Path $work 'sysmon\Sysmon64.exe') -accepteula -i $cfg

Write-Host '[*] Forward the Sysmon channel to Wazuh'
$conf = 'C:\Program Files (x86)\ossec-agent\ossec.conf'
$xml = Get-Content $conf -Raw
if ($xml -notmatch 'Microsoft-Windows-Sysmon/Operational') {
    $block = @"
  <localfile>
    <location>Microsoft-Windows-Sysmon/Operational</location>
    <log_format>eventchannel</log_format>
  </localfile>
</ossec_config>
"@
    $xml = $xml -replace '</ossec_config>\s*$', $block
    Set-Content -Path $conf -Value $xml -Encoding UTF8
}

Write-Host '[*] Audit subcategories used by the P07/P08 detections'
foreach ($sub in 'Logon', 'Kerberos Service Ticket Operations', 'Kerberos Authentication Service',
                 'Security Group Management', 'User Account Management', 'Other Object Access Events',
                 'Process Creation') {
    auditpol /set /subcategory:"$sub" /success:enable /failure:enable | Out-Null
}

Restart-Service -Name WazuhSvc
Write-Host 'Done. Confirm the agent is Active in the dashboard, then DISABLE the AD TEMP egress rule.'

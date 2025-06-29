<#
  .SYNOPSIS
  Install/update hosts files found at https://github.com/StevenBlack/hosts/.
  .DESCRIPTION
  Install/update consolidated hosts files found at
  https://github.com/StevenBlack/hosts/.
  .PARAMETER Alternate
  Update hosts with one of the alternate hosts file found in Steven's alternates
  directory.
  .PARAMETER OutFile
  Download the file only, do not update. Defaults to the current path.
  .PARAMETER NoBackup
  Do not create a backup file.
  .PARAMETER Force
  Force continue the script on errors.
  .PARAMETER Restore
  Restore the hosts file with the current skeleton backup if one exists and
  exits.
  .EXAMPLE
  PS> .\updateHostsWindows.ps1
  .EXAMPLE
  PS> .\updateHostsWindows.ps1 -OutFile '.\hosts'
  --------------------------------------------------------------------------------
  This Powershell script updates the Windows hosts file from one of the various                                           consolidated hosts files found at at: https://github.com/StevenBlack/hosts                                              --------------------------------------------------------------------------------                                        If updating the hosts file fails due to the hosts file being in use then it's                                           best to just keep trying. It's not always in use though it is hard to figure
  out when it's free so it's recommended to use while loop on $LASTEXITCODE to
  keep trying. E.G.: while ($LASTEXITCODE -gt 0) { .\updateHostsWindows.ps1 }.
  --------------------------------------------------------------------------------
  Use: Get-Help .\updateHostsWindows.ps1 -Detailed (or -Full) for more
  information.
  --------------------------------------------------------------------------------

  Checking if we are in a shell with administrative privileges.
  Attempting to get data from
  https://raw.githubusercontent.com/StevenBlack/hosts/refs/heads/master/hosts.
  Attempting to create output file .\hosts.
  Successfully created file: .\hosts.
#>
<#
╔════════════════════════════════════════════════════════════════════════╗
║ This Powershell script updates the Windows hosts file from one of the  ║
║ various consolidated hosts files found at at:                          ║
║ https://github.com/StevenBlack/hosts                                   ║
║ This script is written for backwards compatibility for Powershell 5.1+ ║
║ as PowerCore is not installed by default.                              ║
║                                                                        ║
║ Original script written by:                                            ║
║ Ian Pride (Lateralus138)                                               ║
║ faithnomoread@yahoo.com                                                ║
╚════════════════════════════════════════════════════════════════════════╝
#>
<#
╔═══════════════════╗
║ Parse parameters. ║
╚═══════════════════╝
#>
Param(
  [String]$Alternate,
  [String]$OutFile,
  [Switch]$NoBackup,
  [Switch]$Force,
  [Switch]$Restore
)
<#
╔═══════════════════╗
║ Global variables. ║
╚═══════════════════╝
#>
$seperator = '-' * 80
$baseHostsUrl = 'https://raw.githubusercontent.com/StevenBlack/hosts/refs/heads/master/'
$WriteStatus = {
  Param(
    [ValidateScript({ $_.Length -gt 0 })][String]$Message,
    [Switch]$IsError
  )
  switch ($IsError){
    $true { $color = 'Red' }
    default { $color = 'Green' }
  }
  $lastColor = $host.ui.RawUI.ForegroundColor
  $host.ui.RawUI.ForegroundColor = $color
  $Message
  $host.ui.RawUI.ForegroundColor = $lastColor
}
<#
╔════════════════════╗
║ About this script. ║
╚════════════════════╝
#>
@"

 $seperator
 This Powershell script updates the Windows hosts file from one of the various
 consolidated hosts files found at at: https://github.com/StevenBlack/hosts
 $seperator
 If updating the hosts file fails due to the hosts file being in use then it's
 best to just keep trying. It's not always in use though it is hard to figure
 out when it's free so it's recommended to use while loop on `$LASTEXITCODE to
 keep trying. E.G.: while (`$LASTEXITCODE -gt 0) { .\updateHostsWindows.ps1 }.
 $seperator
 Use: Get-Help .\updateHostsWindows.ps1 -Detailed (or -Full) for more
 information.
 $seperator

"@
<#
╔═════════════════════════════════╗
║ Check administrative privileges ║
╚═════════════════════════════════╝
#>
' Checking if we are in a shell with administrative privileges.'
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(`
    [Security.Principal.WindowsBuiltInRole] "Administrator")) {

$argString = ''
$PSBoundParameters.GetEnumerator() | Foreach-Object {
  $argString += ' -' + $_.Key + ' ' + $_.Value
}
  ' Attempting to restart this script as administrator.'
  try {
    Start-Process powershell `
        -ArgumentList "-NoLogo -NoExit -NoProfile -Command `"Set-Location $PWD`; $PSCommandPath $argString`"" `
        -Verb RunAs `
        -ErrorAction SilentlyContinue
  } catch {
    &$WriteStatus $(" " + $_.Exception.Message + "`n") -IsError
  }
  exit 1
}
if ($Alternate -eq 'True') { $Alternate = '' }
if ($OutFile -eq 'True') { $OutFile = '' }
$hostsFile = $Env:SystemRoot + '\System32\drivers\etc\hosts'
$hostsSkeleton = $hostsFile + '.skel'
<#
╔══════════════════════╗
║ Restore last backup. ║
╚══════════════════════╝
#>
if ($Restore){
  Write-Host " Attempting to restore $hostsSkeleton"
  if (-not (Test-Path -Path $hostsSkeleton -PathType Leaf )) {
    &$WriteStatus $(' ' + $hostsSkeleton + " not found.`n") -IsError
    exit 2
  }
  try {
    Copy-Item -Path $hostsSkeleton -Destination $hostsFile -ErrorAction Stop
    $successMessage =
@"
 Successfully restored $hostsSkeleton to $hostsFile.

"@
    &$WriteStatus $successMessage
  } catch {
    &$WriteStatus $(
      " Could not restore the hosts file.`n " +
      $_.InvocationInfo.MyCommand.Name + ': ' + $_.Exception.Message + "`n If the file was in use please try again. It will eventually be free.`n"
    ) -IsError
    exit 3
  }
  exit 0
}
<#
╔════════════════════════════╗
║ Backup current hosts file. ║
╚════════════════════════════╝
#>
if (-not ($OutFile)){
  switch ($NoBackup){
    $true { " No backup will be created." }
    default {
    " Attempting to create a back up of $hostsFile."
      try {
        Copy-Item -Path $hostsFile -Destination $hostsSkeleton -ErrorAction Stop
        $successMessage =
@"
 Successfully created a backup of the current hosts file at
 $hostsSkeleton.
"@
        &$WriteStatus $successMessage
      } catch {
        &$WriteStatus $(
          " Could not create a backup of the hosts file.`n " +
          $_.InvocationInfo.MyCommand.Name + ': ' + $_.Exception.Message
        ) -IsError
        if (-not ($Force)) {
          &$WriteStatus " This script will now exit (use the -Force switch to force continue on error).`n" -IsError
          exit 4
        }
      }
      
    }
  }
}
<#
╔══════════════════════════╗
║ Select which hosts file. ║
╚══════════════════════════╝
#>
switch ($Alternate.Length -gt 0) {
  $true { $hostsUrl = $baseHostsUrl + 'alternates/' + $Alternate + '/hosts' }
  default { $hostsUrl = $baseHostsUrl + 'hosts' }
}
<#
╔═════════════════════════════╗
║ Get remote hosts file data. ║
╚═════════════════════════════╝
#>
try {
  " Attempting to get data from`n $hostsUrl."
  $response = Invoke-WebRequest -Uri $hostsUrl
} catch {
  &$WriteStatus $(' ' + $_.Exception.Message + "`n") -IsError
  exit 5
}
if (-not($response.StatusDescription -eq 'OK')) {
  &$WriteStatus $(
    " Could not retrieve a valid reponse from`n $hostsUrl. [" +
    $response.StatusCode + '] ' + $response.StatusDescription + "`n"
  ) -IsError
  exit 6
}
<#
╔══════════════════════════════════╗
║ Install, update, or create file. ║
╚══════════════════════════════════╝
#>
if ($OutFile.Length -gt 0){
  " Attempting to create output file $OutFile."
  try {
    $response.Content | Out-File -FilePath $OutFile -Encoding utf8
  } catch {
    &$WriteStatus $(
      " Could not create file: $OutFile.`n " + $_.Exception.Message + "`n"
    ) -IsError
    exit 7
  }
  &$WriteStatus " Successfully created file: $OutFile.`n"
  exit 0
}
" Attempting to update $hostsFile."
try {
  $response.Content | Out-File -FilePath $hostsFile -Encoding utf8
} catch {
  &$WriteStatus $(
    " Could not update: $hostsFile.`n " + $_.Exception.Message + "`n"
  ) -IsError
  exit 8
}
&$WriteStatus " Successfully updated: $hostsFile.`n"
<#
╔═════════════════════════════════════════════════════════════════════════════════╗
║ If the system hosts file has been installed or update then flush the DNS cache. ║
╚═════════════════════════════════════════════════════════════════════════════════╝
#>
try {
  " Attempting to flush the DNS cache."
  ipconfig /flushdns
} catch {
  &$WriteStatus $(
    " Could not flush the DNS cache.`n" + $_.Exception.Message + "`n"
  ) -IsError
  exit 9
}
&$WriteStatus " Successfully flushed the DNS cache.`n"
exit 0

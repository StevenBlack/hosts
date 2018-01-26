function Update-HostsFile
{
    <#
    .SYNOPSIS
    This CmdLet downloads the unified hosts file with optional extensions from 
    https://github.com/StevenBlack/hosts and copies it to the correct folder on Windows machines. 

    .PARAMETER UnifiedOnly
    Downloads only the base hosts file without extensions

    .PARAMETER Fakenews
    Downloads the base hosts file with the Fakenews extension

    .PARAMETER Gambling
    Downloads the base hosts file with the Gambling extension

    .PARAMETER Social
    Downloads the base hosts file with the Social extension

    .PARAMETER Porn
    Downloads the base hosts file with the Porn extension

    .PARAMETER All
    Downloads the base hosts file with all extensions

    .PARAMETER WhitelistFilePath
    Path to a file which contains a list with domains which need to be whitelisted. The domains will
    be cut out of the hosts file. 
    The file must only contain the domains seperated be new line.

    .PARAMETER BlackListFilePath
    Path to a file which contains a list with domains which need to be blacklisted. The domains will
    be appended to the end of the hosts file. 
    The file must only contain the domains seperated be new line.

    .PARAMETER BackupOldHostsFile
    Tells the function to backup the original hosts file.

    .EXAMPLE
    C:\PS> Update-HostsFile
    Downloads the file without extensions and writes the content into 
    %SYSTEMROOT%\System32\etc\drivers\hosts

    .EXAMPLE
    C:\PS> Update-HostsFile -FakeNews -Social
    Downloads the file with the social and Fakenews extensions and writes the content into 
    %SYSTEMROOT%\System32\etc\drivers\hosts. You can combine any of the extensions.

    .EXAMPLE
    C:\PS> Update-HostsFile -Gambling -Social -WhiteListFilePath \\share\whitelist.txt 
    Downloads the file with the social and Gambling extensions, cuts out the whitelisted domains
    and writes the content into %SYSTEMROOT%\System32\etc\drivers\hosts. 

    .EXAMPLE
    C:\PS> Update-HostsFile -Gambling -Social -WhiteListFilePath \\share\whitelist.txt -BlackListFilePath \\share\blacklist.txt
    Downloads the file with the social and Gambling extensions, cuts out the whitelisted domains,
    appends the blacklisted domains and writes the content into %SYSTEMROOT%\System32\etc\drivers\hosts. 

    .LINK
    https://github.com/StevenBlack/hosts
    #>
    [cmdletBinding(DefaultParameterSetName='UnifiedOnly')]
    param
    (
        [Switch]
        [Parameter(ParameterSetName='UnifiedOnly',Mandatory=$false)]
        $UnifiedOnly,
        [Switch]
        [Parameter(ParameterSetName='Extension',Mandatory=$false)]
        $Fakenews,
        [Switch]
        [Parameter(ParameterSetName='Extension',Mandatory=$false)]
        $Gambling,
        [Switch]
        [Parameter(ParameterSetName='Extension',Mandatory=$false)]
        $Social,
        [Switch]
        [Parameter(ParameterSetName='Extension',Mandatory=$false)]
        $Porn,
        [Parameter(ParameterSetName='All',Mandatory=$false)]
        [Switch]
        $All,
        [Parameter()]
        [ValidateScript({ Test-Path -Path $_ -PathType Leaf})]
        [string]
        $WhitelistFilePath,
        [ValidateScript({ Test-Path -Path $_ -PathType Leaf})]
        [string]
        $BlackListFilePath,
        [switch]
        $BackupOldHostsFile
    )
    if(-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))
    {
        throw 'This script requires local administrator privilege'
    }

    $BaseUri = 'https://raw.githubusercontent.com/StevenBlack/hosts/master'
    if($PSBoundParameters.ContainsKey('All'))
    {
        $null = $PSBoundParameters.Remove('All')
        $null = $PSBoundParameters.Add('Fakenews',$true)
        $null = $PSBoundParameters.Add('Gambling',$true)
        $null = $PSBoundParameters.Add('Social',$true)
        $null = $PSBoundParameters.Add('Porn',$true)
    }
    
    if($PSBoundParameters.Keys.Count -eq 0 -or $PSBoundParameters.ContainsKey('UnifiedOnly'))
    {
        Write-Verbose 'Processing UnifiedOnly Hosts file'
        $downloadUri = $BaseUri + '/hosts'
    }
    elseif($PSBoundParameters.Keys.Count -ge 1 -and -not $PSBoundParameters.ContainsKey('All'))
    {
        
        $downloadUri = $BaseUri + '/alternates/' + (( $PSBoundParameters.Keys|Where-Object {$_ -notmatch 'File'}|ForEach-Object {$_.ToLower()} | Sort-Object ) -join '-') + '/hosts'
        Write-Verbose "Using $downloadUri"
    }
    try{
    $webResponse = Invoke-WebRequest -Uri $downloadUri -UseBasicParsing 
    }
    catch
    {
      throw $_
    }
    
    $hostsContent = $webResponse.Content
    $hostsArray = New-Object System.Collections.ArrayList  
    $null = $hostsArray.AddRange(($hostsContent -split '\n'))
    if(-not [string]::IsNullOrEmpty($WhitelistFilePath) )
    {
        
        $whiteListDomains = Get-Content -Path $WhitelistFilePath
        $hostsToWhiteList = New-Object System.Collections.ArrayList
        foreach($hostsEntry in $hostsArray)
        {
            if($whiteListDomains.Contains($hostsEntry.Split('\s')[1]))
            {
                $null = $hostsToWhiteList.Add($hostsEntry)
            }
        }
        foreach($htwl in $hostsToWhiteList)
        {
            $null= $hostsArray.Remove($htwl)
        }
    }
    if(-not [string]::IsNullOrEmpty($BlackListFilePath))
    {
        $null = $hostsArray.Add("")
        $null =         $hostsArray.Add("# Custom Blacklistentries from $BlackListFilePath")
        foreach($blacklistEntry in (Get-Content -Path $BlackListFilePath))
        {
            $null = $hostsArray.Add("0.0.0.0 $blacklistEntry")
        }
    }
    if($BackupOldHostsFile)
    {
        Copy-Item (Join-Path $env:windir 'System32\drivers\etc\hosts') (Join-Path $env:windir 'System32\drivers\etc\hosts.bak')
    }
    try
    {
        $stream = [System.IO.StreamWriter]::new( (Join-Path $env:windir 'System32\drivers\etc\hosts') )
        $hostsArray | ForEach-Object{ $stream.WriteLine( $_ ) }
    }
    finally
    {
        $stream.close()
    }
    $null = ipconfig.exe /flushdns
}

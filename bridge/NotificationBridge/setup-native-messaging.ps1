$hostPath = "C:\Users\hhoechter\NotificationBridge\bin\Debug\net6.0\NotificationBridge.exe"

$manifestContent = @{
    name = "com.loupedeck.notification_bridge"
    description = "Notification Bridge for Loupedeck"
    path = $hostPath
    type = "stdio"
    allowed_origins = @("chrome-extension://EXTENSION_ID_HERE/")
} | ConvertTo-Json

$manifestPath = "$env:LOCALAPPDATA\NotificationBridge"
New-Item -ItemType Directory -Force -Path $manifestPath | Out-Null

$manifestFile = "$manifestPath\com.loupedeck.notification_bridge.json"
$manifestContent | Out-File -FilePath $manifestFile -Encoding ASCII

Write-Output "Manifest created at: $manifestFile"
Write-Output ""
Write-Output "Contents:"
Get-Content $manifestFile
Write-Output ""

# Register with Chrome
$regPath = "HKCU:\Software\Google\Chrome\NativeMessagingHosts\com.loupedeck.notification_bridge"
New-Item -Path $regPath -Force | Out-Null
New-ItemProperty -Path $regPath -Name "(Default)" -Value $manifestFile -PropertyType String -Force | Out-Null

Write-Output "Registry key created at: $regPath"
Write-Output ""
Write-Output "IMPORTANT: You need to update the manifest file with your actual extension ID!"
Write-Output "1. Go to chrome://extensions/"
Write-Output "2. Find 'Notification Bridge for Loupedeck' extension"
Write-Output "3. Copy the ID (long string under the extension name)"
Write-Output "4. Edit $manifestFile"
Write-Output "5. Replace EXTENSION_ID_HERE with your actual extension ID"

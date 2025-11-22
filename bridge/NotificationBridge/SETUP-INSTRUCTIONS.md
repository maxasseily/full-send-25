# Native Messaging Setup - Next Steps

## Get Your Extension ID

1. Open Chrome and go to `chrome://extensions/`
2. Find "Notification Bridge for Loupedeck"
3. Enable "Developer mode" if not already enabled
4. Copy the **ID** (it's a long string like `abcdefghijklmnopqrstuvwxyz123456`)

## Update the Native Messaging Manifest

1. Open this file: `C:\Users\hhoechter\AppData\Local\NotificationBridge\com.loupedeck.notification_bridge.json`
2. Replace `EXTENSION_ID_HERE` with your actual extension ID
3. Save the file

The line should look like:
```json
"allowed_origins": [
    "chrome-extension://abcdefghijklmnopqrstuvwxyz123456/"
]
```

## Test the Connection

1. Reload the extension in Chrome (chrome://extensions/ → click reload button)
2. Open Discord or GitHub
3. Check the extension popup - you should see notifications
4. Open `C:\Users\hhoechter\AppData\Local\LoupedeckNotifications\notifications.json` 
   - This file should now contain the notification data!

## What's Happening

```
Browser Extension (content scripts)
    ↓
Background Worker (aggregates data)
    ↓
Native Messaging Host (C# app)
    ↓
JSON File: %LocalAppData%\LoupedeckNotifications\notifications.json
    ↓
Loupedeck Plugin (reads file every 60s)
    ↓
Creative Console (displays buttons)
```

The native host writes to:
`C:\Users\hhoechter\AppData\Local\LoupedeckNotifications\notifications.json`

Your Loupedeck plugin will read from this location.

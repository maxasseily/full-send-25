# Notification Bridge Extension

Chrome extension that monitors GitHub, Discord, and Slack for notifications and sends them to Loupedeck Creative Console.

## Installation

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right corner)
3. Click "Load unpacked"
4. Select this folder (`NotificationBridgeExtension`)
5. The extension icon should appear in your toolbar

## Testing

1. Open GitHub.com in a browser tab (make sure you're logged in)
2. Open Discord.com in another tab
3. Open Slack in another tab
4. Click the extension icon in your toolbar to see the current notification counts

## How It Works

- **Content Scripts**: Monitor each website's DOM for notification indicators
  - `content-github.js`: Watches GitHub notification bell
  - `content-discord.js`: Counts Discord mention badges and unread indicators
  - `content-slack.js`: Extracts notification count from page title and badges

- **Background Script**: Aggregates notifications from all tabs and stores them

- **Popup**: Shows current notification state for debugging

## Next Steps

The extension currently stores notification data in `chrome.storage.local`. To connect it to your Loupedeck plugin, we'll need to:

1. Create a native messaging host (C# console app)
2. Configure the manifest for native messaging
3. Have the background script send data to the native host
4. Have your Loupedeck plugin read from the native host or shared file

## Debugging

- Open DevTools Console on any monitored page to see content script logs
- Open extension popup and check the console for background script logs
- Go to `chrome://extensions/` and click "Inspect views: service worker" to debug background script

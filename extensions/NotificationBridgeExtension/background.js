// Background service worker for aggregating notifications
let notifications = {
  github: { count: 0, url: '', favicon: '', lastUpdated: 0 },
  discord: { count: 0, url: '', favicon: '', lastUpdated: 0 },
  slack: { count: 0, url: '', favicon: '', lastUpdated: 0 }
};

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Received message:', message);
  
  if (message.type === 'notification_update') {
    const { source, count, url, favicon } = message.data;
    
    notifications[source] = {
      count: count || 0,
      url: url || '',
      favicon: favicon || '',
      lastUpdated: Date.now()
    };
    
    // Store in chrome.storage for persistence
    chrome.storage.local.set({ notifications: notifications });
    
    // Try to send to native host (will implement later)
    sendToNativeHost(notifications);
    
    console.log('Updated notifications:', notifications);
    sendResponse({ success: true });
  } else if (message.type === 'get_notifications') {
    sendResponse({ notifications: notifications });
  }
  
  return true; // Keep channel open for async response
});

// Function to send data to native messaging host
function sendToNativeHost(data) {
  try {
    const port = chrome.runtime.connectNative('com.loupedeck.notification_bridge');
    
    port.onMessage.addListener((response) => {
      console.log('Native host response:', response);
    });
    
    port.onDisconnect.addListener(() => {
      if (chrome.runtime.lastError) {
        console.error('Native host error:', chrome.runtime.lastError.message);
      }
    });
    
    port.postMessage(data);
    console.log('Sent to native host:', data);
  } catch (error) {
    console.error('Failed to connect to native host:', error);
  }
  
  // Also keep local storage as backup
  chrome.storage.local.set({ 
    lastExport: {
      timestamp: Date.now(),
      data: data
    }
  });
}

// Periodic export to file system (temporary solution)
// Every 60 seconds, update the data
setInterval(() => {
  chrome.storage.local.get(['notifications'], (result) => {
    if (result.notifications) {
      console.log('Current notifications state:', result.notifications);
    }
  });
}, 60000);

// Initialize on install
chrome.runtime.onInstalled.addListener(() => {
  console.log('Notification Bridge Extension installed');
  chrome.storage.local.set({ notifications: notifications });
});

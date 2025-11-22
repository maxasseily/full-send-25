// GitHub notification monitoring
console.log('GitHub notification monitor loaded');

function extractGitHubNotifications() {
  try {
    // GitHub stores notification count in the notification indicator
    // Look for notification bell icon with badge
    const notificationBell = document.querySelector('[data-target="notification-indicator.link"]');
    const notificationBadge = document.querySelector('.mail-status.unread');
    
    let count = 0;
    let url = 'https://github.com/notifications';
    
    // Try multiple selectors for notification count
    if (notificationBadge) {
      count = 1; // Has unread notifications
    }
    
    // Alternative: check for the badge count
    const badge = document.querySelector('.notification-indicator .mail-status');
    if (badge && badge.textContent) {
      const badgeText = badge.textContent.trim();
      if (badgeText && !isNaN(badgeText)) {
        count = parseInt(badgeText, 10);
      }
    }
    
    // Get favicon
    const faviconLink = document.querySelector('link[rel="icon"]') || 
                        document.querySelector('link[rel="shortcut icon"]');
    const favicon = faviconLink ? faviconLink.href : 'https://github.githubassets.com/favicons/favicon.png';
    
    console.log('GitHub notifications found:', { count, url, favicon });
    
    // Send to background script
    chrome.runtime.sendMessage({
      type: 'notification_update',
      data: {
        source: 'github',
        count: count,
        url: url,
        favicon: favicon
      }
    }, (response) => {
      if (chrome.runtime.lastError) {
        console.error('Error sending message:', chrome.runtime.lastError);
      }
    });
    
    return { count, url, favicon };
  } catch (error) {
    console.error('Error extracting GitHub notifications:', error);
    return null;
  }
}

// Run immediately
extractGitHubNotifications();

// Monitor for changes using MutationObserver
const observer = new MutationObserver((mutations) => {
  extractGitHubNotifications();
});

// Wait for page to be ready
function startObserving() {
  const targetNode = document.querySelector('body');
  if (targetNode) {
    observer.observe(targetNode, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['class', 'data-count']
    });
    console.log('GitHub observer started');
  } else {
    setTimeout(startObserving, 1000);
  }
}

// Start observing after a short delay
setTimeout(startObserving, 2000);

// Also check periodically (every 30 seconds)
setInterval(extractGitHubNotifications, 30000);

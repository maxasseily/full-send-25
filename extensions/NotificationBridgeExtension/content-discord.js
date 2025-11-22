// Discord notification monitoring
console.log('Discord notification monitor loaded');

function extractDiscordNotifications() {
  try {
    // Discord shows unread indicators in multiple ways:
    // 1. Red badge with number on server icons
    // 2. White dot for unread messages
    // 3. Mention badges (@mentions)
    
    let totalCount = 0;
    let url = 'https://discord.com/channels/@me';
    
    // Count mention badges (these are the red notification badges with numbers)
    const mentionBadges = document.querySelectorAll('[class*="numberBadge"]');
    mentionBadges.forEach(badge => {
      const text = badge.textContent.trim();
      if (text && !isNaN(text)) {
        totalCount += parseInt(text, 10);
      }
    });
    
    // If no specific count, check for any unread indicators
    if (totalCount === 0) {
      const unreadIndicators = document.querySelectorAll('[class*="unread"]');
      if (unreadIndicators.length > 0) {
        totalCount = unreadIndicators.length;
      }
    }
    
    // Get favicon
    const faviconLink = document.querySelector('link[rel="icon"]') || 
                        document.querySelector('link[rel="shortcut icon"]');
    const favicon = faviconLink ? faviconLink.href : 'https://discord.com/assets/847541504914fd33810e70a0ea73177e.ico';
    
    console.log('Discord notifications found:', { count: totalCount, url, favicon });
    
    // Send to background script
    chrome.runtime.sendMessage({
      type: 'notification_update',
      data: {
        source: 'discord',
        count: totalCount,
        url: url,
        favicon: favicon
      }
    }, (response) => {
      if (chrome.runtime.lastError) {
        console.error('Error sending message:', chrome.runtime.lastError);
      }
    });
    
    return { count: totalCount, url, favicon };
  } catch (error) {
    console.error('Error extracting Discord notifications:', error);
    return null;
  }
}

// Run immediately
setTimeout(extractDiscordNotifications, 3000); // Wait for Discord to load

// Monitor for changes
const observer = new MutationObserver((mutations) => {
  extractDiscordNotifications();
});

function startObserving() {
  const targetNode = document.querySelector('body');
  if (targetNode) {
    observer.observe(targetNode, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['class']
    });
    console.log('Discord observer started');
  } else {
    setTimeout(startObserving, 1000);
  }
}

setTimeout(startObserving, 3000);

// Also check periodically (every 30 seconds)
setInterval(extractDiscordNotifications, 30000);

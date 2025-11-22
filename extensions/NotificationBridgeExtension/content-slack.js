// Slack notification monitoring
console.log('Slack notification monitor loaded');

function extractSlackNotifications() {
  try {
    // Slack shows notifications in several ways:
    // 1. Badge count in title (e.g., "(3) Slack | My Workspace")
    // 2. Unread indicators on channels
    // 3. DM indicators
    
    let totalCount = 0;
    let url = window.location.href;
    
    // Try to extract from page title first
    const titleMatch = document.title.match(/^\((\d+)\)/);
    if (titleMatch) {
      totalCount = parseInt(titleMatch[1], 10);
    }
    
    // Alternative: count unread badges in sidebar
    if (totalCount === 0) {
      const unreadBadges = document.querySelectorAll('[data-qa="channel_sidebar_name_button"] .c-mention_badge');
      unreadBadges.forEach(badge => {
        const text = badge.textContent.trim();
        if (text && !isNaN(text)) {
          totalCount += parseInt(text, 10);
        } else if (text) {
          totalCount += 1; // Has unread but no specific count
        }
      });
    }
    
    // Count unreads in channel list (alternative selector)
    if (totalCount === 0) {
      const unreadIndicators = document.querySelectorAll('.p-channel_sidebar__badge');
      if (unreadIndicators.length > 0) {
        totalCount = unreadIndicators.length;
      }
    }
    
    // Get favicon
    const faviconLink = document.querySelector('link[rel="icon"]') || 
                        document.querySelector('link[rel="shortcut icon"]');
    const favicon = faviconLink ? faviconLink.href : 'https://a.slack-edge.com/80588/img/icons/favicon-32.png';
    
    console.log('Slack notifications found:', { count: totalCount, url, favicon });
    
    // Send to background script
    chrome.runtime.sendMessage({
      type: 'notification_update',
      data: {
        source: 'slack',
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
    console.error('Error extracting Slack notifications:', error);
    return null;
  }
}

// Run after Slack loads
setTimeout(extractSlackNotifications, 3000);

// Monitor title changes (Slack updates title with notification count)
const titleObserver = new MutationObserver((mutations) => {
  extractSlackNotifications();
});

const titleElement = document.querySelector('title');
if (titleElement) {
  titleObserver.observe(titleElement, {
    childList: true,
    characterData: true,
    subtree: true
  });
}

// Monitor DOM for badge changes
const observer = new MutationObserver((mutations) => {
  extractSlackNotifications();
});

function startObserving() {
  const targetNode = document.querySelector('body');
  if (targetNode) {
    observer.observe(targetNode, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['class', 'data-qa']
    });
    console.log('Slack observer started');
  } else {
    setTimeout(startObserving, 1000);
  }
}

setTimeout(startObserving, 3000);

// Also check periodically (every 30 seconds)
setInterval(extractSlackNotifications, 30000);

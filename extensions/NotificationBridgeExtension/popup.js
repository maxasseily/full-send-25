// Popup script to display current notification state
function updatePopup() {
  chrome.storage.local.get(['notifications'], (result) => {
    const notifications = result.notifications || {};
    const container = document.getElementById('notifications');
    const statusDiv = document.getElementById('status');
    
    container.innerHTML = '';
    
    const sources = ['github', 'discord', 'slack'];
    sources.forEach(source => {
      const data = notifications[source] || { count: 0, url: '', favicon: '' };
      
      const item = document.createElement('div');
      item.className = 'notification-item';
      
      const favicon = data.favicon || `https://www.google.com/s2/favicons?domain=${source}.com`;
      
      item.innerHTML = `
        <img src="${favicon}" alt="${source}">
        <div class="notification-info">
          <div class="source-name">${source.charAt(0).toUpperCase() + source.slice(1)}</div>
          <div class="count">${data.count > 0 ? data.count + ' unread' : 'No notifications'}</div>
        </div>
        ${data.count > 0 ? `<span class="badge">${data.count}</span>` : ''}
      `;
      
      if (data.url) {
        item.style.cursor = 'pointer';
        item.onclick = () => {
          chrome.tabs.create({ url: data.url });
        };
      }
      
      container.appendChild(item);
    });
    
    const lastUpdate = Math.max(
      notifications.github?.lastUpdated || 0,
      notifications.discord?.lastUpdated || 0,
      notifications.slack?.lastUpdated || 0
    );
    
    if (lastUpdate > 0) {
      const timeAgo = Math.floor((Date.now() - lastUpdate) / 1000);
      statusDiv.textContent = `Last updated: ${timeAgo < 60 ? timeAgo + 's' : Math.floor(timeAgo/60) + 'm'} ago`;
    } else {
      statusDiv.textContent = 'No data yet. Visit GitHub, Discord, or Slack.';
    }
  });
}

// Initial load
updatePopup();

// Refresh button
document.getElementById('refresh').addEventListener('click', () => {
  // Request content scripts to re-check
  chrome.tabs.query({}, (tabs) => {
    tabs.forEach(tab => {
      if (tab.url.includes('github.com') || 
          tab.url.includes('discord.com') || 
          tab.url.includes('slack.com')) {
        chrome.tabs.reload(tab.id);
      }
    });
  });
  
  setTimeout(updatePopup, 2000);
});

// Listen for updates
chrome.storage.onChanged.addListener((changes, namespace) => {
  if (namespace === 'local' && changes.notifications) {
    updatePopup();
  }
});

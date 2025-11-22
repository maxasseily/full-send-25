namespace Loupedeck.GetPushNotificationsPlugin.Services
{
    using System;
    using System.IO;
    using System.Net.Http;
    using System.Threading;
    using System.Threading.Tasks;
    using Newtonsoft.Json;
    using Loupedeck.GetPushNotificationsPlugin.Models;

    public class NotificationService
    {
        private readonly string _notificationFilePath;
        private Timer _pollTimer;
        private NotificationContainer _currentNotifications;
        private readonly HttpClient _httpClient;
        private static readonly object _lock = new object();

        public event EventHandler<NotificationContainer> NotificationsUpdated;

        public NotificationService()
        {
            var localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            _notificationFilePath = Path.Combine(localAppData, "LoupedeckNotifications", "notifications.json");
            _httpClient = new HttpClient();
            _currentNotifications = new NotificationContainer
            {
                Github = new NotificationData(),
                Discord = new NotificationData(),
                Slack = new NotificationData()
            };
        }

        public void Start()
        {
            PluginLog.Info("NotificationService starting...");
            
            // Poll every 10 seconds
            _pollTimer = new Timer(PollNotifications, null, TimeSpan.Zero, TimeSpan.FromSeconds(10));
        }

        public void Stop()
        {
            PluginLog.Info("NotificationService stopping...");
            _pollTimer?.Dispose();
            _httpClient?.Dispose();
        }

        private void PollNotifications(object state)
        {
            try
            {
                if (!File.Exists(_notificationFilePath))
                {
                    PluginLog.Warning($"Notification file not found: {_notificationFilePath}");
                    return;
                }

                var json = File.ReadAllText(_notificationFilePath);
                var notifications = JsonConvert.DeserializeObject<NotificationContainer>(json);

                if (notifications != null)
                {
                    lock (_lock)
                    {
                        var hasChanges = HasChanges(_currentNotifications, notifications);
                        _currentNotifications = notifications;

                        if (hasChanges)
                        {
                            PluginLog.Info($"Notifications updated - GitHub: {notifications.Github?.Count ?? 0}, Discord: {notifications.Discord?.Count ?? 0}, Slack: {notifications.Slack?.Count ?? 0}");
                            NotificationsUpdated?.Invoke(this, notifications);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                PluginLog.Error($"Error polling notifications: {ex.Message}");
            }
        }

        private bool HasChanges(NotificationContainer old, NotificationContainer newData)
        {
            return old.Github?.Count != newData.Github?.Count ||
                   old.Discord?.Count != newData.Discord?.Count ||
                   old.Slack?.Count != newData.Slack?.Count;
        }

        public NotificationContainer GetCurrentNotifications()
        {
            lock (_lock)
            {
                return _currentNotifications;
            }
        }

        public async Task<BitmapImage> DownloadFaviconAsync(string faviconUrl)
        {
            try
            {
                if (string.IsNullOrEmpty(faviconUrl))
                    return null;

                var response = await _httpClient.GetAsync(faviconUrl);
                if (response.IsSuccessStatusCode)
                {
                    var imageBytes = await response.Content.ReadAsByteArrayAsync();
                    return BitmapImage.FromArray(imageBytes);
                }
            }
            catch (Exception ex)
            {
                PluginLog.Error($"Error downloading favicon from {faviconUrl}: {ex.Message}");
            }

            return null;
        }
    }
}

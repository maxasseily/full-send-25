namespace Loupedeck.GetPushNotificationsPlugin.Actions
{
    using System;
    using System.Diagnostics;
    using Loupedeck.GetPushNotificationsPlugin.Services;
    using Loupedeck.GetPushNotificationsPlugin.Models;

    public class DiscordNotificationCommand : PluginDynamicCommand
    {
        private NotificationService _notificationService;
        private NotificationData _currentData;
        private BitmapImage _cachedFavicon;

        public DiscordNotificationCommand()
            : base(displayName: "Discord", description: "Discord notifications", groupName: "Notifications")
        {
            _currentData = new NotificationData();
        }

        protected override bool OnLoad()
        {
            _notificationService = ((GetPushNotificationsPlugin)this.Plugin)?._notificationService;
            if (_notificationService != null)
            {
                _notificationService.NotificationsUpdated += OnNotificationsUpdated;
            }
            return true;
        }

        private void OnNotificationsUpdated(object sender, NotificationContainer notifications)
        {
            if (notifications?.Discord != null)
            {
                _currentData = notifications.Discord;
                this.ActionImageChanged();
                
                if (_cachedFavicon == null && !string.IsNullOrEmpty(_currentData.Favicon))
                {
                    _ = DownloadFaviconAsync();
                }
            }
        }

        private async System.Threading.Tasks.Task DownloadFaviconAsync()
        {
            try
            {
                _cachedFavicon = await _notificationService.DownloadFaviconAsync(_currentData.Favicon);
                if (_cachedFavicon != null)
                {
                    this.ActionImageChanged();
                }
            }
            catch (Exception ex)
            {
                PluginLog.Error($"Error downloading Discord favicon: {ex.Message}");
            }
        }

        protected override void RunCommand(string actionParameter)
        {
            if (!string.IsNullOrEmpty(_currentData?.Url))
            {
                try
                {
                    Process.Start(new ProcessStartInfo
                    {
                        FileName = _currentData.Url,
                        UseShellExecute = true
                    });
                    PluginLog.Info($"Opened Discord: {_currentData.Url}");
                }
                catch (Exception ex)
                {
                    PluginLog.Error($"Error opening Discord URL: {ex.Message}");
                }
            }
        }

        protected override BitmapImage GetCommandImage(string actionParameter, PluginImageSize imageSize)
        {
            using (var bitmapBuilder = new BitmapBuilder(imageSize))
            {
                if (_cachedFavicon != null)
                {
                    bitmapBuilder.SetBackgroundImage(_cachedFavicon);
                }
                else
                {
                    bitmapBuilder.Clear(BitmapColor.Black);
                }

                if (_currentData?.Count > 0)
                {
                    var countText = _currentData.Count > 99 ? "99+" : _currentData.Count.ToString();
                    
                    bitmapBuilder.FillRectangle(
                        imageSize.GetWidth() - 35, 5, 30, 20,
                        new BitmapColor(231, 76, 60)
                    );
                    
                    bitmapBuilder.DrawText(countText, 0, 0, imageSize.GetWidth(), imageSize.GetHeight(),
                        new BitmapColor(255, 255, 255), imageSize.GetWidth() - 35, 5);
                }
                else
                {
                    bitmapBuilder.DrawText("Discord\n0", BitmapColor.White);
                }

                return bitmapBuilder.ToImage();
            }
        }
    }
}

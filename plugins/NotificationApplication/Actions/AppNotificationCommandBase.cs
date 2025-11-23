namespace Loupedeck.ExamplePlugin.Actions
{
    using System;
    using System.Diagnostics;
    using Loupedeck.ExamplePlugin.Managers;
    using Loupedeck.ExamplePlugin.Models;
    using Loupedeck.ExamplePlugin.Utilities;

    // Base class for app notification commands.
    // Displays app icon with macOS-style notification badge overlay.
    public abstract class AppNotificationCommandBase : PluginDynamicCommand
    {
        protected readonly Int32 Slot;
        private readonly AppIconLoader _iconLoader;

        protected AppNotificationCommandBase(Int32 slot)
            : base(
                displayName: $"App Notification {slot + 1}",
                description: $"Shows app with notifications in slot {slot + 1}",
                groupName: "App Notifications")
        {
            this.Slot = slot;
            this._iconLoader = new AppIconLoader();

            // Subscribe to notification changes.
            NotificationManager.Instance.NotificationAppsChanged += this.OnNotificationAppsChanged;
        }

        // Called when the notification apps list changes.
        private void OnNotificationAppsChanged(Object sender, EventArgs e)
        {
            // Trigger UI update.
            this.ActionImageChanged();
        }

        // Gets the app for this slot, or null if no app.
        protected AppNotificationInfo GetApp()
        {
            return NotificationManager.Instance.GetAppAtSlot(this.Slot);
        }

        // This method is called when the user executes the command (presses the button).
        protected override void RunCommand(String actionParameter)
        {
            var app = this.GetApp();

            if (app == null || String.IsNullOrEmpty(app.AppName))
            {
                PluginLog.Verbose($"No app in notification slot {this.Slot}");
                return;
            }

            try
            {
                // Launch or switch to the app using macOS open command.
                var processStartInfo = new ProcessStartInfo
                {
                    FileName = "open",
                    Arguments = $"-a \"{app.AppName}\"",
                    UseShellExecute = true,
                    CreateNoWindow = true
                };

                Process.Start(processStartInfo);
                PluginLog.Info($"Opened app: {app.AppName} (had {app.BadgeCount} notifications)");
            }
            catch (Exception ex)
            {
                PluginLog.Error($"Failed to open {app.AppName}: {ex.Message}");
            }
        }

        // This method is called when Loupedeck needs to show the command name.
        protected override String GetCommandDisplayName(String actionParameter, PluginImageSize imageSize)
        {
            var app = this.GetApp();
            if (app == null)
            {
                return $"Slot {this.Slot + 1}";
            }

            // If there are notifications, append count to the app name.
            if (app.BadgeCount > 0)
            {
                var count = app.BadgeCount > 99 ? "99+" : app.BadgeCount.ToString();
                return $"{app.AppName} - ({count})";
            }

            return app.AppName;
        }

        // This method is called when Loupedeck needs to get the command image.
        protected override BitmapImage GetCommandImage(String actionParameter, PluginImageSize imageSize)
        {
            var app = this.GetApp();

            if (app == null || String.IsNullOrEmpty(app.AppName))
            {
                // No app in this slot - return empty/null.
                return null;
            }

            // Load the app icon.
            var icons = this._iconLoader.LoadAppIcons(app.AppName);
            BitmapImage baseIcon = null;

            if (icons.HasValue)
            {
                // Select appropriate icon size.
                baseIcon = (imageSize == PluginImageSize.Width90) ? icons.Value.Icon256 : icons.Value.Icon80;
            }

            // If no icon could be loaded, return null.
            if (baseIcon == null)
            {
                PluginLog.Verbose($"No icon available for {app.AppName}");
                return null;
            }

            // Return the app icon directly (notification count is shown in display name).
            return baseIcon;
        }
    }
}

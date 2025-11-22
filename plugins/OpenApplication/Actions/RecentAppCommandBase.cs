namespace Loupedeck.ExamplePlugin.Actions
{
    using System;
    using System.Diagnostics;
    using Loupedeck.ExamplePlugin.Managers;
    using Loupedeck.ExamplePlugin.Models;
    using Loupedeck.ExamplePlugin.Utilities;

    // Base class for recent app commands.
    public abstract class RecentAppCommandBase : PluginDynamicCommand
    {
        protected readonly Int32 Slot;
        protected readonly String DefaultAppName;
        private readonly AppIconLoader _iconLoader;

        protected RecentAppCommandBase(Int32 slot, String defaultAppName)
            : base(displayName: $"Recent App {slot + 1}", description: $"Opens recent app in slot {slot + 1}", groupName: "Recent Apps")
        {
            this.Slot = slot;
            this.DefaultAppName = defaultAppName;
            this._iconLoader = new AppIconLoader();

            // Subscribe to recent apps changes.
            RecentAppsManager.Instance.RecentAppsChanged += this.OnRecentAppsChanged;
        }

        // Called when the recent apps list changes.
        private void OnRecentAppsChanged(Object sender, EventArgs e)
        {
            // Trigger UI update.
            this.ActionImageChanged();
        }

        // Gets the app for this slot (recent app or default app).
        protected String GetAppName()
        {
            var app = RecentAppsManager.Instance.GetAppAtSlot(this.Slot);
            return app?.AppName ?? this.DefaultAppName;
        }

        // This method is called when the user executes the command.
        protected override void RunCommand(String actionParameter)
        {
            var appName = this.GetAppName();

            if (String.IsNullOrEmpty(appName))
            {
                PluginLog.Warning($"No app configured for slot {this.Slot}");
                return;
            }

            try
            {
                // Launch or switch to the app using macOS open command.
                var processStartInfo = new ProcessStartInfo
                {
                    FileName = "open",
                    Arguments = $"-a \"{appName}\"",
                    UseShellExecute = true,
                    CreateNoWindow = true
                };

                Process.Start(processStartInfo);
                PluginLog.Info($"Opened app: {appName}");
            }
            catch (Exception ex)
            {
                PluginLog.Error($"Failed to open {appName}: {ex.Message}");
            }
        }

        // This method is called when Loupedeck needs to show the command on the console or the UI.
        protected override String GetCommandDisplayName(String actionParameter, PluginImageSize imageSize)
        {
            var appName = this.GetAppName();
            return appName ?? $"Slot {this.Slot + 1}";
        }

        // This method is called when Loupedeck needs to get the command image.
        protected override BitmapImage GetCommandImage(String actionParameter, PluginImageSize imageSize)
        {
            var appName = this.GetAppName();

            if (String.IsNullOrEmpty(appName))
            {
                return null;
            }

            // Try to load the app icon.
            var icons = this._iconLoader.LoadAppIcons(appName);

            if (icons.HasValue)
            {
                // Return appropriate icon size based on the requested image size.
                if (imageSize == PluginImageSize.Width90)
                {
                    return icons.Value.Icon256;
                }
                else
                {
                    return icons.Value.Icon80;
                }
            }

            // If icon loading failed, return null (Loupedeck will show default).
            PluginLog.Verbose($"No icon available for {appName}");
            return null;
        }
    }
}

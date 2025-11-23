namespace Loupedeck.ExamplePlugin.Monitors
{
    using System;
    using System.Collections.Generic;
    using System.Diagnostics;
    using System.Text.RegularExpressions;
    using Loupedeck.ExamplePlugin.Managers;
    using Loupedeck.ExamplePlugin.Utilities;

    // Monitors Dock badge counts using AppleScript for apps that don't support lsappinfo.
    // This is specifically for apps like WhatsApp that display badges but don't set StatusLabel.
    public class DockBadgeMonitor
    {
        private Timer _timer;
        private readonly Object _lock = new Object();

        // Polling interval in milliseconds (5 seconds).
        private const Int32 PollingIntervalMs = 5000;

        // Apps that we know need Dock badge monitoring instead of lsappinfo
        private static readonly HashSet<String> AppsRequiringDockMonitoring = new HashSet<String>(StringComparer.OrdinalIgnoreCase)
        {
            "WhatsApp",
            "‎WhatsApp"  // With Unicode LTR mark
        };

        public DockBadgeMonitor()
        {
        }

        // Starts monitoring Dock badges.
        public void Start()
        {
            if (this._timer != null)
            {
                PluginLog.Warning("DockBadgeMonitor is already running");
                return;
            }

            PluginLog.Info("Starting DockBadgeMonitor for WhatsApp and other non-standard apps");

            // Do an initial poll.
            this.PollDockBadges();

            // Start the timer.
            this._timer = new Timer(this.OnTimerTick, null, PollingIntervalMs, PollingIntervalMs);
        }

        // Stops monitoring Dock badges.
        public void Stop()
        {
            if (this._timer == null)
            {
                return;
            }

            PluginLog.Info("Stopping DockBadgeMonitor");

            this._timer.Dispose();
            this._timer = null;
        }

        // Timer callback that polls for Dock badges.
        private void OnTimerTick(Object state)
        {
            try
            {
                this.PollDockBadges();
            }
            catch (Exception ex)
            {
                PluginLog.Error($"Error in DockBadgeMonitor timer tick: {ex.Message}");
            }
        }

        // Polls Dock for badge counts using AppleScript.
        private void PollDockBadges()
        {
            lock (this._lock)
            {
                try
                {
                    PluginLog.Verbose("Polling Dock for badge counts...");
                    var appNotifications = this.GetDockBadges();

                    if (appNotifications != null && appNotifications.Count > 0)
                    {
                        PluginLog.Info($"Found {appNotifications.Count} apps with Dock badges");

                        // Update the manager with the results
                        // Specify which apps we manage so we only clear those apps
                        NotificationManager.Instance.UpdateNotifications(appNotifications, AppsRequiringDockMonitoring);
                    }
                    else
                    {
                        // No badges found, but still need to clear any previously detected badges
                        // Pass empty dictionary with our managed apps list
                        var emptyDict = new Dictionary<String, Int32>();
                        NotificationManager.Instance.UpdateNotifications(emptyDict, AppsRequiringDockMonitoring);
                    }
                }
                catch (Exception ex)
                {
                    PluginLog.Error($"Failed to poll Dock badges: {ex.Message}");
                }
            }
        }

        // Gets badge counts from Dock using AppleScript.
        // Returns a dictionary of app name -> badge count.
        private Dictionary<String, Int32> GetDockBadges()
        {
            var result = new Dictionary<String, Int32>(StringComparer.OrdinalIgnoreCase);

            try
            {
                // AppleScript to get badge value for each app
                foreach (var appName in AppsRequiringDockMonitoring)
                {
                    var cleanAppName = appName.Trim('\u200E'); // Remove LTR mark
                    var badgeCount = this.GetAppDockBadge(cleanAppName);

                    if (badgeCount > 0)
                    {
                        result[cleanAppName] = badgeCount;
                        PluginLog.Info($"Dock badge found for '{cleanAppName}': {badgeCount}");
                    }
                }
            }
            catch (Exception ex)
            {
                PluginLog.Error($"Failed to get Dock badges: {ex.Message}");
            }

            return result;
        }

        // Gets the Dock badge count for a specific app using AppleScript.
        // Returns 0 if the app has no badge or if there's an error.
        private Int32 GetAppDockBadge(String appName)
        {
            try
            {
                // Write AppleScript to a temp file to avoid quoting issues
                var tempScript = System.IO.Path.GetTempFileName();
                try
                {
                    // Escape double quotes in app name for AppleScript
                    var escapedAppName = appName.Replace("\"", "\\\"");

                    var script = $@"tell application ""System Events""
    tell process ""Dock""
        try
            set dockItem to first UI element of list 1 whose name is ""{escapedAppName}""
            try
                set badgeValue to value of attribute ""AXStatusLabel"" of dockItem
                return badgeValue
            on error
                return """"
            end try
        on error
            return """"
        end try
    end tell
end tell";

                    System.IO.File.WriteAllText(tempScript, script);

                    var processStartInfo = new ProcessStartInfo
                    {
                        FileName = "osascript",
                        Arguments = tempScript,
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        CreateNoWindow = true
                    };

                    using (var process = Process.Start(processStartInfo))
                    {
                        var output = process.StandardOutput.ReadToEnd();
                        var error = process.StandardError.ReadToEnd();
                        process.WaitForExit();

                        if (!String.IsNullOrWhiteSpace(output))
                        {
                            PluginLog.Verbose($"Dock badge output for '{appName}': {output.Trim()}");

                            // Try to parse the badge value
                            var trimmedOutput = output.Trim();
                            if (!String.IsNullOrEmpty(trimmedOutput))
                            {
                                // Handle "100+" style badges by stripping the "+"
                                var badgeString = trimmedOutput.TrimEnd('+');

                                if (Int32.TryParse(badgeString, out var badgeCount))
                                {
                                    PluginLog.Info($"Parsed badge for '{appName}': {badgeCount} (raw: '{trimmedOutput}')");
                                    return badgeCount;
                                }
                            }
                        }

                        if (!String.IsNullOrWhiteSpace(error))
                        {
                            PluginLog.Verbose($"Dock badge error for '{appName}': {error.Trim()}");
                        }
                    }
                }
                finally
                {
                    // Clean up temp file
                    try
                    {
                        if (System.IO.File.Exists(tempScript))
                        {
                            System.IO.File.Delete(tempScript);
                        }
                    }
                    catch
                    {
                        // Ignore cleanup errors
                    }
                }
            }
            catch (Exception ex)
            {
                PluginLog.Verbose($"Failed to get Dock badge for '{appName}': {ex.Message}");
            }

            return 0;
        }
    }
}

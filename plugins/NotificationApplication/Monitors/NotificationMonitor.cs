namespace Loupedeck.ExamplePlugin.Monitors
{
    using System;
    using System.Collections.Generic;
    using System.Diagnostics;
    using System.Text.RegularExpressions;
    using System.Threading;
    using Loupedeck.ExamplePlugin.Managers;
    using Loupedeck.ExamplePlugin.Utilities;

    // Monitors macOS application notification badges using lsappinfo.
    public class NotificationMonitor
    {
        private Timer _timer;
        private readonly Object _lock = new Object();

        // Polling interval in milliseconds (5 seconds).
        private const Int32 PollingIntervalMs = 5000;

        // Regex to parse app names from lsappinfo list output
        // Example: 1) "AppName" ASN:...
        private static readonly Regex AppNameRegex = new Regex(
            @"^\s*\d+\)\s+""([^""]+)""\s+ASN:",
            RegexOptions.Compiled | RegexOptions.Multiline);

        // Regex to parse StatusLabel from lsappinfo info output
        // Example: "StatusLabel"={ "label"="5" }
        private static readonly Regex StatusLabelRegex = new Regex(
            @"""StatusLabel""=\{\s*""label""=""(\d+)""\s*\}",
            RegexOptions.Compiled);

        // Regex to detect NULL status (no badge)
        private static readonly Regex NullStatusRegex = new Regex(
            @"""StatusLabel""=\[\s*NULL\s*\]",
            RegexOptions.Compiled);

        // Alternative regex patterns for different StatusLabel formats
        private static readonly Regex[] AlternativeStatusLabelRegexes = new Regex[]
        {
            // Pattern 1: "label"="5" (without StatusLabel wrapper)
            new Regex(@"""label""=""(\d+)""", RegexOptions.Compiled),
            // Pattern 2: StatusLabel={ label="5" } (without quotes around keys)
            new Regex(@"StatusLabel=\{\s*label=""(\d+)""\s*\}", RegexOptions.Compiled),
            // Pattern 3: StatusLabel with empty label: "StatusLabel"={ "label"="" }
            new Regex(@"""StatusLabel""=\{\s*""label""=""""\s*\}", RegexOptions.Compiled),
            // Pattern 4: Just a number in the output
            new Regex(@"badge[""']?\s*[:=]\s*(\d+)", RegexOptions.Compiled | RegexOptions.IgnoreCase),
        };

        public NotificationMonitor()
        {
        }

        // Starts monitoring notification badges.
        public void Start()
        {
            if (this._timer != null)
            {
                PluginLog.Warning("NotificationMonitor is already running");
                return;
            }

            PluginLog.Info("Starting NotificationMonitor");

            // Do an initial poll.
            this.PollNotifications();

            // Start the timer.
            this._timer = new Timer(this.OnTimerTick, null, PollingIntervalMs, PollingIntervalMs);
        }

        // Stops monitoring notification badges.
        public void Stop()
        {
            if (this._timer == null)
            {
                return;
            }

            PluginLog.Info("Stopping NotificationMonitor");

            this._timer.Dispose();
            this._timer = null;
        }

        // Timer callback that polls for notification badges.
        private void OnTimerTick(Object state)
        {
            try
            {
                this.PollNotifications();
            }
            catch (Exception ex)
            {
                PluginLog.Error($"Error in NotificationMonitor timer tick: {ex.Message}");
            }
        }

        // Polls lsappinfo for notification badge counts.
        private void PollNotifications()
        {
            lock (this._lock)
            {
                try
                {
                    PluginLog.Verbose("Polling for notification badges...");
                    var appNotifications = this.GetNotificationBadges();

                    if (appNotifications != null)
                    {
                        if (appNotifications.Count > 0)
                        {
                            PluginLog.Info($"Updating NotificationManager with {appNotifications.Count} apps with badges");
                        }

                        // Always update the manager, even if the dictionary is empty
                        // (to clear badges that were removed).
                        NotificationManager.Instance.UpdateNotifications(appNotifications);
                    }
                    else
                    {
                        PluginLog.Warning("GetNotificationBadges returned null");
                    }
                }
                catch (Exception ex)
                {
                    PluginLog.Error($"Failed to poll notifications: {ex.Message}");
                }
            }
        }

        // Apps that are monitored by other monitors (e.g., DockBadgeMonitor).
        // We should not report these apps to avoid clearing their badges.
        private static readonly HashSet<String> AppsMonitoredElsewhere = new HashSet<String>(StringComparer.OrdinalIgnoreCase)
        {
            "WhatsApp",
            "‎WhatsApp"  // With Unicode LTR mark
        };

        // Runs lsappinfo to get notification badge counts for all apps.
        // Returns a dictionary of app name -> badge count.
        private Dictionary<String, Int32> GetNotificationBadges()
        {
            var result = new Dictionary<String, Int32>(StringComparer.OrdinalIgnoreCase);

            try
            {
                // Step 1: Get list of all running apps.
                var appNames = this.GetRunningAppNames();

                if (appNames == null || appNames.Count == 0)
                {
                    PluginLog.Verbose("No running apps found");
                    return result;
                }

                PluginLog.Verbose($"Found {appNames.Count} running apps, checking for badges");

                // Step 2: Query each app for StatusLabel.
                foreach (var appName in appNames)
                {
                    // Skip apps that are monitored by DockBadgeMonitor to avoid clearing their badges
                    if (AppsMonitoredElsewhere.Contains(appName))
                    {
                        PluginLog.Verbose($"Skipping {appName} (monitored by DockBadgeMonitor)");
                        continue;
                    }

                    var badgeCount = this.GetAppBadgeCountWithFallback(appName);

                    if (badgeCount > 0)
                    {
                        result[appName] = badgeCount;
                        PluginLog.Info($"Found notification badge: {appName} = {badgeCount}");
                    }
                }

                PluginLog.Verbose($"Found {result.Count} apps with notification badges");
            }
            catch (Exception ex)
            {
                PluginLog.Error($"Failed to get notification badges: {ex.Message}");
            }

            return result;
        }

        // Gets a list of all running application names.
        private List<String> GetRunningAppNames()
        {
            var appNames = new List<String>();

            try
            {
                var processStartInfo = new ProcessStartInfo
                {
                    FileName = "lsappinfo",
                    Arguments = "list",
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

                    if (process.ExitCode == 0 && !String.IsNullOrWhiteSpace(output))
                    {
                        // Parse app names from output using regex.
                        var matches = AppNameRegex.Matches(output);

                        foreach (Match match in matches)
                        {
                            if (match.Success && match.Groups.Count >= 2)
                            {
                                var appName = match.Groups[1].Value;
                                appNames.Add(appName);
                            }
                        }

                        // Log all detected running apps for debugging
                        if (appNames.Count > 0)
                        {
                            PluginLog.Verbose($"Running apps detected: {String.Join(", ", appNames)}");
                        }
                    }
                    else if (!String.IsNullOrEmpty(error))
                    {
                        PluginLog.Error($"lsappinfo list error: {error}");
                    }
                }
            }
            catch (Exception ex)
            {
                PluginLog.Error($"Failed to get running apps: {ex.Message}");
            }

            return appNames;
        }

        // Tries to get badge count with app name variations.
        // Handles bundle IDs and different name formats.
        private Int32 GetAppBadgeCountWithFallback(String appName)
        {
            // Try the original name first
            var badgeCount = this.GetAppBadgeCount(appName);
            if (badgeCount > 0)
            {
                return badgeCount;
            }

            // If the name looks like a bundle ID (e.g., "com.whatsapp.WhatsApp"),
            // try extracting the app name from the last component
            if (appName.Contains("."))
            {
                var parts = appName.Split('.');
                var simpleName = parts[parts.Length - 1];

                if (!String.Equals(simpleName, appName, StringComparison.OrdinalIgnoreCase))
                {
                    PluginLog.Verbose($"Trying simplified name '{simpleName}' for bundle ID '{appName}'");
                    badgeCount = this.GetAppBadgeCount(simpleName);
                    if (badgeCount > 0)
                    {
                        return badgeCount;
                    }
                }
            }

            return 0;
        }

        // Gets the badge count for a specific app.
        // Returns 0 if the app has no badge or if there's an error.
        private Int32 GetAppBadgeCount(String appName)
        {
            try
            {
                var processStartInfo = new ProcessStartInfo
                {
                    FileName = "lsappinfo",
                    Arguments = $"info -only StatusLabel -app \"{appName}\"",
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

                    // Log raw output for debugging
                    if (!String.IsNullOrWhiteSpace(output))
                    {
                        PluginLog.Verbose($"StatusLabel output for '{appName}': {output.Trim()}");
                    }

                    if (!String.IsNullOrWhiteSpace(error))
                    {
                        PluginLog.Warning($"StatusLabel error for '{appName}': {error.Trim()}");
                    }

                    if (process.ExitCode == 0 && !String.IsNullOrWhiteSpace(output))
                    {
                        // Check if StatusLabel is explicitly NULL (no badge)
                        if (NullStatusRegex.IsMatch(output))
                        {
                            PluginLog.Verbose($"App '{appName}' has NULL StatusLabel (no badge)");
                            return 0;
                        }

                        // Try primary regex pattern first
                        var match = StatusLabelRegex.Match(output);

                        if (match.Success && match.Groups.Count >= 2)
                        {
                            var badgeCountStr = match.Groups[1].Value;

                            if (Int32.TryParse(badgeCountStr, out var badgeCount))
                            {
                                PluginLog.Info($"Badge found for '{appName}': {badgeCount} (primary pattern)");
                                return badgeCount;
                            }
                        }

                        // Try alternative regex patterns
                        for (var i = 0; i < AlternativeStatusLabelRegexes.Length; i++)
                        {
                            match = AlternativeStatusLabelRegexes[i].Match(output);

                            if (match.Success)
                            {
                                // For pattern 3 (empty label), return 0
                                if (i == 2 && match.Groups.Count >= 1)
                                {
                                    PluginLog.Verbose($"App '{appName}' has empty badge label (alternative pattern {i + 1})");
                                    return 0;
                                }

                                if (match.Groups.Count >= 2)
                                {
                                    var badgeCountStr = match.Groups[1].Value;

                                    if (Int32.TryParse(badgeCountStr, out var badgeCount) && badgeCount > 0)
                                    {
                                        PluginLog.Info($"Badge found for '{appName}': {badgeCount} (alternative pattern {i + 1})");
                                        return badgeCount;
                                    }
                                }
                            }
                        }

                        // If we got output but no match, log it for debugging
                        PluginLog.Verbose($"No badge pattern matched for '{appName}', raw output: {output.Trim()}");
                    }
                    else if (process.ExitCode != 0)
                    {
                        PluginLog.Verbose($"lsappinfo returned exit code {process.ExitCode} for '{appName}'");
                    }
                }
            }
            catch (Exception ex)
            {
                PluginLog.Warning($"Exception getting badge for '{appName}': {ex.Message}");
            }

            return 0;
        }
    }
}

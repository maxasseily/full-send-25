namespace Loupedeck.ExamplePlugin.Managers
{
    using System;
    using System.Collections.Generic;
    using System.IO;
    using System.Linq;
    using Loupedeck.ExamplePlugin.Models;
    using Loupedeck.ExamplePlugin.Utilities;
    using Newtonsoft.Json;

    // Manages notification badges for all applications.
    // Tracks unlimited apps but surfaces only the top 8 by recency.
    public class NotificationManager
    {
        private const Int32 DisplaySlots = 8;
        private const Int32 MaxDaysToKeep = 7; // Prune apps with no badge for this many days

        // Apps monitored by specialized monitors (e.g., DockBadgeMonitor).
        // These apps should not be auto-cleared when missing from a status update.
        private static readonly HashSet<String> AppsWithDedicatedMonitors = new HashSet<String>(StringComparer.OrdinalIgnoreCase)
        {
            "WhatsApp",
            "‎WhatsApp"  // With Unicode LTR mark
        };

        // Singleton instance.
        private static NotificationManager _instance;
        public static NotificationManager Instance => _instance ?? (_instance = new NotificationManager());

        // Dictionary of all apps with notifications: app name -> info.
        private Dictionary<String, AppNotificationInfo> _allApps;

        // Cached list of top 8 apps by notification recency.
        private List<AppNotificationInfo> _top8Apps;

        // Path to the JSON file for persistence.
        private readonly String _persistencePath;

        // Lock for thread-safe access.
        private readonly Object _lock = new Object();

        // Event fired when the top 8 apps list changes.
        public event EventHandler NotificationAppsChanged;

        // Helper for loading app icons and paths.
        private readonly AppIconLoader _iconLoader;

        private NotificationManager()
        {
            this._allApps = new Dictionary<String, AppNotificationInfo>(StringComparer.OrdinalIgnoreCase);
            this._top8Apps = new List<AppNotificationInfo>();
            this._iconLoader = new AppIconLoader();

            // Set persistence path.
            var appDataPath = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
                "Library",
                "Application Support",
                "Logi",
                "LogiPluginService"
            );

            if (!Directory.Exists(appDataPath))
            {
                Directory.CreateDirectory(appDataPath);
            }

            this._persistencePath = Path.Combine(appDataPath, "AppNotifications.json");

            // Load persisted state.
            this.Load();
        }

        // Gets the app at the specified display slot (0-7), or null if no app in that slot.
        public AppNotificationInfo GetAppAtSlot(Int32 slot)
        {
            lock (this._lock)
            {
                if (slot < 0 || slot >= DisplaySlots)
                {
                    return null;
                }

                if (slot < this._top8Apps.Count)
                {
                    return this._top8Apps[slot];
                }

                return null;
            }
        }

        // Gets all top 8 apps (read-only copy).
        public List<AppNotificationInfo> GetTop8Apps()
        {
            lock (this._lock)
            {
                return new List<AppNotificationInfo>(this._top8Apps);
            }
        }

        // Updates notification badges based on current system state.
        // Called by NotificationMonitor with a dictionary of app name -> badge count.
        // appsUnderManagement: Optional set of app names this monitor is responsible for.
        //                      If provided, only apps in this set will be cleared when not seen.
        //                      If null, all apps (except dedicated monitor apps) can be cleared.
        public void UpdateNotifications(Dictionary<String, Int32> currentBadges, HashSet<String> appsUnderManagement = null)
        {
            if (currentBadges == null)
            {
                return;
            }

            var now = DateTime.Now;
            var top8Changed = false;
            var badgeCountChanged = false;

            lock (this._lock)
            {
                // Track which apps we've seen in this update.
                var seenApps = new HashSet<String>(StringComparer.OrdinalIgnoreCase);

                // Update or add apps with badges.
                foreach (var kvp in currentBadges)
                {
                    var appName = kvp.Key;
                    var newBadgeCount = kvp.Value;

                    seenApps.Add(appName);

                    if (this._allApps.TryGetValue(appName, out var existingApp))
                    {
                        // App exists - check if badge count changed.
                        if (existingApp.BadgeCount != newBadgeCount)
                        {
                            PluginLog.Info($"Badge changed for {appName}: {existingApp.BadgeCount} -> {newBadgeCount}");
                            badgeCountChanged = true;

                            // Badge count changed - update timestamp if it increased.
                            if (newBadgeCount > existingApp.BadgeCount)
                            {
                                existingApp.LastNotificationTime = now;
                                PluginLog.Info($"Badge increased for {appName}, updating LastNotificationTime");
                            }

                            existingApp.BadgeCount = newBadgeCount;
                            existingApp.LastSeenTime = now;
                        }
                        else
                        {
                            // Badge count same - just update last seen time.
                            existingApp.LastSeenTime = now;
                        }
                    }
                    else
                    {
                        // New app with badge - find its bundle path.
                        var bundlePath = this._iconLoader.FindAppBundle(appName);

                        var appInfo = new AppNotificationInfo(
                            appName,
                            bundlePath ?? String.Empty,
                            newBadgeCount,
                            now,  // LastNotificationTime
                            now   // LastSeenTime
                        );

                        this._allApps[appName] = appInfo;

                        PluginLog.Info($"New app with badge: {appName} ({newBadgeCount})");
                    }
                }

                // Clear badge count for apps not in current update (but keep them in the list).
                foreach (var app in this._allApps.Values.ToList())
                {
                    if (!seenApps.Contains(app.AppName))
                    {
                        // If appsUnderManagement is specified, only clear apps in that set
                        if (appsUnderManagement != null && !appsUnderManagement.Contains(app.AppName))
                        {
                            PluginLog.Verbose($"Skipping badge clear for {app.AppName} (not managed by this monitor)");
                            continue;
                        }

                        // Don't clear badges for apps monitored by dedicated monitors
                        if (AppsWithDedicatedMonitors.Contains(app.AppName))
                        {
                            PluginLog.Verbose($"Skipping badge clear for {app.AppName} (has dedicated monitor)");
                            continue;
                        }

                        if (app.BadgeCount > 0)
                        {
                            PluginLog.Info($"Badge cleared for {app.AppName}");
                            app.BadgeCount = 0;
                            badgeCountChanged = true;
                        }
                    }
                }

                // Prune apps with no badge for more than MaxDaysToKeep.
                var cutoffDate = now.AddDays(-MaxDaysToKeep);
                var appsToRemove = this._allApps.Values
                    .Where(app => app.BadgeCount == 0 && app.LastSeenTime < cutoffDate)
                    .Select(app => app.AppName)
                    .ToList();

                foreach (var appName in appsToRemove)
                {
                    this._allApps.Remove(appName);
                    PluginLog.Verbose($"Pruned old app: {appName}");
                }

                // Compute new top 8.
                var previousTop8 = this._top8Apps.Select(app => app.AppName).ToList();

                this._top8Apps = this._allApps.Values
                    .OrderByDescending(app => app.LastNotificationTime)
                    .Take(DisplaySlots)
                    .ToList();

                var currentTop8 = this._top8Apps.Select(app => app.AppName).ToList();

                // Check if top 8 changed.
                if (!previousTop8.SequenceEqual(currentTop8))
                {
                    top8Changed = true;
                    PluginLog.Info($"Top 8 apps changed. New list: {String.Join(", ", currentTop8)}");
                }
            }

            // Save and notify outside the lock.
            this.Save();

            // Fire event if top 8 list changed OR if any badge counts changed.
            if (top8Changed || badgeCountChanged)
            {
                this.OnNotificationAppsChanged();
            }
        }

        // Loads the notification apps from disk.
        private void Load()
        {
            try
            {
                if (File.Exists(this._persistencePath))
                {
                    var json = File.ReadAllText(this._persistencePath);
                    var loadedApps = JsonConvert.DeserializeObject<List<AppNotificationInfo>>(json);

                    if (loadedApps != null)
                    {
                        lock (this._lock)
                        {
                            // Convert list to dictionary.
                            this._allApps = loadedApps.ToDictionary(
                                app => app.AppName,
                                app => app,
                                StringComparer.OrdinalIgnoreCase
                            );

                            // Compute top 8.
                            this._top8Apps = this._allApps.Values
                                .OrderByDescending(app => app.LastNotificationTime)
                                .Take(DisplaySlots)
                                .ToList();
                        }

                        PluginLog.Info($"Loaded {this._allApps.Count} apps from disk, top 8 computed");
                    }
                }
            }
            catch (Exception ex)
            {
                PluginLog.Error($"Failed to load notification apps from disk: {ex.Message}");
            }
        }

        // Saves the notification apps to disk.
        private void Save()
        {
            try
            {
                String json;
                lock (this._lock)
                {
                    // Convert dictionary to list for serialization.
                    var appList = this._allApps.Values
                        .OrderByDescending(app => app.LastNotificationTime)
                        .ToList();

                    json = JsonConvert.SerializeObject(appList, Formatting.Indented);
                }

                File.WriteAllText(this._persistencePath, json);
                PluginLog.Verbose($"Saved notification apps to disk");
            }
            catch (Exception ex)
            {
                PluginLog.Error($"Failed to save notification apps to disk: {ex.Message}");
            }
        }

        // Raises the NotificationAppsChanged event.
        private void OnNotificationAppsChanged()
        {
            this.NotificationAppsChanged?.Invoke(this, EventArgs.Empty);
        }
    }
}

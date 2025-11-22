namespace Loupedeck.ExamplePlugin.Managers
{
    using System;
    using System.Collections.Generic;
    using System.IO;
    using System.Linq;
    using Loupedeck.ExamplePlugin.Models;
    using Newtonsoft.Json;

    // Manages the list of recently opened applications.
    public class RecentAppsManager
    {
        private const Int32 MaxRecentApps = 8;

        // Singleton instance.
        private static RecentAppsManager _instance;
        public static RecentAppsManager Instance => _instance ?? (_instance = new RecentAppsManager());

        // List of recent apps, ordered from most recent (index 0) to least recent.
        private List<AppInfo> _recentApps;

        // Path to the JSON file for persistence.
        private readonly String _persistencePath;

        // Lock for thread-safe access.
        private readonly Object _lock = new Object();

        // Event fired when the recent apps list changes.
        public event EventHandler RecentAppsChanged;

        private RecentAppsManager()
        {
            this._recentApps = new List<AppInfo>();

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

            this._persistencePath = Path.Combine(appDataPath, "RecentApps.json");

            // Load persisted state.
            this.Load();
        }

        // Gets the app at the specified slot (0-7), or null if no app in that slot.
        public AppInfo GetAppAtSlot(Int32 slot)
        {
            lock (this._lock)
            {
                if (slot < 0 || slot >= MaxRecentApps)
                {
                    return null;
                }

                if (slot < this._recentApps.Count)
                {
                    return this._recentApps[slot];
                }

                return null;
            }
        }

        // Gets all recent apps (read-only copy).
        public List<AppInfo> GetAllRecentApps()
        {
            lock (this._lock)
            {
                return new List<AppInfo>(this._recentApps);
            }
        }

        // Adds or updates an app in the recent apps list.
        // If the app already exists, it's removed and re-added at the top.
        public void AddOrUpdateApp(String appName, String bundlePath)
        {
            if (String.IsNullOrEmpty(appName))
            {
                return;
            }

            lock (this._lock)
            {
                // Remove existing entry if present.
                this._recentApps.RemoveAll(app => app.AppName.Equals(appName, StringComparison.OrdinalIgnoreCase));

                // Add to the top.
                this._recentApps.Insert(0, new AppInfo(appName, bundlePath, DateTime.Now));

                // Trim to max size.
                if (this._recentApps.Count > MaxRecentApps)
                {
                    this._recentApps = this._recentApps.Take(MaxRecentApps).ToList();
                }

                PluginLog.Info($"Added app to recent apps: {appName}");
            }

            // Save and notify.
            this.Save();
            this.OnRecentAppsChanged();
        }

        // Loads the recent apps list from disk.
        private void Load()
        {
            try
            {
                if (File.Exists(this._persistencePath))
                {
                    var json = File.ReadAllText(this._persistencePath);
                    var loadedApps = JsonConvert.DeserializeObject<List<AppInfo>>(json);

                    if (loadedApps != null)
                    {
                        lock (this._lock)
                        {
                            this._recentApps = loadedApps.Take(MaxRecentApps).ToList();
                        }

                        PluginLog.Info($"Loaded {this._recentApps.Count} recent apps from disk");
                    }
                }
            }
            catch (Exception ex)
            {
                PluginLog.Error($"Failed to load recent apps from disk: {ex.Message}");
            }
        }

        // Saves the recent apps list to disk.
        public void Save()
        {
            try
            {
                String json;
                lock (this._lock)
                {
                    json = JsonConvert.SerializeObject(this._recentApps, Formatting.Indented);
                }

                File.WriteAllText(this._persistencePath, json);
                PluginLog.Verbose($"Saved recent apps to disk");
            }
            catch (Exception ex)
            {
                PluginLog.Error($"Failed to save recent apps to disk: {ex.Message}");
            }
        }

        // Raises the RecentAppsChanged event.
        private void OnRecentAppsChanged()
        {
            this.RecentAppsChanged?.Invoke(this, EventArgs.Empty);
        }
    }
}

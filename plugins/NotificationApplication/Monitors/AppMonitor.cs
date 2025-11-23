namespace Loupedeck.ExamplePlugin.Monitors
{
    using System;
    using System.Diagnostics;
    using System.Threading;
    using Loupedeck.ExamplePlugin.Managers;
    using Loupedeck.ExamplePlugin.Utilities;

    // Monitors the frontmost macOS application and updates the recent apps list.
    public class AppMonitor
    {
        private Timer _timer;
        private String _currentFrontmostApp;
        private readonly AppIconLoader _iconLoader;
        private readonly Object _lock = new Object();

        // Polling interval in milliseconds (1.5 seconds).
        private const Int32 PollingIntervalMs = 1500;

        public AppMonitor()
        {
            this._iconLoader = new AppIconLoader();
        }

        // Starts monitoring the frontmost application.
        public void Start()
        {
            if (this._timer != null)
            {
                PluginLog.Warning("AppMonitor is already running");
                return;
            }

            PluginLog.Info("Starting AppMonitor");

            // Initialize current frontmost app.
            this._currentFrontmostApp = this.GetFrontmostApp();

            // Start the timer.
            this._timer = new Timer(this.OnTimerTick, null, PollingIntervalMs, PollingIntervalMs);
        }

        // Stops monitoring the frontmost application.
        public void Stop()
        {
            if (this._timer == null)
            {
                return;
            }

            PluginLog.Info("Stopping AppMonitor");

            this._timer.Dispose();
            this._timer = null;
        }

        // Timer callback that checks for frontmost app changes.
        private void OnTimerTick(Object state)
        {
            try
            {
                var frontmostApp = this.GetFrontmostApp();

                if (String.IsNullOrEmpty(frontmostApp))
                {
                    return;
                }

                lock (this._lock)
                {
                    // Check if the frontmost app has changed.
                    if (!frontmostApp.Equals(this._currentFrontmostApp, StringComparison.OrdinalIgnoreCase))
                    {
                        PluginLog.Info($"Frontmost app changed: {this._currentFrontmostApp} -> {frontmostApp}");

                        // Find the app bundle path.
                        var bundlePath = this._iconLoader.FindAppBundle(frontmostApp);

                        // Update the recent apps list.
                        RecentAppsManager.Instance.AddOrUpdateApp(frontmostApp, bundlePath ?? String.Empty);

                        // Update current app.
                        this._currentFrontmostApp = frontmostApp;
                    }
                }
            }
            catch (Exception ex)
            {
                PluginLog.Error($"Error in AppMonitor timer tick: {ex.Message}");
            }
        }

        // Gets the name of the frontmost (active) application using AppleScript.
        private String GetFrontmostApp()
        {
            try
            {
                var processStartInfo = new ProcessStartInfo
                {
                    FileName = "osascript",
                    Arguments = "-e \"set appPath to POSIX path of (path to frontmost application)\" -e \"do shell script \\\"basename '\\\" & appPath & \\\"' .app\\\"\"",
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
                        return output.Trim();
                    }
                    else if (!String.IsNullOrEmpty(error))
                    {
                        PluginLog.Verbose($"osascript error: {error}");
                    }
                }
            }
            catch (Exception ex)
            {
                PluginLog.Error($"Failed to get frontmost app: {ex.Message}");
            }

            return null;
        }
    }
}

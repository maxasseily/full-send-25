namespace Loupedeck.ExamplePlugin.Utilities
{
    using System;
    using System.Collections.Generic;
    using System.Diagnostics;
    using System.IO;

    // Utility class for loading and caching macOS application icons.
    public class AppIconLoader
    {
        // Cache of loaded icons: AppName -> (Icon80, Icon256)
        private readonly Dictionary<String, (BitmapImage Icon80, BitmapImage Icon256)> _iconCache;

        // Temporary directory for converted PNG files.
        private readonly String _tempIconDir;

        public AppIconLoader()
        {
            this._iconCache = new Dictionary<String, (BitmapImage, BitmapImage)>();
            this._tempIconDir = Path.Combine(Path.GetTempPath(), "LoupedeckAppIcons");

            // Create temp directory if it doesn't exist.
            if (!Directory.Exists(this._tempIconDir))
            {
                Directory.CreateDirectory(this._tempIconDir);
            }
        }

        // Finds the bundle path for a given application name.
        // Searches /Applications and ~/Applications.
        public String FindAppBundle(String appName)
        {
            if (String.IsNullOrEmpty(appName))
            {
                return null;
            }

            // Try common locations.
            var searchPaths = new[]
            {
                "/Applications",
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Applications")
            };

            foreach (var searchPath in searchPaths)
            {
                var appPath = Path.Combine(searchPath, $"{appName}.app");
                if (Directory.Exists(appPath))
                {
                    return appPath;
                }
            }

            // Try using mdfind (Spotlight search) as fallback.
            try
            {
                var processStartInfo = new ProcessStartInfo
                {
                    FileName = "mdfind",
                    Arguments = $"kMDItemKind == 'Application' && kMDItemFSName == '{appName}.app'",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    CreateNoWindow = true
                };

                using (var process = Process.Start(processStartInfo))
                {
                    var output = process.StandardOutput.ReadToEnd();
                    process.WaitForExit();

                    var lines = output.Split(new[] { '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries);
                    if (lines.Length > 0)
                    {
                        return lines[0].Trim();
                    }
                }
            }
            catch (Exception ex)
            {
                PluginLog.Warning($"Failed to search for app bundle using mdfind: {ex.Message}");
            }

            return null;
        }

        // Loads app icons for the given app name.
        // Returns (Icon80, Icon256) tuple, or null if loading fails.
        public (BitmapImage Icon80, BitmapImage Icon256)? LoadAppIcons(String appName)
        {
            if (String.IsNullOrEmpty(appName))
            {
                return null;
            }

            // Check cache first.
            if (this._iconCache.TryGetValue(appName, out var cachedIcons))
            {
                return cachedIcons;
            }

            try
            {
                // Find the app bundle.
                var bundlePath = this.FindAppBundle(appName);
                if (bundlePath == null)
                {
                    PluginLog.Warning($"Could not find app bundle for: {appName}");
                    return null;
                }

                // Find the .icns file in the bundle.
                var icnsPath = this.FindIconFile(bundlePath);
                if (icnsPath == null)
                {
                    PluginLog.Warning($"Could not find .icns file for: {appName}");
                    return null;
                }

                // Convert to PNG files.
                var png80Path = Path.Combine(this._tempIconDir, $"{appName}-80.png");
                var png256Path = Path.Combine(this._tempIconDir, $"{appName}-256.png");

                if (!this.ConvertIconToPng(icnsPath, png80Path, 80))
                {
                    PluginLog.Error($"Failed to convert icon to 80x80 PNG for: {appName}");
                    return null;
                }

                if (!this.ConvertIconToPng(icnsPath, png256Path, 256))
                {
                    PluginLog.Error($"Failed to convert icon to 256x256 PNG for: {appName}");
                    return null;
                }

                // Load the PNG files as BitmapImages.
                var icon80 = BitmapImage.FromFile(png80Path);
                var icon256 = BitmapImage.FromFile(png256Path);

                if (icon80 == null || icon256 == null)
                {
                    PluginLog.Error($"Failed to load PNG files as BitmapImages for: {appName}");
                    return null;
                }

                // Cache the icons.
                var icons = (icon80, icon256);
                this._iconCache[appName] = icons;

                PluginLog.Info($"Successfully loaded icons for: {appName}");
                return icons;
            }
            catch (Exception ex)
            {
                PluginLog.Error($"Failed to load icons for {appName}: {ex.Message}");
                return null;
            }
        }

        // Finds the .icns icon file in an app bundle.
        private String FindIconFile(String bundlePath)
        {
            var resourcesPath = Path.Combine(bundlePath, "Contents", "Resources");
            if (!Directory.Exists(resourcesPath))
            {
                return null;
            }

            // Look for .icns files.
            var icnsFiles = Directory.GetFiles(resourcesPath, "*.icns");
            if (icnsFiles.Length > 0)
            {
                // Prefer files with "App" or the app name in them, otherwise use first.
                var appName = Path.GetFileNameWithoutExtension(bundlePath);
                foreach (var icnsFile in icnsFiles)
                {
                    var fileName = Path.GetFileNameWithoutExtension(icnsFile);
                    if (fileName.Contains(appName) || fileName.Contains("App"))
                    {
                        return icnsFile;
                    }
                }
                return icnsFiles[0];
            }

            return null;
        }

        // Converts an .icns file to a PNG file at the specified size using sips.
        private Boolean ConvertIconToPng(String icnsPath, String outputPath, Int32 size)
        {
            try
            {
                var processStartInfo = new ProcessStartInfo
                {
                    FileName = "sips",
                    Arguments = $"-s format png \"{icnsPath}\" --out \"{outputPath}\" --resampleWidth {size}",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };

                using (var process = Process.Start(processStartInfo))
                {
                    process.WaitForExit();
                    return process.ExitCode == 0;
                }
            }
            catch (Exception ex)
            {
                PluginLog.Error($"Failed to convert icon using sips: {ex.Message}");
                return false;
            }
        }

        // Clears the icon cache.
        public void ClearCache()
        {
            this._iconCache.Clear();
        }
    }
}

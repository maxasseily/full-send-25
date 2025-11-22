namespace Loupedeck.ExamplePlugin.Models
{
    using System;

    // Represents information about a recently opened application.
    public class AppInfo
    {
        // The display name of the application.
        public String AppName { get; set; }

        // The full bundle path to the application (e.g., /Applications/Visual Studio Code.app).
        public String BundlePath { get; set; }

        // The timestamp when the application was last opened/switched to.
        public DateTime LastOpenedTime { get; set; }

        // Default constructor for JSON deserialization.
        public AppInfo()
        {
        }

        // Constructor with parameters.
        public AppInfo(String appName, String bundlePath, DateTime lastOpenedTime)
        {
            this.AppName = appName;
            this.BundlePath = bundlePath;
            this.LastOpenedTime = lastOpenedTime;
        }

        // Constructor with current timestamp.
        public AppInfo(String appName, String bundlePath)
            : this(appName, bundlePath, DateTime.Now)
        {
        }
    }
}

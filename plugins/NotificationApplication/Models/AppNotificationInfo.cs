namespace Loupedeck.ExamplePlugin.Models
{
    using System;

    // Represents information about an application with notification badges.
    public class AppNotificationInfo
    {
        // The display name of the application.
        public String AppName { get; set; }

        // The full bundle path to the application (e.g., /Applications/Messages.app).
        public String BundlePath { get; set; }

        // The current notification badge count (0 if no badge).
        public Int32 BadgeCount { get; set; }

        // The timestamp when the badge count last changed (increased or appeared).
        public DateTime LastNotificationTime { get; set; }

        // The timestamp when we last saw this app with any badge.
        public DateTime LastSeenTime { get; set; }

        // Default constructor for JSON deserialization.
        public AppNotificationInfo()
        {
        }

        // Constructor with parameters.
        public AppNotificationInfo(String appName, String bundlePath, Int32 badgeCount, DateTime lastNotificationTime, DateTime lastSeenTime)
        {
            this.AppName = appName;
            this.BundlePath = bundlePath;
            this.BadgeCount = badgeCount;
            this.LastNotificationTime = lastNotificationTime;
            this.LastSeenTime = lastSeenTime;
        }

        // Constructor with current timestamps.
        public AppNotificationInfo(String appName, String bundlePath, Int32 badgeCount)
            : this(appName, bundlePath, badgeCount, DateTime.Now, DateTime.Now)
        {
        }
    }
}

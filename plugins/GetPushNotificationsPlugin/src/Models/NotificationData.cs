namespace Loupedeck.GetPushNotificationsPlugin.Models
{
    using System;

    public class NotificationData
    {
        public int Count { get; set; }
        public string Url { get; set; }
        public string Favicon { get; set; }
        public long LastUpdated { get; set; }
    }

    public class NotificationContainer
    {
        public NotificationData Github { get; set; }
        public NotificationData Discord { get; set; }
        public NotificationData Slack { get; set; }
    }
}

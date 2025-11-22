namespace Loupedeck.GetPushNotificationsPlugin
{
    using System;
    using Loupedeck.GetPushNotificationsPlugin.Services;
    using Loupedeck.GetPushNotificationsPlugin.Actions;

    // This class contains the plugin-level logic of the Loupedeck plugin.

    public class GetPushNotificationsPlugin : Plugin
    {
        public NotificationService _notificationService;

        // Gets a value indicating whether this is an API-only plugin.
        public override Boolean UsesApplicationApiOnly => true;

        // Gets a value indicating whether this is a Universal plugin or an Application plugin.
        public override Boolean HasNoApplication => true;

        // Initializes a new instance of the plugin class.
        public GetPushNotificationsPlugin()
        {
            // Initialize the plugin log.
            PluginLog.Init(this.Log);

            // Initialize the plugin resources.
            PluginResources.Init(this.Assembly);
            
            // Initialize notification service early so commands can use it
            _notificationService = new NotificationService();
        }

        // This method is called when the plugin is loaded.
        public override void Load()
        {
            PluginLog.Info("GetPushNotificationsPlugin loading...");

            // Start the notification service
            _notificationService.Start();

            PluginLog.Info("GetPushNotificationsPlugin loaded successfully");
        }

        // This method is called when the plugin is unloaded.
        public override void Unload()
        {
            PluginLog.Info("GetPushNotificationsPlugin unloading...");
            _notificationService?.Stop();
        }
    }
}

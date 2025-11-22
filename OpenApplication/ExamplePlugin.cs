namespace Loupedeck.ExamplePlugin
{
    using System;
    using Loupedeck.ExamplePlugin.Managers;
    using Loupedeck.ExamplePlugin.Monitors;

    // This class contains the plugin-level logic of the Loupedeck plugin.

    public class ExamplePlugin : Plugin
    {
        private AppMonitor _appMonitor;

        // Gets a value indicating whether this is an API-only plugin.
        public override Boolean UsesApplicationApiOnly => true;

        // Gets a value indicating whether this is a Universal plugin or an Application plugin.
        public override Boolean HasNoApplication => true;

        // Initializes a new instance of the plugin class.
        public ExamplePlugin()
        {
            // Initialize the plugin log.
            PluginLog.Init(this.Log);

            // Initialize the plugin resources.
            PluginResources.Init(this.Assembly);
        }

        // This method is called when the plugin is loaded.
        public override void Load()
        {
            // Initialize the RecentAppsManager (loads persisted state).
            var manager = RecentAppsManager.Instance;
            PluginLog.Info("RecentAppsManager initialized");

            // Start the AppMonitor to track frontmost application changes.
            this._appMonitor = new AppMonitor();
            this._appMonitor.Start();
        }

        // This method is called when the plugin is unloaded.
        public override void Unload()
        {
            // Stop the AppMonitor.
            if (this._appMonitor != null)
            {
                this._appMonitor.Stop();
                this._appMonitor = null;
            }

            // Save the recent apps state.
            RecentAppsManager.Instance.Save();
            PluginLog.Info("Plugin unloaded, state saved");
        }
    }
}

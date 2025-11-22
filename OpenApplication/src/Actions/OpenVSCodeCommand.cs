namespace Loupedeck.ExamplePlugin
{
    using System;
    using System.Diagnostics;

    // This class implements a command that opens Visual Studio Code.

    public class OpenVSCodeCommand : PluginDynamicCommand
    {
        // Initializes the command class.
        public OpenVSCodeCommand()
            : base(displayName: "Open VSCode", description: "Opens Visual Studio Code", groupName: "Commands")
        {
        }

        // This method is called when the user executes the command.
        protected override void RunCommand(String actionParameter)
        {
            try
            {
                // Launch VSCode using macOS open command
                var processStartInfo = new ProcessStartInfo
                {
                    FileName = "open",
                    Arguments = "-a \"Visual Studio Code\"",
                    UseShellExecute = true,
                    CreateNoWindow = true
                };

                Process.Start(processStartInfo);
                PluginLog.Info("Visual Studio Code opened successfully");
            }
            catch (Exception ex)
            {
                PluginLog.Error($"Failed to open Visual Studio Code: {ex.Message}");
            }
        }

        // This method is called when Loupedeck needs to show the command on the console or the UI.
        protected override String GetCommandDisplayName(String actionParameter, PluginImageSize imageSize) =>
            "Open VSCode";
    }
}

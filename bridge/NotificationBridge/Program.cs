using System;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace NotificationBridge
{
    class Program
    {
        static async Task Main(string[] args)
        {
            var outputPath = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "LoupedeckNotifications",
                "notifications.json"
            );

            Directory.CreateDirectory(Path.GetDirectoryName(outputPath)!);

            Console.Error.WriteLine($"Native messaging host started. Output: {outputPath}");

            while (true)
            {
                try
                {
                    var message = await ReadMessageAsync();
                    if (message == null) break;

                    Console.Error.WriteLine($"Received: {message}");

                    // Write to file for Loupedeck plugin to read
                    await File.WriteAllTextAsync(outputPath, message);

                    // Send response back to extension
                    await SendMessageAsync(new { status = "success", timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() });
                }
                catch (Exception ex)
                {
                    Console.Error.WriteLine($"Error: {ex.Message}");
                }
            }
        }

        static async Task<string?> ReadMessageAsync()
        {
            var stdin = Console.OpenStandardInput();
            var buffer = new byte[4];
            
            var bytesRead = await stdin.ReadAsync(buffer, 0, 4);
            if (bytesRead < 4) return null;

            var length = BitConverter.ToInt32(buffer, 0);
            if (length <= 0) return null;

            var messageBuffer = new byte[length];
            bytesRead = await stdin.ReadAsync(messageBuffer, 0, length);
            
            return Encoding.UTF8.GetString(messageBuffer, 0, bytesRead);
        }

        static async Task SendMessageAsync(object message)
        {
            var json = JsonConvert.SerializeObject(message);
            var bytes = Encoding.UTF8.GetBytes(json);
            var length = BitConverter.GetBytes(bytes.Length);

            var stdout = Console.OpenStandardOutput();
            await stdout.WriteAsync(length, 0, 4);
            await stdout.WriteAsync(bytes, 0, bytes.Length);
            await stdout.FlushAsync();
        }
    }
}

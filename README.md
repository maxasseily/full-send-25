# NotificationApplication Plugin for Logitech Creative Console

This repo contains an experimental Loupedeck / Logitech Creative Console plugin
that turns your deck into a live dashboard and launcher for your desktop apps.

The core idea: use the Creative Console as a smart notification surface and
app launcher. The plugin automatically:

- Tracks notification badges across your macOS desktop (any app that shows a
  badge in the Dock or via `lsappinfo`)
- Highlights the apps with active notifications on the console, with live
  badge counts
- Lets you jump straight into the corresponding app by pressing its icon
- Learns which apps you actually use and exposes them as a “recent apps”
  launcher, also on the console

This project was originally built for the TUM Hackathon 2025.

---

## High‑Level Architecture

The repo contains several components, but the main one you’ll care about is
the `NotificationApplication` plugin under `plugins/NotificationApplication`.

- `plugins/NotificationApplication`
  - `ExamplePlugin.cs`: plugin entry point that wires everything together
  - `Monitors/NotificationMonitor.cs`: polls macOS (`lsappinfo`) for per‑app
    notification badges
  - `Monitors/DockBadgeMonitor.cs`: specializes in apps whose dock badges
    aren’t visible via `lsappinfo` (e.g., WhatsApp)
  - `Monitors/AppMonitor.cs`: tracks the current frontmost application
  - `Managers/NotificationManager.cs`: aggregates all badge data, keeps a
    ranked “top apps with notifications” list, persists to disk
  - `Managers/RecentAppsManager.cs`: tracks your most recently used apps and
    persists them to disk
  - `Actions/AppNotificationXCommand.cs`: one command per “notification slot”
    (up to 8), bound to specific buttons on the console
  - `Actions/RecentAppXCommand.cs`: one command per “recent app slot” (up to 8)
  - `Utilities/AppIconLoader.cs`: finds applications and icons so buttons look
    like the real app

There are also other sample plugins and a browser‑extension/bridge experiment
in this repo, but you can get a lot of value just from the
`NotificationApplication` part on its own.

---

## What the Plugin Does

Once installed and running, the plugin effectively turns part of your Creative
Console into:

1. **A desktop‑wide notification overview**
   - It periodically scans your running and known apps.
   - For each app that exposes a badge (e.g., unread messages, pending work),
     it records the badge count and when it was last seen.
   - It keeps a rolling, pruned list of the apps that have had notifications
     recently and surfaces the most relevant ones as “slots” on the deck.

2. **A one‑press notification jump‑to**
   - Each notification slot on the console shows the app’s icon and badge
     count.
   - Pressing that button focuses the corresponding application (or launches it
     if needed), so you go from “I see something needs attention” to “I’m in
     the app handling it” in one gesture.

3. **A personalized, recent‑apps launcher**
   - Independently of notifications, the plugin watches which app is
     frontmost.
   - As you naturally switch between tools (browser, IDE, chat apps, design
     tools, etc.), it records them in `RecentAppsManager`.
   - The top N (up to 8) most recent apps are bound to dedicated “Recent App”
     buttons, giving you a dynamic launcher that constantly reflects how you
     actually work.

Because the plugin reads from system‑level APIs and app badges, it works for
any app that shows a badge, without requiring per‑app integrations.

---

## Requirements

- macOS (the monitors use `lsappinfo` and Dock badge behaviour)
- Logitech / Loupedeck Creative Console with plugin support
- .NET SDK compatible with the Loupedeck SDK version used here
- Logitech / Loupedeck software installed (so it can load the plugin)

---

## Getting Started

### 1. Build the NotificationApplication plugin

From the repo root:

1. Open `plugins/NotificationApplication/ExamplePlugin.csproj` in your IDE
   (Rider, Visual Studio for Mac, VS Code with C#).
2. Restore dependencies and build the project in `Release` mode.
3. Locate the built plugin package or DLLs under `plugins/NotificationApplication/bin`
   or `plugins/NotificationApplication/package` (depending on how you package it
   with the Loupedeck SDK).

Consult your version of the Loupedeck / Logitech plugin docs if you’re unsure
how to package and install a plugin—they typically expect a specific folder or
bundle structure.

### 2. Install the plugin into the Creative Console software

1. Open the Logitech / Loupedeck configuration software.
2. Either:
   - Use the “Install plugin” / “Import plugin” flow if your build produced a
     packaged plugin file, **or**
   - Place the built plugin folder/DLL into the plugins directory that the
     software scans (check the vendor docs for the exact path).
3. Restart the plugin service / Creative Console software if needed so the
   plugin is picked up.

Once installed, you should see the plugin listed in the software’s plugin
browser with a name similar to “NotificationApplication” or “ExamplePlugin”.

### 3. Add plugin actions to your deck

In the Creative Console UI:

1. Create or open a profile/page for your deck.
2. Find the actions provided by this plugin, which should include:
   - `AppNotification1` … `AppNotification8`
   - `RecentApp1` … `RecentApp8`
3. Drag the `AppNotificationX` actions onto a row or grid you want to use as
   your notification overview.
4. Drag the `RecentAppX` actions onto another row/grid that you want to use as
   your “recent apps” launcher.

You don’t need to manually configure which apps go into which slot; the plugin
assigns them dynamically based on current notifications and recency.

---

## Using the Plugin Day‑to‑Day

Once the plugin is installed and its actions are on your deck:

- **Watch notifications at a glance**
  - The `AppNotificationX` buttons will show the icons of the apps that have
    the most recent or active notification badges.
  - The badge count on each button mirrors what you see in the Dock (e.g. the
    number of unread messages).

- **Jump directly into noisy apps**
  - When you see a badge you care about, press that button.
  - The plugin focuses (or launches) that application, letting you clear the
    notification and then return to what you were doing.

- **Use the Recent Apps row as a launcher**
  - The `RecentAppX` buttons evolve as you work: they show your most recently
    used applications, in order.
  - Pressing a button launches or focuses that app, effectively giving you a
    personalized launcher layer on the deck.

Because the plugin remembers state on disk, your notification history and
recent‑apps ordering survive plugin reloads and system restarts.

---

## Tips and Notes

- If you don’t see any apps appearing in the notification slots, make sure:
  - You’re on macOS.
  - The apps you expect to see actually display a Dock badge when they have
    notifications.
  - The plugin is loaded and not disabled in the Creative Console software.

- If a specific app doesn’t show up, it may use a non‑standard badge mechanism.
  The `DockBadgeMonitor` is designed to handle some of these cases (like
  WhatsApp), but not all apps are covered yet.

- You can safely restart the plugin or the console software; the managers
  persist their state to JSON in the Logitech plugin service directory and
  rehydrate on startup.

---

## Development Notes

If you want to hack on the plugin:

- The main coordination happens in `plugins/NotificationApplication/ExamplePlugin.cs`.
- Notification logic lives under `Managers/` and `Monitors/`.
- App launching and icon rendering live under `Actions/` and `Utilities/`.

Feel free to fork and adapt the logic:

- Add filters for which apps are eligible to appear.
- Change the ranking heuristics (e.g., prefer productivity apps over social).
- Add custom actions that clear badges, toggle focus modes, etc.

Pull requests, experiments, and wild ideas welcome—this is a hackathon project
meant to be extended.


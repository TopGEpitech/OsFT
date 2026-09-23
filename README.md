# MACOS EMULATOR · Unreal Engine games on your Mac

**Your games on your Mac, full screen, on your keyboard, at 60 Hz.**
A native launcher for Apple Silicon (M1, M2, M3, M4 and newer) that runs a real Android device locally, optimized for Unreal Engine games: no Windows, no Boot Camp, no virtual machine, no streaming.

[**⬇︎ Download the launcher (.dmg)**](https://github.com/TopGEpitech/macosemulator/releases/latest/download/MACOS-EMULATOR.dmg) · [Website](https://macosemulator.com/en) · [Support](https://macosemulator.com/en/compte)

## How it works

A real Android device runs locally on Apple's own Hypervisor (nothing hacky, no SIP disabling, no admin rights, no Android Studio, no Java). Games render in OpenGL straight on your GPU, and the launcher gives you keyboard controls that feel right.

You sign into **your** Google account and install your games from the real Google Play, exactly like on a phone.

## Download and install

1. [Download the latest `.dmg`](https://github.com/TopGEpitech/macosemulator/releases/latest/download/MACOS-EMULATOR.dmg), open it and drag **MACOS EMULATOR** into your Applications folder.
2. First launch, one time only: double-click the app. If macOS blocks it, open **System Settings > Privacy & Security**, scroll to the message about the app, and click **Open Anyway**. This is the standard prompt for any app not sold through the App Store, not a warning about this app in particular.
3. Open the app, hit **Install game engine** once (about 3.5 GB), then sign into the Play Store and install your game.

That's it. After the first setup it boots from a snapshot in a few seconds.

Prefer the terminal? This one line does the same as step 2 (the app keeps its original file name on disk):

```sh
xattr -dr com.apple.quarantine "/Applications/OSFT - Launcher.app"
```

All releases: [github.com/TopGEpitech/macosemulator/releases](https://github.com/TopGEpitech/macosemulator/releases).

## What you get

- **Full screen, sharp.** Drawn at scale 1, no blur, on any display size.
- **Keyboard controls.** Map any key to an on-screen action, per resolution, changeable mid-game.
- **Machine profile in one click.** 8, 16 or 24 GB of RAM: memory, resolution, quality and frame rate are set together, and each stays editable.
- **Three quality levels.** Smooth, Balanced (the default on every profile) or Ultra, at 30 or 60 Hz.
- **Fewer stutters at the start of a session.** Effects are prepared on every core of your Mac.
- **Going back takes one click.** The previous version is one button away if a release does not suit your Mac.

## What you need

- An Apple Silicon Mac: M1, M2, M3, M4 or newer (MacBook Air, MacBook Pro, iMac, Mac mini, Mac Studio). Intel Macs are not supported: hardware virtualization needs an Apple Silicon chip.
- macOS 12 or later.
- About 10 GB free for the setup, plus room for your games.
- 8 GB of RAM works, 16 GB is comfier.

## Pricing

Playing needs an active subscription, **cancel anytime**, or a **one-time lifetime license**. Current prices and promo codes are on [macosemulator.com](https://macosemulator.com/en#pricing). Your license key is emailed right after payment; paste it into the app and play. If your game is not available on the Google Play Store, you are refunded in full.

## FAQ

**Do I need Windows, Boot Camp, Parallels or a virtual machine?**
No. Nothing to install besides the launcher. Your Mac stays the way it is.

**Is it an emulator?**
It is a real Android device running on Apple's Hypervisor with GPU rendering, tuned for Unreal Engine games rather than a slow generic emulator.

**Which Macs are supported?**
Any Apple Silicon Mac (M1 and up) on macOS 12 or later. Intel Macs are not.

**Is MACOS EMULATOR affiliated with a game publisher?**
No. MACOS EMULATOR is an independent project, not affiliated with any game publisher, nor with Apple or Epic Games. Mac and macOS are trademarks of Apple Inc. Unreal and Unreal Engine are trademarks of Epic Games, Inc.

## Something broke?

Fastest: the support chat in your [customer area](https://macosemulator.com/en/compte) with the **Send a report** button (performance report and launcher logs, two clicks). Or open an [issue](https://github.com/TopGEpitech/macosemulator/issues) with your Mac model, macOS version, and what you were doing.

## In other languages

[Français](https://macosemulator.com/fr) · [Tiếng Việt](https://macosemulator.com/vi) · [Español](https://macosemulator.com/es) · [Polski](https://macosemulator.com/pl) · [Nederlands](https://macosemulator.com/nl) · [한국어](https://macosemulator.com/ko) · [ไทย](https://macosemulator.com/th) · [Deutsch](https://macosemulator.com/de) · [中文](https://macosemulator.com/sg)

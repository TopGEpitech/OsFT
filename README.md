# OS FIGHT TACTICS

![OS FIGHT TACTICS](launcher.png)

Teamfight Tactics on your Mac. Full screen, keyboard controls, no jank.

Last season I was playing on Emulator due to a bad PC  and since
TFT will not be there on 18.1, and I wasn't about to stop playing.
I brought my  emulator and decided to tuning it, breaking it, tuning it again, 
until it actually felt good on a Mac. At some point I figured I'd stop keeping it to myself. 
This is that setup, cleaned up and optimized for TFT, so you don't have to sink a year into 
getting there.


It runs a real Android device locally (Apple's own Hypervisor, nothing hacky),
renders straight to the GPU, and hands you keyboard controls that feel right for
TFT. You sign into *your* Google account and install the game from the real Play
Store, same as you would on a phone.

## Download

**[⬇︎ Download the latest .dmg](../../releases/latest)**

Then:

1. Open the `.dmg` and drag **OSFT - Launcher** into your Applications folder.
2. First launch, one time only: double-click the app. macOS blocks it, so open
   **System Settings > Privacy & Security**, scroll to the message about
   OSFT - Launcher, and click **Open Anyway**. This is the standard prompt for any
   app not sold through the App Store; it is not a warning about this app in
   particular.
3. Open the app, hit **Install game engine** once (~3.5 GB), then sign into the
   Play Store and grab Teamfight Tactics.

That's it. After the first setup it boots from a snapshot in a few seconds.

Prefer the terminal? This one line does the same as step 2:

```sh
xattr -dr com.apple.quarantine "/Applications/OSFT - Launcher.app"
```

## What you need

- Apple Silicon Mac (M1 or newer)
- macOS 12 or later
- ~10 GB free for the setup, plus room for the game
- 8 GB RAM works, 16 GB is comfier

## Good to know

- Playing needs an active subscription: **$2/month, cancel whenever**. Grab a key
  at **[macosfighttactics.com](https://macosfighttactics.com)** and paste it into
  the app.
- It never ships or pushes games. You install them yourself, from your own Play
  Store account, exactly like on a real phone.
- No SIP disabling, no admin rights, no Android Studio, no Java. Your Mac stays
  the way it is.

## Something broke?

Open an [issue](../../issues). Tell me your Mac model, macOS version, and what you
were doing. I read them.

---

Made by one person who plays too much TFT.

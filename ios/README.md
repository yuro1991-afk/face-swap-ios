# Swift shell (Mac + Xcode only)

This folder is **source**. It is not an `.ipa`.

This Windows host cannot compile it. On a Mac:

1. Create a new iOS App in Xcode (SwiftUI).
2. Replace the app files with `FaceSwap/*.swift` and `Info.plist`.
3. Set the gateway URL to the Windows LAN address printed by `START.cmd`.
4. Sign with your personal Apple ID and run on a plugged-in iPhone (free provisioning, 7 days).

The product that already installs on any iPhone is the PWA in `../pwa` via Safari → Add to Home Screen.

Running RF downloader on macOS
----------------------------

Because this app is not signed with an Apple Developer ID, macOS may warn you the first time you try to open it.

To run the app:
1. Right-click the app and choose "Open".
2. Confirm the warning by clicking "Open".
3. After this, you can double-click normally.

Alternatively, go to System Settings → Privacy & Security → Allow Anyway.

Advanced users can run:
xattr -d com.apple.quarantine /path/to/IGC rfdownloader.app


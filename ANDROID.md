# ShamCash — Android demo build

This repository currently contains a **demonstration web UI**, not a production wallet. Balances, accounts, QR codes, and transactions are not connected to a payment provider or authoritative backend. Do not enter real credentials or use this app to store, send, or receive money.

## Build and download a debug APK

The GitHub Actions workflow **Build Android demo APK** generates a Capacitor Android wrapper and builds an unsigned debug APK. It runs on pushes to this branch that change the app/build files, or can be started manually from the Actions page.

After a successful run:

1. Open the repository's **Actions** tab.
2. Open the completed **Build Android demo APK** run.
3. Download the `shamcash-demo-debug-apk` artifact.
4. Transfer `app-debug.apk` to the Android device and install it. Android may ask you to allow installation from that source.

This is a debug/testing APK, not a Play Store release. No APK is available until GitHub Actions completes successfully.

## Local build

Requires Node.js 20, Java 17, and Android SDK tools:

```sh
npm install
npx cap add android
npx cap sync android
cd android
./gradlew assembleDebug
```

The APK is written to `android/app/build/outputs/apk/debug/app-debug.apk`.

## Backend and security status

The current browser-side demo authentication and local storage are not secure authentication or financial infrastructure. A real service needs a server-side identity provider, protected database access, authorization rules, transaction validation/ledgering, and a reviewed payment integration. Secrets must be stored in deployment secrets or environment variables, never in the repository or Android app. MongoDB by itself is a database, not SMS authentication or a payment provider.

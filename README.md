# Sarik — Worm Cinema Android APK

This project contains a native Android wrapper which runs the existing Flask
Worm Cinema application **locally on the phone** and displays it in a WebView.
Its cinema data is saved in the app's private storage, so it does not require a
separate hosted Flask server.

## Build the APK

1. Install JDK 17, Android SDK Platform 35, and Build Tools 35.0.0.
2. Set `ANDROID_HOME` to the Android SDK location.
3. Run:

   ```bash
   gradle :android:app:assembleDebug
   ```

The generated installable debug APK is:

```text
android/app/build/outputs/apk/debug/app-debug.apk
```

A GitHub Actions workflow is included to build and upload the same APK as the
`worm-cinema-debug-apk` artifact after a push to the `work` branch or a manual
workflow run.

## Local web development

```bash
python -m pip install -r requirements.txt
python app.py
```

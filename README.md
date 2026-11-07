# nono-builder

Build recipe for the NONO app. **No app code lives here**: the workflow downloads
the private `Jamesodigie/NoNo` repo with the `NONO_REPO_TOKEN` secret, builds the
Android app and the admin dashboard, and publishes them:

- APK → www.nono.com.ng download (and NoNo's `apk-latest` branch)
- Admin dashboard → admin.nono.com.ng (NoNo's `admin-site` branch)

Run it from **Actions → Build NONO → Run workflow**.

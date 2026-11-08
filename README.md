# nono-builder

Build pipeline for NONO. This repository contains the build and publishing workflows only; the actual application source lives in the private `Jamesodigie/NONO-app` repository.

## Repository roles

- `Jamesodigie/NONO-app` — Flutter application source, Android project, Supabase migrations/functions, tests, assets and website source.
- `Jamesodigie/nono-builder` — CI build pipeline and APK GitHub Release.
- `Jamesodigie/NoNo` — retained as the original backup and current deployment destination for the `website`, `admin-site` and `apk-latest` branches.

The source migration completed successfully on November 8, 2026. The original `NoNo` repository was not deleted or modified.

## Build

Run **Actions → Build NONO → Run workflow**. The default source ref is `main` in `NONO-app`; you can enter another branch or commit when you intentionally want to build a different version.

The workflow checks out the app and admin source from `NONO-app`. It publishes the APK release to this builder repository and continues updating the existing website/admin/APK deployment branches in `NoNo`.

## Required GitHub secret

Keep `NONO_REPO_TOKEN` configured in this repository's Actions secrets.

Use a fine-grained token owned by the repository owner, with repository access to both `NoNo` and `NONO-app` and these permissions:

- Contents: Read and write — read the source and publish deployment branches/releases.
- Workflows: Read and write — needed because the source repository contains GitHub Actions workflow files.

Do not put Supabase service-role keys or other private backend credentials in this token or in source files. The public Supabase publishable/anon key used by the app is not a service-role secret.

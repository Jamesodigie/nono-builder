# nono-builder

Build pipeline for NONO. The application source is being separated into the private `Jamesodigie/NONO-app` repository. This repository contains the build and publishing workflows only.

## One-time source migration

1. In GitHub, update the `NONO_REPO_TOKEN` secret in this repository so its fine-grained token has **Contents: Read and write** access to both private repositories:
   - `Jamesodigie/NoNo` (source being migrated and current website/admin publishing destination)
   - `Jamesodigie/NONO-app` (new source destination)
2. Open **Actions → Migrate NONO source to NONO-app → Run workflow**.
3. Confirm the workflow succeeds. It copies the existing default-branch history to `NONO-app/main` and preserves the unmerged build-hardening work on `chore/reliable-android-build-and-apk-storage`.

The original `NoNo` repository is not deleted or modified by the migration. The new repository is kept private.

## Build

After migration is verified, the **Build NONO** workflow will be pointed at `Jamesodigie/NONO-app`. It will continue publishing the APK release here and the website/admin deployment branches to the existing `Jamesodigie/NoNo` repository.

Run builds from **Actions → Build NONO → Run workflow**.

# 🚀 Publishing & Releasing Abilithic Scan

All commands run from the project folder:

```bat
cd "D:\Lab Kantor 2025\Github-Me\Project_2-Scan\abilithic-scan"
```

---

## 1. First-time setup (only once)

Create the repo on GitHub first (empty, no README), then:

```bat
git init
git add .
git commit -m "Abilithic Scan v1.0.0 — friendly GUI for the full power of Nmap"
git branch -M main
git remote add origin https://github.com/<your-username>/abilithic-scan.git
git push -u origin main
```

> Replace `<your-username>`. If you use SSH:
> `git remote add origin git@github.com:<your-username>/abilithic-scan.git`

---

## 2. Update (push changes) — use this every time you change something

```bat
git add -A
git commit -m "Update: readable progress bar & criticality badges, NSE checkboxes, screenshots"
git push
```

Quick one-liner for small tweaks:

```bat
git add -A && git commit -m "Tweak UI colors and README" && git push
```

---

## 3. Release the .exe to GitHub

There are two ways. **Option A** is the easiest path to a self-contained binary
(with Nmap bundled); **Option B** is fully automated via GitHub Actions.

### Option A — Build locally, upload the .exe (recommended for a bundled Nmap)

1. (Optional, for a self-contained app) copy a Windows Nmap build into
   `abilithic_scan\data\nmap\` — see that folder's README.
2. Build the executable:

   ```bat
   build.bat
   ```
   This produces `dist\AbilithicScan.exe` and `dist\AbilithicScan.exe.sha256.txt`.

3. Create the GitHub release and attach the files. Easiest with the GitHub CLI
   (`gh`, from https://cli.github.com):

   ```bat
   gh release create v1.0.0 ^
     dist\AbilithicScan.exe ^
     dist\AbilithicScan.exe.sha256.txt ^
     --title "Abilithic Scan v1.0.0" ^
     --notes "First release: friendly GUI for the full power of Nmap. Automatic port criticality, NSE picker, and polished Excel reports. See CHANGELOG.md."
   ```

   No `gh`? Do it in the browser: **Releases → Draft a new release →** create tag
   `v1.0.0` → drag `AbilithicScan.exe` (+ the `.sha256.txt`) into the assets box →
   **Publish release**.

### Option B — Let GitHub Actions build the .exe automatically

The workflow `.github/workflows/build.yml` builds the `.exe` on a Windows runner
and attaches it to the release whenever you push a tag starting with `v`:

```bat
git tag v1.0.0
git push origin v1.0.0
```

Watch progress on the repo's **Actions** tab; when it finishes, the `.exe` and
checksum appear on the **Releases** page.

> ⚠️ Note: the Actions build does **not** include the Nmap binary (it's
> git-ignored). The resulting `.exe` will use an Nmap found on the user's PATH.
> For a truly stand-alone download, use **Option A**.

---

## 4. Cutting the next version

1. Bump the version in `abilithic_scan/__init__.py` (`__version__`), in
   `version_info.txt`, and add a `CHANGELOG.md` entry.
2. Commit & push (section 2).
3. Tag & release (section 3) with the new version, e.g. `v1.1.0`.

```bat
git tag v1.1.0
git push origin v1.1.0
```

---

## Handy git commands

| Goal | Command |
|---|---|
| See what changed | `git status` |
| See file diffs | `git diff` |
| Undo unstaged changes to a file | `git checkout -- path\to\file` |
| List tags | `git tag` |
| Delete a wrong tag (local + remote) | `git tag -d v1.0.0` then `git push origin :refs/tags/v1.0.0` |
| Pull latest (if editing on 2 machines) | `git pull` |

# Audit Progress

## 2026-11-05 13:27 UTC — Phase 1 kickoff; repository orientation

**Objective:** Initialize durable audit state and establish the starting branch/worktree before substantive investigation.

**Files/functions examined:** None. Listed top-level files; found Python modules/tests, `README.md`, `READ ME.txt`, `CONTRIBUTING.md`, `LICENSE`, `MIRRORED_ARTWORK_IMPLEMENTATION.md`, `requirements.txt`, and `build.ps1`.

**Commands run:** `git status --short --branch`; `git remote -v`; `git --no-pager log -8 --oneline --decorate`; top-level file inventory; checks for existing audit documents.

**Findings:**
- **Verified:** Current branch is `feature/mirrored-artwork-retry-cache`, at `8e95eb2` (`Release v2.0.4 with GB/GBC mode detection`), and the worktree was clean.
- **Verified:** `origin` is `merkin-agent/dsscc`; `upstream` is already configured as `voluptuary/dsscc`.
- **Verified:** No `audit/AUDIT_HANDOFF.md` or `audit/AUDIT_PROGRESS.md` existed at kickoff; created both.
- **Unverified:** Project architecture, exact branch feature behavior, kernel output contract, default branches and current remote divergence, baseline build/tests.

**Code changes:** None. Added initial audit handoff and this journal.

**Validation:** No tests/build run yet; documentation files not yet committed.

**Commit/push status:** Audit docs uncommitted; nothing pushed.

**Next action:** Read project guidance/build/test configuration; refresh and compare default-branch refs; record baseline and inspect branch changes.

## 2026-11-05 13:30 UTC — Phase 1 milestone; identity, baseline, and branch scope

**Objective:** Establish project conventions and commands, refresh comparison refs, and determine what the branch name’s “mirrored” feature means.

**Files/functions examined:** Read `README.md`, `READ ME.txt`, `CONTRIBUTING.md`, `LICENSE`, `MIRRORED_ARTWORK_IMPLEMENTATION.md`, `requirements.txt`, `.github/workflows/release.yml`, `build.ps1`, and `DS Style Thumbnail Scraper.spec`. No individual runtime function has yet been reviewed in depth.

**Commands/tests run:** `git fetch origin`; `git fetch upstream`; branch/remotes/log/ref inspection; `git diff --stat origin/main...HEAD`; `git diff --check origin/main...HEAD`; `python -m unittest discover -s tests -v`; `python -m py_compile 'DS Style Thumbnail Scraper.py' rom_matching.py thumbnail_output_paths.py thumbnail_image_data.py thumbnail_rendering.py ezflash_gba_thumbs.py`; Python/Pillow/PyInstaller environment query.

**Findings:**
- **Verified:** The application is a Python/Tkinter Windows desktop app. README documents GBA pack creation and custom art output for additional DS Style-supported systems. The documented pack path is source lookup/download → validation/cache → BMP conversion → `IMGS`/`IMGS2`; output is copied under `SYSTEM/IMGS` and `SYSTEM/IMGS2`.
- **Verified:** “Mirrored artwork” means local ROM-relative directory preservation in `IMGS` and `IMGS2`, e.g. ROM `Game Boy/T/Tetris (World).gb` maps to same-stem BMPs below `IMGS/Game Boy/T/` and `IMGS2/Game Boy/T/`. It does not mean alternate remote mirror hosts. README and `MIRRORED_ARTWORK_IMPLEMENTATION.md` say this; runtime tracing remains to be done.
- **Verified:** `upstream` was already configured. `origin/main` and `upstream/main` are both `98fed08d617b982b58d62c1bb9c2b4488b5ac8be`; HEAD is 34 commits ahead and zero behind each. The same feature ref exists on both remotes at `8e95eb2`.
- **Verified:** Baseline unit suite passed: 147 tests in 0.932s. Targeted `py_compile` passed. `git diff --check origin/main...HEAD` reported no whitespace errors.
- **Verified:** Runtime declares Pillow `>=10.0.0`; environment is Python 3.14.2/Pillow 13.0.0. PyInstaller is not installed. Release workflow is tag-triggered and builds on Windows/Python 3.12 using `build.ps1`.
- **Verified:** The branch has 34 commits and 37 changed paths vs both defaults; first feature commit is `f8319fd` (“Add mirrored artwork, retry and caching support”). Most changed code is in the GUI entry point; later commits add provider fallbacks, hashing, local-pack matching, and GB/GBC save conversion.
- **Unverified:** Kernel requirements/compatibility, actual retry/cache semantics, and the correctness of output format/layout.

**Code changes:** Updated audit handoff to record the baseline, branch topology, and verified meaning of mirroring. No product code changes.

**Validation:** 147 unit tests and targeted compilation passed. Windows executable build not attempted (Linux environment; PyInstaller absent). Live provider requests not attempted.

**Commit/push status:** Audit docs remain uncommitted; no code changes or pushes.

**Next action:** Trace the precise mirror/cache/retry paths in `DS Style Thumbnail Scraper.py`; research both cartridge kernels’ source-level output contract before rating compatibility.

## 2026-11-05 13:40 UTC — Phase 2 milestone; preliminary kernel comparison (superseded)

**Objective:** Verify what the released DS Style kernels actually load before judging the mirrored pack output.

**Files/functions examined:** Official kernel repositories `FrankieT19/omega-de-ds-style-kernel` (original Omega) and `FrankieT19/omega-de-ds-style-kernel` (Omega DE), `source/ezkernelnew.c` at each `v7.4` tag and current `main` v8.0 snapshots; key functions `Launcher_ThumbnailFolder`, `Launcher_ThumbnailReadSize`, `Launcher_LoadCustomThumbManifest`, `Launcher_LoadCustomThumbnailByName`, `Launcher_CustomThumbFileName`, `Launcher_LoadThumbnailByGameCode`, `Launcher_LoadThumbDataForIndex`. In the app, traced `fetch_bytes`, `sd_scan_rom_cache_path`, `cache_sd_scan_image`, `ask_sd_download_fallback_skip`, `_scan_sd_worker`, and `build_custom_rom_output`; read output-path/image helpers and relevant tests.

**Commands/research:** Fetched both kernel repositories’ source trees to `/tmp/audit-kernel-omega-de` and `/tmp/audit-kernel-omega`; fetched official `v7.4` tags; inspected GitHub release lists and kernel README files via `gh`; source `rg`/`git grep`; README and implementation-note review. Kernel heads at inspection: Omega DE `67a5f7ba23b38ad2c10fdb4f27956750a65129fc`, original Omega `ef30b8ba78147943d95653dfa82f721b52096f67`. Official manager pack metadata: `docs/manager/packages/current/included-artwork.zip`, 49,464,652 bytes, SHA `4aa8f49b6bfb6e88728a6d4624766c4316d4ac23`; archive contents not yet inspected.

**Findings (initial, incorrectly selected compatibility repos):**
- **Verified only for FrankieT19 secondary kernels:** Their v7.4 and current v8.0 source used `IMGS`/`IMGS2`, flat-CUSTOM lookup and 256-manifest implementation. This was not the kernel repository specified by the user for this DSSCC adaptation; do not use it to conclude what the target kernel supports.
- **Superseded conclusion:** “Public kernel source does not implement nested mirror lookup or DST1” was incorrect for the target of this version. The specified Voluptuary Merkin Mix kernel does implement both.
- **Still potentially applicable, needs tests:** DSSCC’s total combined CUSTOM cap (>255) does not match the target kernel’s separate per-size 256-entry manifests. The initially claimed need to count extension defaults was wrong; target source explicitly loads extension defaults outside the old manifest.
- **Verified:** This DSSCC runtime’s failure path prompts for fallback or skip and does not retry the same Libretro URL; this is a code fact independent of the mistaken kernel selection.

**Correction required:** User clarified that `voluptuary/ezfode-dssmm-kernel` is the primary compatibility reference, with FrankieT19 only a source for applicable improvements. Corrected the handoff above and continue with target source.

**Code changes:** Updated handoff with the verified kernel contract and the likely legacy-CUSTOM limit defect. No product code changed yet.

**Validation:** No new tests run in this milestone; baseline 147 tests remain green.

**Commit/push status:** Audit docs uncommitted; no code commits/pushes.

**Next action:** Add regression coverage and correct legacy CUSTOM limits in `build_custom_rom_output()`; inspect the official artwork archive’s file metadata without placing artwork into the repository.

## 2026-11-05 13:36 UTC — Correction; selected the actual compatibility kernel

**Objective:** Replace the preliminary output-contract research with the target specified by the user and retain the prior investigation as an explicit correction trail.

**Files/functions examined:** Cloned `voluptuary/ezfode-dssmm-kernel` at `cff477969bc501548497e7be8dab9e3b445ba987`; read its README and source `source/ezkernelnew.c`, including `Launcher_ThumbnailFolder`, `Launcher_LoadCustomThumbManifest`, `Launcher_TagTransparentThumbnailPixels`, `Launcher_LoadCustomThumbnailByName`, `Launcher_LoadMirroredThumbnail`, `Launcher_LoadExtensionDefaultThumbnail`, `Launcher_LoadThumbnailFromRomHeaderPath`, and `Launcher_LoadThumbnailForPath`; inspected `source/launcher_artwork_path.h`. Verified repository README and release listing (latest v8.2.0; earlier v7.4.3 introduced mirrored lookup). Also checked FrankieT19’s v8.0 DE source only for secondary comparison.

**Commands/research:** `gh repo view/list`, `gh api` tree and README, `gh release list/view`; `git clone --depth=1 https://github.com/voluptuary/ezfode-dssmm-kernel.git /tmp/audit-voluptuary-ezfode`; source `rg`; file-range reads. Did not fetch the 49 MB artwork ZIP.

**Findings:**
- **Verified:** The actual target is the DE-only Voluptuary Merkin Mix kernel. Its README explicitly describes ROM-folder mirrored artwork, custom and built-in thumbnail fallbacks; it documents title 120×80, box 80×80, uncompressed top-down 16-bit BMP, and `DST1` in BMP header bytes 6–9, where marked RGB555 zero pixels are transparent. Target source has the same constants and checks the BMP dimensions/bit depth before applying the marker.
- **Verified:** The target tries mirrored artwork under `/SYSTEM/IMGS` or `/SYSTEM/IMGS2`, resolves long directory names (LFNs) when the ROM browser uses aliases, and tries alias paths as compatibility fallback. On miss it falls back to flat `CUSTOM/<basename>.bmp`, GBA game-code art for GBA files, direct `CUSTOM/<extension>.bmp`, then NOTFOUND. This directly supports the app’s mirror layout; the earlier “no mirror support” claim is reversed.
- **Verified:** Target source uses two separate custom manifests of 256 entries and explicitly states extension-default thumbnails bypass the historical manifest. Therefore excluding extension defaults in the app’s index count is correct, contrary to the earlier tentative note.
- **Likely defect (medium, output generation):** In legacy CUSTOM mode, DSSCC combines ordinary entries from both size buckets and rejects at >255. The target kernel has separate manifests per size, each with a 256-entry cap; its source also documents each CUSTOM folder supports 256. The app’s README likewise describes 256 per size. This means combined 256 entries split across sizes are incorrectly rejected, and exactly 256 in either size is incorrectly rejected. Reproduction and focused test still needed.
- **Verified scope caveat:** `voluptuary/ezfode-dssmm-kernel` describes itself as Omega DE only. The original Omega compatibility requirement cannot be concluded from this target. FrankieT19’s original Omega repository may serve as a separate comparison but not as evidence for the DE target.
- **Verified secondary source insight:** FrankieT19’s source is an ancestor/contributor base per target README. Only improvements absent from target will be considered for DSSCC if directly relevant; no external kernel code will be changed by this audit.
- **Unverified:** Whether v8.2.0 is the kernel version paired with DSSCC v2.0.4; whether original Omega has a Voluptuary mirror; all cache eviction and cross-process concerns.

**Correction to previous entry:** The earlier statements that the public kernel lacked mirrored lookup and DST1 handling and that extension defaults count against the index are retracted for the target repository. The correct target implementation explicitly includes these features.

**Code changes:** Corrected `AUDIT_HANDOFF.md`, replacing the wrong primary compatibility repository and carrying forward only the per-size CUSTOM-cap issue for testing. Preserved, rather than deleted, the earlier mistaken claims in the previous journal entry and marked them superseded.

**Validation:** No product tests run in this correction step. External source findings are directly verifiable in target files. Targeted regression test for the legacy cap is pending.

**Commit/push status:** Audit docs uncommitted; no code changes/push.

**Next action:** Implement the per-size CUSTOM manifest cap fix with regression tests; then continue the code audit against the Voluptuary source as primary and Frankie source only for non-regressing applicable comparisons.

## 2026-11-05 13:47 UTC — Correction and fix milestone; CUSTOM directory accounting

**Correction to 13:36 entry:** That entry incorrectly concluded extension-default files do not consume manifest capacity. In `voluptuary/ezfode-dssmm-kernel/source/ezkernelnew.c::Launcher_LoadCustomThumbManifest`, the enumeration has no extension-default exclusion: every regular file is stripped/hashed and increments `launcher_custom_thumb_manifest_count` until `LAUNCHER_CUSTOM_THUMB_MANIFEST_MAX` (256). `Launcher_LoadExtensionDefaultThumbnail` opens the extension path directly, but this direct open does not change how the manifest scan counts the file. The new fix and user docs therefore count extension-default files in the 256-file directory limit. This corrects the prior statement without deleting it.

**Objective:** Align legacy CUSTOM output validation with the actual Voluptuary target manifest and verify the change.

**Files/functions changed:** `DS Style Thumbnail Scraper.py::custom_output_manifest_overflow` and `ThumbnailScraperApp.build_custom_rom_output`; removed unused `ThumbnailScraperApp.is_extension_default_name`. Updated the Legacy CUSTOM explanation in `README.md` and `READ ME.txt`. Added `tests/test_custom_art_output_limits.py`.

**Verified defect (medium, output generation):** Prior code summed unique names from both `120x80` and `80x80`, rejecting above 255, and excluded extension defaults. Target kernel has a separate manifest for each art style, each scans up to 256 regular entries. Reproduction before fix: 128 title + 128 box entries are rejected despite each separate directory being below capacity; 256 in one size also rejected; a 256-entry folder including an extension default could still be accepted and risk an ordinary file being outside the manifest scan. Expected: independent maximum of 256 emitted files per CUSTOM folder. Actual before: global 255 ordinary-only limit.

**Fix/regression coverage:** Implemented per-size overflow reporting at >256 and counted all flat-CUSTOM names including extension defaults. Tests cover two independent full-size folders, 257 in only one style, and 255 ordinary plus one default accepted / 256 plus one rejected.

**Validation:** `python -m unittest tests.test_custom_art_output_limits -v` — 3 passed. `python -m unittest discover -s tests -v` — 150 passed. `python -m py_compile 'DS Style Thumbnail Scraper.py' rom_matching.py thumbnail_output_paths.py thumbnail_image_data.py thumbnail_rendering.py ezflash_gba_thumbs.py` — passed. `git diff --check` — passed.

**Residual limitation:** Source-level target is Voluptuary `main` at `cff477969bc501548497e7be8dab9e3b445ba987` (README says v8.2.0). No physical card/hardware test. Repository target is Omega DE only.

**Commit/push status:** Product source/test/user-doc changes uncommitted; audit docs uncommitted. No pushes.

**Next action:** Commit the tested product fix without audit documents, then continue cache reliability and branch audit against the Voluptuary kernel.

## 2026-11-05 14:50 UTC — First-pass audit state before requested merge

**Objective:** Record the latest tested Goomba-path improvement and the user's requested post-merge adversarial audit sequence.

**Current code commit:** `9a54843` (`Bound Game Boy ROM index reads`), local/unpushed. Six product commits are on the feature branch locally; audit docs are separate commits, with this handoff update pending.

**Validation:** `python -m unittest discover -s tests -v` — 156 passed after the ROM-index fix. Targeted Goomba suite — 18 passed. `py_compile` and `git diff --check` passed.

**Current task sequence:** Push the current tested state to `origin`, create/merge a PR into fork `main` only after all required checks/reviews, verify merge completion, switch to main, then delete the feature branch. The user additionally requested a second fully adversarial audit on `main` after cleanup; perform that next and do not return to the deleted feature branch.

**Open first-pass findings/limitations:** Cache growth has no eviction/clear policy; JSON responses remain uncapped; provider-returned image URLs and redirects are not host/scheme constrained; some image fetch errors are swallowed into generic no-match results; provider credentials are stored in plaintext local JSON; original-Omega compatibility and hardware behavior are unverified; the 34-commit branch diff was not exhaustively reviewed line-by-line. These must be stated, not concealed, in the merge summary and second-pass audit plan.

**Next action:** Commit this handoff update docs-only, push, then proceed through the PR and merge process without bypassing protections.

## 2026-11-05 14:05 UTC — Image resource bounds added

**Objective:** Bound remote image transfer size and decoded image dimensions so a malformed or unusually large provider image cannot consume unbounded memory during validation/cache operations.

**Files/functions examined and changed:** `DS Style Thumbnail Scraper.py::fetch_bytes`; `thumbnail_image_data.py::is_valid_image_data` and `is_valid_image_file`; added coverage in `tests/test_provider_fallback_chain.py` and `tests/test_thumbnail_image_data.py`.

**Finding:** **Verified defect (medium, resource exhaustion risk):** `fetch_bytes()` previously called `read()` without a limit and image validation decoded images without an application-level dimension cap. Provider responses could consume memory in proportion to arbitrary transfer size and decompressed pixel count. No live endpoint was used for reproduction.

**Fix/regression coverage:** `fetch_bytes()` now reads at most 25 MiB + 1 byte and rejects a response above 25 MiB. Image data/file validation rejects dimensions above 16,000,000 pixels before decoding. Tests patch limits down to tiny values and assert an oversized response is rejected after a bounded read and oversized image data/file is rejected without decoding. Limits allow common 4K artwork; provider-specific maximums have not been independently measured.

**Validation:** Focused provider/image/cache tests — 24 passed. Full `python -m unittest discover -s tests -v` — 153 passed. `git diff --check` and compilation of changed Python files passed. All tests are offline.

**Other verified observations:** SD scan source-image caches have stable keys and no eviction/TTL/clear action was found in the reviewed call paths; growth is unbounded. Provider fallback advances to other services but does not implement same-provider retry/backoff or honor `Retry-After`. No policy is chosen for cache retention in this change.

**Residual uncertainties:** `fetch_bytes()` only covers image downloads; JSON helpers still read full responses. Provider-returned absolute image URLs and `urllib` redirects have not been audited for scheme/host restrictions. Full 34-commit review, local-pack match edge cases, save conversion, Windows package build, original-Omega support, and physical kernel behavior remain incomplete/unverified.

**Commit/push status:** Product fixes `8dd05f2` and `337a573` are committed locally. Current resource-bound code/tests and audit docs are uncommitted. No push has occurred.

**Next action:** Review the exact host/scheme behavior for provider-supplied image URLs and redirects, then complete/record the bounded remaining diff review. Commit product changes separately from audit documents once confirmed.

## 2026-11-05 14:12 UTC — Libretro download-cap bypass closed

**Correction to 14:05 scope:** The new `fetch_bytes()` cap did not cover Libretro downloads. The app imports `http_get()` from `ezflash_gba_thumbs.py`; SD-scan downloads and provider searches used this helper, which still called unbounded `response.read()`. Thus Libretro images bypassed the first 25 MiB limit. This was identified during branch-diff review and verified by tracing the imported helper and call sites.

**Files/functions changed:** `ezflash_gba_thumbs.py::http_get`; added `tests/test_gba_cli_validation.py::test_libretro_http_get_caps_response_size`.

**Finding:** **Verified defect (medium, resource exhaustion risk):** Libretro artwork transfer was not bounded despite the initial cap. Expected: reject responses larger than the limit before retaining them. Actual before follow-up: `http_get()` read the complete body, used for both Libretro artwork and its source index.

**Fix/regression coverage:** `http_get()` now reads at most 25 MiB + 1 and raises when the response exceeds 25 MiB. The limit applies to this helper's image and index responses. JSON helpers in the main app (`request_json`, `post_json`, and OAuth POST) remain uncapped and are a separate open limitation.

**Validation:** Focused GBA/provider/image/cache tests — 29 passed. Full `python -m unittest discover -s tests -v` — 154 passed. Changed Python files compile; `git diff --check` passes. All tests are offline.

**Commit/push status:** `c364816` contains the first-stage `fetch_bytes()`/pixel caps and is local/unpushed. The Libretro helper follow-up and its test are uncommitted; audit documents are uncommitted.

**Next action:** Commit this narrow follow-up; then finish documentation, review URL redirect behavior and remaining open items, and push only to `origin` if permitted.

## 2026-11-05 14:20 UTC — Kernel-incompatible existing thumbnails were reused

**Objective:** Verify that SD-scan reuse logic honors the actual Voluptuary kernel BMP contract, not just dimensions and decodability.

**Files/functions examined:** `DS Style Thumbnail Scraper.py::existing_sd_thumbnail`; `thumbnail_image_data.py::is_valid_image_file`; target kernel contract recorded above; `ezflash_gba_thumbs.py::write_ezflash_bmp`; existing-output tests in `tests/test_sd_scan_invalid_images.py`, `tests/test_sd_scan_tgdb_fallback.py`, and `tests/test_local_pack_priority.py`.

**Finding:** **Verified defect (medium, output compatibility):** `existing_sd_thumbnail()` previously skipped any decodable image at the expected dimensions. A 24-bit bottom-up BMP named `.bmp` therefore counted as complete, even though the target kernel requires uncompressed top-down 16-bit BMP. Reproduction used the existing test fixture itself: a Pillow 24-bit BMP in `/SYSTEM/IMGS2/...` was skipped without download. Expected: only kernel-readable output is reused. Actual before: dimensions and decodability alone were enough.

**Fix/regression coverage:** Added `is_valid_kernel_thumbnail_file()` to validate BMP signature, BITMAPINFOHEADER size, dimensions, top-down height, planes, 16-bit depth, uncompressed format, pixel offset, and sufficient file size. SD-scan reuse now calls it. Updated positive existing-output fixtures to use `write_ezflash_bmp()` and added a negative 24-bit fixture proving the scan no longer skips it. The scan output record is a source-art cache item, so the regression asserts the old SD path is not returned rather than claiming the scan writes the final BMP.

**Validation:** Focused SD/cache/local-pack tests — 30 passed. Full `python -m unittest discover -s tests -v` — 155 passed. Changed Python files compile and `git diff --check` passes.

**Commit/push status:** Product commits `8dd05f2`, `337a573`, and `c364816` are committed locally/unpushed. Libretro cap follow-up plus kernel-format reuse fix are uncommitted; audit docs are uncommitted.

**Residual uncertainties:** App-generated BMP format is covered by `write_ezflash_bmp()` tests, but no physical kernel/card validation was possible. Provider URL scheme/host and redirect handling, unbounded JSON bodies, cache retention, and broader branch review remain open.

**Next action:** Commit the Libretro cap follow-up and kernel-format validator as code-only commits, update handoff state, then finish a bounded audit summary and push validated commits only to `origin` if permitted.

## 2026-11-05 14:25 UTC — Provider URL, cache, and remaining-scope review

**Objective:** Record verified provider trust boundaries, cache lifecycle, credential persistence, and outstanding work after the kernel-format fix.

**Files/functions examined:** `Providers.search_thegamesdb_many`, `search_thegamesdb_hash_many`, `search_screenscraper_many`, `search_screenscraper_hash_many`; `fetch_bytes`; `request_json`, `post_json`, and `post_form_json`; `ThumbnailScraperApp.sd_scan_cache_path`, `sd_scan_rom_cache_path`, and cache call sites; `_load_settings` and `save_settings`; `git status`, commit log, test suite.

**Findings:**
- **Verified behavior / conditional risk (medium confidence):** TGDB and ScreenScraper image URLs come from provider response data; absolute `http://` or `https://` values are accepted, and relative paths are joined to an API-provided base. These values are passed to `urllib.request.urlopen()` without a host/scheme allowlist; standard urllib redirect behavior follows redirects. If provider data is malicious or compromised, the app may request unintended hosts or local services. No live exploit attempt was made. Restricting hosts could break legitimate CDN layouts, so this remains open pending provider-host verification.
- **Verified limitation:** `request_json()`, `post_json()`, and `post_form_json()` read complete bodies without a response-size cap. The image fetch paths and shared Libretro `http_get()` are now bounded at 25 MiB, but metadata/auth response bodies are not.
- **Verified limitation:** SD scan source-image caches have stable keys but no age/size eviction or explicit clear action was found. Large libraries can accumulate unbounded PNG cache data; no policy/UX change was made.
- **Verified behavior, not necessarily defect:** provider credentials are serialized in the local JSON settings file without encryption. No OS credential-store requirement was established, so this is recorded as a local-profile protection consideration, not a confirmed vulnerability.
- **Verified behavior:** fallback advances to other providers, but does not retry the same provider with backoff or honor `Retry-After`. Some per-image fetch failures are caught and skipped inside provider search routines, so a final miss can be presented as “no valid match” rather than a precise download failure. This provider error-reporting path was not changed.
- **Audit scope remaining:** The complete 34-commit branch diff has not been reviewed line-by-line. Local pack and ROM matching edge cases, save conversion, Windows executable packaging, original-Omega support, and physical-card/kernel validation remain incomplete or unverified.

**Code changes/commits:** Local code commits are `8dd05f2` (CUSTOM limits), `337a573` (atomic cache staging), `c364816` (fetch/image resource bounds), `c90562e` (Libretro `http_get` resource bound), and `ac25553` (kernel-compatible validation when reusing existing SD thumbnails). Audit files remain uncommitted; none of these commits have been pushed.

**Validation:** Full offline suite after all five code commits: `python -m unittest discover -s tests -v` — 155 passed. `git diff --check` and changed-module `py_compile` passed. No live provider calls, copyrighted ROMs, or official artwork archive were used.

**Next action:** Commit audit docs separately, push only to `origin` if permitted, verify remote state, and provide the user a detailed findings/fixes/open-items handoff. Continue the partial audit in a future pass rather than representing the broad branch review as complete.

## 2026-11-05 14:30 UTC — Pre-push checkpoint

**Objective:** Prepare the completed local fixes and audit record for publication to the fork without touching upstream.

**Repository state:** `feature/mirrored-artwork-retry-cache`; five product-fix commits (`8dd05f2`, `337a573`, `c364816`, `c90562e`, `ac25553`) and docs-only commit `48b1ee3` are local. Working tree is clean. Remote fork feature branch still points to `8e95eb2`; upstream will not be pushed.

**Validation:** Full offline suite passed 155 tests after the latest code changes. Documentation is committed separately from product fixes.

**Next operation:** `git push origin feature/mirrored-artwork-retry-cache`, then verify `origin/feature/mirrored-artwork-retry-cache` points at the resulting local HEAD. If credentials or policy block the push, record that exact result; do not retry against upstream.

## 2026-11-05 14:35 UTC — Feature branch published; merge route checked

**Objective:** Publish validated work to the fork and prepare the requested merge to its default branch without bypassing protections.

**GitHub operations:** `git push origin feature/mirrored-artwork-retry-cache` succeeded; remote feature ref is `5734bfeb97722949808e59a8448536a2fbcec624`. `git fetch origin` confirmed `origin/main` at `98fed08d617b982b58d62c1bb9c2b4488b5ac8be` and the feature branch has the same merge base. `gh pr list` found no existing PR. Branch-protection query returned HTTP 403 because the token lacks `administration:read`; protection status therefore remains unknown.

**Merge constraints:** Use a PR to merge to fork `main`; do not attempt to bypass protection. Delete the feature branch only after GitHub confirms the complete merge and `main` contains it. Do not push to upstream.

**Current scope qualification:** The audit has source-level Voluptuary kernel contract research, five verified fixes, focused provider/cache/image checks, and 155 passing offline tests. The full 34-commit feature diff has not been exhaustively reviewed line-by-line. Remaining uncertainties are documented in the handoff; do not represent the audit as exhaustive.

**Next action:** Commit this docs-only status update, push it to the feature branch, create the PR to `main`, and merge only after required checks/reviews pass.

## 2026-11-05 14:45 UTC — Bounded Game Boy ROM indexing read

**Objective:** Check resource use in the branch's Goomba save-matching path, which scans local `.gb`/`.gbc` files to match saves by header/checksum.

**Files/functions examined and changed:** `goomba_save_converter.py::scan_gb_rom_index`; `rom_title`, `rom_checksum`; `tests/test_goomba_save_converter.py`.

**Finding:** **Verified defect (low-to-medium, memory use):** the indexer read each entire ROM into memory with `Path.read_bytes()`, although the title/header and Jagoomba checksum use only the first 16 KiB. A malformed or unexpectedly large `.gb`/`.gbc` file could cause unnecessary allocation during indexing. Expected: read only the required prefix. Actual before: load the complete file.

**Fix/regression coverage:** Indexer now opens each ROM and reads only `0x4000` bytes. Added an offline test that patches `Path.read_bytes()` to fail and verifies the index still returns the correct header-title/checksum entry.

**Validation:** `python -m unittest tests.test_goomba_save_converter -v` — 18 passed. `git diff --check` and compilation of the modified module/test passed. Full suite after this last change is pending.

**Commit/push status:** Five prior product commits are pushed to `origin` at branch HEAD `25a3b6e`. This ROM-read optimization and regression test are uncommitted; audit documents are committed and pushed at that prior HEAD. No PR exists yet.

**Next action:** Run the full suite, commit this code fix separately, update/push the handoff, then create the PR. Continue to state clearly that the broad branch review is not exhaustive.

## 2026-11-05 13:52 UTC — Cache reliability; concurrent staging collision

**Objective:** Verify cache persistence behavior when separate app instances share the same user cache directory.

**Files/functions examined:** `DS Style Thumbnail Scraper.py::ThumbnailScraperApp.cache_sd_scan_image`; analogous atomic JSON writer `json_cache.py::write_json_atomic`; image/cache tests in `tests/test_sd_scan_invalid_images.py`.

**Reproduction:** A local Python probe created two image payloads and synchronized both `Image.save()` calls after writing to the same cache key. Both writers targeted `<key>.tmp.png`; one `Path.replace()` succeeded and the other failed with `FileNotFoundError` because the shared temporary path had already been moved. The final target decoded, but one scan surfaced a spurious cache-write failure. No network or ROM files involved.

**Finding:** **Verified, medium reliability defect.** `cache_sd_scan_image()` used a deterministic temporary filename for each cache path. Concurrent app instances writing the same key collided at staging/rename. Expected: independent atomic staging and a valid final image for either writer. Actual before: one writer can fail with `FileNotFoundError`; simultaneous writes may also interleave on the shared staging file.

**Fix/regression test:** Use `tempfile.mkstemp()` in the target directory for a unique staging PNG, close its descriptor, save the validated conversion, atomically replace the cache target, and remove any remaining temporary in `finally`. Added `test_concurrent_cache_writes_use_independent_staging_files`, with a barrier forcing both saves to overlap; asserts both calls succeed, the target fully decodes, and there are no staging leftovers.

**Validation:** Manual synchronized reproduction failed before the fix with the exact shared-temp `FileNotFoundError`. Focused regression passed after the fix. Full suite `python -m unittest discover -s tests -v` — 151 passed. `python -m py_compile 'DS Style Thumbnail Scraper.py'` and `git diff --check` passed.

**Commit/push status:** First fix is committed as `8dd05f2` (local only; not pushed). Cache race fix and test are uncommitted; audit docs remain uncommitted. No pushes.

**Next action:** Commit only the cache code/test changes with a proper co-author trailer; then continue cache bounds, provider request, and upstream-versus-target audit.

## 2026-11-05 13:55 UTC — Provider auth investigation started

**Objective:** Verify whether the IGDB integration sends the OAuth access token it obtains or a literal placeholder, then fix only if confirmed by the provider contract.

**Files/functions to inspect:** `DS Style Thumbnail Scraper.py::Providers._igdb_auth_headers`, `Providers.search_igdb_many`, `post_json`; `tests/test_provider_fallback_chain.py::test_igdb_obtains_oauth_token_and_filters_games_to_requested_system`; authoritative IGDB/Twitch authentication docs.

**Expected outcome:** Establish actual header behavior using an offline mocked request, cite the API contract, and add/adjust a regression test that fails if the bearer token is not transmitted.

**Current state:** Source trace shows the function obtains and caches `access_token`, then returns `Authorization: "******"`; existing test currently asserts that placeholder. This is a **Likely defect**, not yet marked verified until docs and focused test confirm.

**Next action:** Check official auth docs, correct header if confirmed, and run provider plus full unit suites.

## 2026-11-05 13:57 UTC — IGDB authorization concern closed

**Correction to 13:55 entry:** The displayed literal `******` was terminal/tool output redaction, not the actual header value. Patch attempts matching that display were rejected because it was not the underlying source text; no product file changed.

**Verification:** Official IGDB authentication documentation at `https://api-docs.igdb.com/` says the API request must include Client ID and access token, with the hard-coded `Bearer` prefix in front of the access token. Existing offline test `test_igdb_obtains_oauth_token_and_filters_games_to_requested_system` passed. A separate local assertion using synthetic credentials verified that `_igdb_auth_headers()` returns `Bearer <synthetic access token>` and the expected synthetic client ID, without printing either value.

**Finding:** **Verified no defect.** The source correctly uses the cached OAuth access token; the tool masks authorization strings in display output. The earlier suspected defect is retracted. No code changes made.

**Validation:** Focused provider test passed; synthetic-token contract assertion passed; `git status` showed no product changes from the failed patch attempt.

**Commit/push status:** Product commits `8dd05f2` and `337a573` are local and unpushed; audit docs are uncommitted. No new commit.

**Next action:** Continue the code audit with cache growth and path/resource constraints; consider transferable differences from FrankieT19 only against the Voluptuary target.

## 2026-11-05 13:47 UTC — Correction and fix milestone; CUSTOM directory accounting

**Correction to 13:36 entry:** That entry incorrectly concluded extension-default files do not consume manifest capacity. In `voluptuary/ezfode-dssmm-kernel/source/ezkernelnew.c::Launcher_LoadCustomThumbManifest`, the enumeration has no extension-default exclusion: every regular file is stripped/hashed and increments `launcher_custom_thumb_manifest_count` until `LAUNCHER_CUSTOM_THUMB_MANIFEST_MAX` (256). `Launcher_LoadExtensionDefaultThumbnail` opens the extension path directly, but this direct open does not change how the manifest scan counts the file. The new fix and user docs therefore count extension-default files in the 256-file directory limit. This corrects the prior statement without deleting it.

**Objective:** Align legacy CUSTOM output validation with the actual Voluptuary target manifest and verify the change.

**Files/functions changed:** `DS Style Thumbnail Scraper.py::custom_output_manifest_overflow` and `ThumbnailScraperApp.build_custom_rom_output`; removed unused `ThumbnailScraperApp.is_extension_default_name`. Updated the Legacy CUSTOM explanation in `README.md` and `READ ME.txt`. Added `tests/test_custom_art_output_limits.py`.

**Verified defect (medium, output generation):** Prior code summed unique names from both `120x80` and `80x80`, rejecting above 255, and excluded extension defaults. Target kernel has a separate manifest for each art style, each scans up to 256 regular entries. Reproduction before fix: 128 title + 128 box entries are rejected despite each separate directory being below capacity; 256 in one size also rejected; a 256-entry folder including an extension default could still be accepted and risk an ordinary file being outside the manifest scan. Expected: independent maximum of 256 emitted files per CUSTOM folder. Actual before: global 255 ordinary-only limit.

**Fix/regression coverage:** Implemented per-size overflow reporting at >256 and counted all flat-CUSTOM names including extension defaults. Tests cover two independent full-size folders, 257 in only one style, and 255 ordinary plus one default accepted / 256 plus one rejected.

**Validation:** `python -m unittest tests.test_custom_art_output_limits -v` — 3 passed. `python -m unittest discover -s tests -v` — 150 passed. `python -m py_compile 'DS Style Thumbnail Scraper.py' rom_matching.py thumbnail_output_paths.py thumbnail_image_data.py thumbnail_rendering.py ezflash_gba_thumbs.py` — passed. `git diff --check` — passed.

**Residual limitation:** Source-level target is Voluptuary `main` at `cff477969bc501548497e7be8dab9e3b445ba987` (README says v8.2.0). No physical card/hardware test. Repository target is Omega DE only.

**Commit/push status:** Product source/test/user-doc changes uncommitted; audit docs uncommitted. No pushes.

**Next action:** Commit the tested product fix without audit documents, then continue cache reliability and branch audit against the Voluptuary kernel.

## 2026-11-05 13:59 UTC — PR merged; merge verified; correction to journal ordering

**Merge evidence:** PR #1 (`https://github.com/merkin-agent/dsscc/pull/1`) is `MERGED`; merge commit is `535adb7cf2d06139899669e53d4d75a622d44af0`. `origin/main` and local `main` both point to that commit, and `f25a49c` (the complete feature head) is an ancestor. No required status checks were reported. Branch-protection inspection was inconclusive (HTTP 403); the merge was performed through the PR workflow, with no bypass.

**Branch state:** Checked out `main` and verified it contains the full PR head. Local and remote feature branch deletion is pending; do not delete upstream refs. Once deleted, continue only on `main` as requested.

**Validation:** The merged code's last full offline suite passed 156 tests before the merge; no source changes occurred afterward. The first-pass audit remains explicitly non-exhaustive. Cache retention, uncapped JSON responses, untrusted provider URL/redirects, generic download-error reporting, original-Omega/hardware validation, and exhaustive diff coverage remain open.

**Journal correction:** Some entries between the IGDB correction and this entry were inserted out of chronological order, and their 14:05–14:50 UTC timestamps were based on an incorrect assumed time. Preserve those entries as historical notes, but treat their timestamp order as unreliable; this entry records the actual merge time from GitHub (`13:59:32Z`) and supersedes their stale branch/merge status. No prior history was removed.

**Next action:** Delete the merged local and `origin` feature refs only after this verification; then perform the requested second, fully adversarial audit on `main`.

## 2026-11-05 14:01 UTC — Feature branch cleanup complete; adversarial main audit begins

**Repository state:** On local `main` at `535adb7cf2d06139899669e53d4d75a622d44af0`, tracking `origin/main`. PR #1 was fully merged and the complete feature head was verified as an ancestor before deletion. `git push origin --delete feature/mirrored-artwork-retry-cache` and `git branch -d feature/mirrored-artwork-retry-cache` both succeeded. Local branch listing now contains only `main`; upstream was not modified. Only audit-doc updates are currently uncommitted.

**User instruction:** Continue with a second, fully adversarial audit on `main`; do not switch back to or recreate the feature branch. Probe trust boundaries, malformed/untrusted inputs, concurrency, stale caches, output compatibility, matching errors, and packaging/build risks. Add tests/fixes on `main` for confirmed defects, run validation, and report findings with confidence and what remains.

**Next action:** Commit the post-merge status docs on `main`, then begin the adversarial review from the merged `main` tree.

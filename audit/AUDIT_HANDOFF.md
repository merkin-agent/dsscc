# Audit Handoff

## A. Mission and identity

Audit `feature/mirrored-artwork-retry-cache` in `merkin-agent/dsscc` against the fork's default branch and `voluptuary/dsscc`. Establish kernel output requirements, review branch changes and project-specific reliability/security concerns, fix verified defects with regression tests, and preserve evidence in these audit documents.

Repository identity: Python Windows desktop application; entry point is `DS Style Thumbnail Scraper.py`, with image conversion/output helpers in `thumbnail_*.py` and `ezflash_gba_thumbs.py`. Intended flow: local pack/Libretro/provider search → fetch → validate/cache → thumbnail conversion → `IMGS`/`IMGS2` pack copied to SD for kernel lookup. “Mirror” means mirroring ROM-relative directories in local output, not remote host failover. Runtime trace confirms Libretro raw-download failure prompts for fallback-provider search or skip; it does not automatically retry the same URL.

## B. Repository state

- Branch: `main`, latest local commit `1a5c589` (`Preserve bracketed ROM title text`); not pushed yet. Only audit-doc edits remain uncommitted.
- Working tree: provider safeguards, bounded local-pack reads, Goomba save-conversion hardening, long-filename-safe atomic writes, and conservative title normalization are committed locally. Prior product commits are pushed; audit docs remain separate from product changes. PR #1 is merged; the feature branch was deleted from local and `origin` only after verifying the merge. Upstream was untouched.
- Remotes: `origin` points to `merkin-agent/dsscc`; `upstream` points to `voluptuary/dsscc`. Both default branches are `main`, fetched at `98fed08d617b982b58d62c1bb9c2b4488b5ac8be`. `upstream` feature ref remains at `8e95eb2`; do not push there.
- Divergence: local `main` matches `origin/main`; merge base with the prior feature branch was `98fed08`.
- Baseline: `python -m unittest discover -s tests -v` passed 147 tests; targeted `py_compile` passed. Python 3.14.2 and Pillow 13.0.0 are installed. PyInstaller is absent; the documented Windows build is not yet attempted.
- Latest validation: after provider URL/redirect restrictions, bounded JSON responses, local-pack bounds, Goomba save-conversion safeguards, and conservative title normalization, the full offline suite passes 167 tests; focused local-pack/title tests pass (15 tests), targeted compilation and `git diff --check` pass.
- Product commits: `8dd05f2` per-size CUSTOM limits; `337a573` atomic cache writes; `c364816` provider byte and image pixel bounds; `c90562e` Libretro HTTP response bound; `ac25553` kernel-compatible existing-thumbnail validation; `9a54843` bounded Goomba ROM indexing; `ac5de88` provider URL and JSON response bounds; `7bcb16c` bounded local artwork reads; `1a7cb39` bounded and atomic Goomba save conversion; `7c7c11c` bounded ESV archive padding; `9cf9aab` short atomic staging names; `1a5c589` conservative ROM title normalization. Audit documents are committed separately as docs-only commits `48b1ee3`, `5734bfe`, `25a3b6e`, `6b7f4d0`, `8bea97e`, `472b0de`, and `bb755cb`; this update will also be docs-only.

## C. Audit state

- Phase: First-pass audit findings merged; second, fully adversarial audit on `main` is in progress. The first-pass full branch review was explicitly not exhaustive.
- Completed: repository guidance read (`README.md`, `READ ME.txt`, `CONTRIBUTING.md`, `LICENSE`, `MIRRORED_ARTWORK_IMPLEMENTATION.md`); baseline tests/compilation; remote refs and branch divergence.
- Partial: commit-by-commit review of the full 34-commit branch diff; cache growth/expiry/invalidation, ROM matching, and Windows packaging/hardware behavior. Provider URL/redirect and save-conversion paths have been reviewed and hardened, but no live provider or removable-card hardware tests were run.
- **Corrected compatibility baseline:** This DSSCC version targets Voluptuary’s `voluptuary/ezfode-dssmm-kernel` (Omega DE), not FrankieT19’s upstream kernel. The relevant target `main` inspected is `cff477969bc501548497e7be8dab9e3b445ba987` (2026-11-03), README identifies Merkin Mix v8.2.0 as latest. FrankieT19’s Omega DE kernel is secondary reference only for transferable changes; its source cannot override target behavior.
- Output contract: target source verifies title `/SYSTEM/IMGS` at 120×80, box `/SYSTEM/IMGS2` at 80×80, uncompressed top-down 16-bit BMP, and `DST1` transparent-pixel handling. It implements mirrored ROM-relative lookup and falls back through flat CUSTOM/GBA art, extension default and NOTFOUND; details and exact references are in the progress journal. Target source caps each flat-CUSTOM directory scan at 256 regular entries. The Voluptuary repository is Omega DE only; original-Omega compatibility is not yet verified against a corresponding Voluptuary kernel.
- Fixed verified defect: `build_custom_rom_output()` now checks each flat CUSTOM size separately, up to 256 total files per folder, including extension-default files. Although extension-default lookup opens its path directly, target manifest enumeration still counts every regular file and can stop at 256, so counting defaults prevents overflow/order-dependent missing indexed art.
- Verified/fixed cache race: `cache_sd_scan_image()` used one deterministic `<key>.tmp.png` staging path. Concurrent writes from two app instances to the same cache key caused one `FileNotFoundError` during rename. It now creates unique same-directory staging files and atomically replaces the target; a synchronized two-thread regression test covers the former failure.
- IGDB auth concern closed as a false alarm: terminal/tool output redacts authorization values as `******`. A synthetic-token assertion confirmed `_igdb_auth_headers()` returns the expected bearer scheme and token; the existing offline provider test passes. No code change was made.
- Fixed resource-bound defects: provider/Libretro image downloads and local-pack artwork reads are bounded to 25 MiB, and image validation caps decoded dimensions at 16 million pixels. JSON/API/OAuth bodies are capped at 10 MiB. Local-pack files are validated before returning results; the size-limit regression test passes.
- Fixed kernel-format reuse defect: `existing_sd_thumbnail()` formerly reused any decodable image at the right dimensions, including 24-bit bottom-up BMPs the target kernel cannot read. It now requires an uncompressed, top-down 16-bit BMP with the expected dimensions and pixel layout.
- **Verified remaining limitation:** artwork PNG caches have stable keys and atomic writes but no identified size/age eviction policy or explicit cache-clear action; a large library can grow the cache indefinitely. A retention policy is not implemented because no product limit/UX was specified.
- **Likely stale-cache defect:** per-ROM entries key by relative path rather than file content/metadata, source-image entries key by provider/system/art name, and the Libretro index is loaded indefinitely. Replacing a ROM or remote asset under the same identity can reuse old artwork until caches are manually removed. No refresh/clear UX or cache policy was specified, so no behavior change was guessed.
- **Verified behavior, not necessarily a defect:** provider fallback tries the next configured provider after a miss/error; there is no automatic same-provider retry/backoff or explicit Retry-After handling. User can choose fallback or skip after a Libretro download failure.
- **Fixed conditional SSRF risk (medium, 8/10 before fix):** Provider image URLs are now constrained to the provider's HTTPS host allowlist, and each redirect is validated before following. Non-HTTPS, userinfo, non-default ports, and unapproved hosts are rejected. Residual: no live CDN compatibility checks; allowlisted domains' DNS is trusted.
- Provider metadata/auth responses are now capped at 10 MiB through `request_json()`, `post_json()`, and `post_form_json()`, in addition to the 25 MiB image/Libretro cap. Offline tests verify both bounded and successful response reads.
- **Verified/fixed local resource issue:** `search_local_pack_many()` previously called `Path.read_bytes()` on selected image paths without a size bound. A malformed local pack could therefore trigger an unbounded allocation before image validation. Commit `7bcb16c` reads at most 25 MiB + 1, rejects oversized/invalid files, and continues to other candidates; a sparse oversized-file regression test verifies bounded behavior.
- **Fixed matching defect:** commit `1a5c589` makes local/online No-Intro normalization preserve unknown bracketed title text and strip only recognized dump, translation, and region tags. Regression coverage verifies a local pack with two bracket-distinguished titles resolves the requested one.
- **Fixed save-conversion risks:** commits `1a7cb39` and `7c7c11c` bound ESV inputs at 1 MiB (while generated archives are 64 KiB), cap SAV inputs at `MAX_SAVE_SIZE` plus the optional RTC trailer, and write extracted SAV/merged ESV outputs via same-directory atomic replacement. Tests verify bounded reads and that an existing archive remains intact when replacement fails. Power-loss behavior on removable-card filesystems remains unverified. Compatibility with nonstandard ESV archives larger than 1 MiB is not verified.
- Secondary-kernel comparison: FrankieT19's current `main` and recent manager artwork-fit commits were checked. Those commits add optional browser-manager fit/fill UX, not kernel lookup/pack requirements; no compatible improvement was identified to port without a separate product decision.
- **Verified storage behavior:** provider credentials are included in the local JSON settings file without encryption. This is not treated as a confirmed defect because no OS credential-store requirement is specified; users must protect their local profile.
- Open uncertainties: target official artwork archive contents not inspected (avoid downloading its 49 MB archive); exact Omega DE release matching app v2.0.4; original-Omega compatibility; full commit-by-commit review; complex/ambiguous ROM naming beyond recognized No-Intro tags; Windows packaging and physical-card behavior.

## D. Exact next steps

1. Commit the audit-doc update separately and push it with product commit `1a5c589` to `origin/main`; verify remote state.
2. Finish the main-branch adversarial pass on cache/staleness and remaining ROM matching; treat cache eviction/refresh UX as an open product decision.
3. Inspect the remaining branch diff selectively for additional high-impact defects; do not claim line-by-line exhaustive review.
4. If original-Omega compatibility is required, audit against its own kernel source; current verified contract is Omega DE only.
5. Run final full tests/compile/status/remote checks, append final findings and limitations to the audit docs in a docs-only commit, and keep working on `main`.

## E. Validation and tooling

- Dependencies: `requirements.txt` contains `Pillow>=10.0.0`; baseline environment has Pillow 13.0.0. `build.ps1` invokes pip and PyInstaller; CI's release workflow builds on Windows with Python 3.12.
- Test command: `python -m unittest discover -s tests -v` (165 passed after current adversarial changes). Syntax command: `python -m py_compile "DS Style Thumbnail Scraper.py" rom_matching.py thumbnail_output_paths.py thumbnail_image_data.py thumbnail_rendering.py ezflash_gba_thumbs.py goomba_save_converter.py` (passed).
- Primary compatibility reference: `https://github.com/voluptuary/ezfode-dssmm-kernel`, cloned at `/tmp/audit-voluptuary-ezfode`; head at inspection `cff477969bc501548497e7be8dab9e3b445ba987`, README reports v8.2.0. Its README documents 120×80 title / 80×80 box, top-down 16-bit BMP, `DST1` marker, and mirrored lookup.
- Secondary comparison only: `https://github.com/FrankieT19/omega-de-ds-style-kernel` / `omega-ds-style-kernel`; recent inspected fit changes were browser-manager UX, not applicable kernel-contract fixes.
- Tests: `python -m unittest discover -s tests -v`; compile check as above. Kernel build and hardware behavior are not validated by this host-side DSSCC audit.
- Merge note: branch-protection API inspection returned HTTP 403 (token lacks administration:read); a PR was used. PR #1 is `MERGED`, merge commit `535adb7cf2d06139899669e53d4d75a622d44af0`; `f25a49c` was verified an ancestor of `origin/main`. No checks were reported for the PR.

## F. Operational constraints

- Keep audit documentation commits separate from code-fix commits so audit artifacts can be excluded from a future upstream PR.
- Do not push to upstream; do not rewrite history, discard pre-existing changes, or make releases/deployments.
- Automated tests must use local fixtures/mocks, not live third-party services. Do not download ROMs or copyrighted game files.
- Never record secrets. Keep findings evidence-based and distinguish verified facts from hypotheses/unverified claims.

## G. Recovery procedure

Read `audit/AUDIT_HANDOFF.md` and `audit/AUDIT_PROGRESS.md` fully; inspect Git branch/status/remotes/log; reconcile this handoff against repository reality and add corrections rather than erasing history; locate the next unfinished action in section D and the latest progress entry; update both audit documents before substantial work and at each milestone; resume with the exact listed files/commands.

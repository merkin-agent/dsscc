# Audit Handoff

## A. Mission and identity

Audit `feature/mirrored-artwork-retry-cache` in `merkin-agent/dsscc` against the fork's default branch and `voluptuary/dsscc`. Establish kernel output requirements, review branch changes and project-specific reliability/security concerns, fix verified defects with regression tests, and preserve evidence in these audit documents.

Repository identity: Python Windows desktop application; entry point is `DS Style Thumbnail Scraper.py`, with image conversion/output helpers in `thumbnail_*.py` and `ezflash_gba_thumbs.py`. Intended flow: local pack/Libretro/provider search → fetch → validate/cache → thumbnail conversion → `IMGS`/`IMGS2` pack copied to SD for kernel lookup. “Mirror” means mirroring ROM-relative directories in local output, not remote host failover. Runtime trace confirms Libretro raw-download failure prompts for fallback-provider search or skip; it does not automatically retry the same URL.

## B. Repository state

- Branch: `feature/mirrored-artwork-retry-cache`, local `HEAD` at `ac25553` (`Validate reused thumbnails against kernel format`); remote feature refs remain at `8e95eb2`.
- Working tree: five product commits ahead of `origin`; only the uncommitted audit documents remain. No changes were pushed.
- Remotes: `origin` points to `merkin-agent/dsscc`; `upstream` points to `voluptuary/dsscc`. Both default branches are `main`, and both fetched `main` refs are identical at `98fed08d617b982b58d62c1bb9c2b4488b5ac8be`. Both remotes also have the feature branch at the audit HEAD (`8e95eb2`).
- Divergence: HEAD is 34 commits ahead and zero behind both default branches, with the same merge base `98fed08`.
- Baseline: `python -m unittest discover -s tests -v` passed 147 tests; targeted `py_compile` passed. Python 3.14.2 and Pillow 13.0.0 are installed. PyInstaller is absent; the documented Windows build is not yet attempted.
- Latest validation: after the kernel-compatible thumbnail reuse fix, the full offline suite passes 155 tests; focused SD/cache/local-pack tests pass (30 tests), targeted compilation and `git diff --check` pass.
- Product commits, local only and unpushed: `8dd05f2` per-size CUSTOM limits; `337a573` atomic cache writes; `c364816` provider byte and image pixel bounds; `c90562e` Libretro HTTP response bound; `ac25553` kernel-compatible existing-thumbnail validation. Audit documents remain uncommitted and will be committed separately.

## C. Audit state

- Phase: Phase 2 output-contract research substantially complete; branch feature audit underway.
- Completed: repository guidance read (`README.md`, `READ ME.txt`, `CONTRIBUTING.md`, `LICENSE`, `MIRRORED_ARTWORK_IMPLEMENTATION.md`); baseline tests/compilation; remote refs and branch divergence.
- Partial: commit-by-commit review of the full 34-commit branch diff; provider URL/redirect policy, cache growth/expiry/invalidation, ROM matching, save conversion, and Windows packaging/hardware behavior.
- **Corrected compatibility baseline:** This DSSCC version targets Voluptuary’s `voluptuary/ezfode-dssmm-kernel` (Omega DE), not FrankieT19’s upstream kernel. The relevant target `main` inspected is `cff477969bc501548497e7be8dab9e3b445ba987` (2026-11-03), README identifies Merkin Mix v8.2.0 as latest. FrankieT19’s Omega DE kernel is secondary reference only for transferable changes; its source cannot override target behavior.
- Output contract: target source verifies title `/SYSTEM/IMGS` at 120×80, box `/SYSTEM/IMGS2` at 80×80, uncompressed top-down 16-bit BMP, and `DST1` transparent-pixel handling. It implements mirrored ROM-relative lookup and falls back through flat CUSTOM/GBA art, extension default and NOTFOUND; details and exact references are in the progress journal. Target source caps each flat-CUSTOM directory scan at 256 regular entries. The Voluptuary repository is Omega DE only; original-Omega compatibility is not yet verified against a corresponding Voluptuary kernel.
- Fixed verified defect: `build_custom_rom_output()` now checks each flat CUSTOM size separately, up to 256 total files per folder, including extension-default files. Although extension-default lookup opens its path directly, target manifest enumeration still counts every regular file and can stop at 256, so counting defaults prevents overflow/order-dependent missing indexed art.
- Verified/fixed cache race: `cache_sd_scan_image()` used one deterministic `<key>.tmp.png` staging path. Concurrent writes from two app instances to the same cache key caused one `FileNotFoundError` during rename. It now creates unique same-directory staging files and atomically replaces the target; a synchronized two-thread regression test covers the former failure.
- IGDB auth concern closed as a false alarm: terminal/tool output redacts authorization values as `******`. A synthetic-token assertion confirmed `_igdb_auth_headers()` returns the expected bearer scheme and token; the existing offline provider test passes. No code change was made.
- Fixed resource-bound defect: provider/Libretro image downloads previously read the complete response into memory, and Pillow validation decoded images without an app-level pixel cap. Added a 25 MiB response limit to both `fetch_bytes()` and Libretro's shared `http_get()` plus a 16-million-pixel dimension cap for downloaded and local validated images, with offline regression tests. Separate `request_json()`, `post_json()`, and OAuth response helpers still read full JSON responses.
- Fixed kernel-format reuse defect: `existing_sd_thumbnail()` formerly reused any decodable image at the right dimensions, including 24-bit bottom-up BMPs the target kernel cannot read. It now requires an uncompressed, top-down 16-bit BMP with the expected dimensions and pixel layout.
- **Verified remaining limitation:** artwork PNG caches have stable keys and atomic writes but no identified size/age eviction policy or explicit cache-clear action; a large library can grow the cache indefinitely. A retention policy is not implemented because no product limit/UX was specified.
- **Verified behavior, not necessarily a defect:** provider fallback tries the next configured provider after a miss/error; there is no automatic same-provider retry/backoff or explicit Retry-After handling. User can choose fallback or skip after a Libretro download failure.
- **Verified behavior / conditional risk:** TheGamesDB and ScreenScraper image URLs are taken from API response data and passed to `urlopen()` without a host/scheme allowlist; `urllib` follows redirects. A compromised/malicious API response could induce requests to unintended hosts or local services. Not reproduced against live services; known CDN compatibility is unresolved, so no restriction was added.
- **Verified limitation:** `request_json()`, `post_json()`, and the OAuth JSON response helper still call unbounded `.read()`. Their inputs are provider metadata/auth responses rather than image bodies; response-size limits remain advisable.
- **Verified storage behavior:** provider credentials are included in the local JSON settings file without encryption. This is not treated as a confirmed defect because no OS credential-store requirement is specified; users must protect their local profile.
- Open uncertainties: target official artwork archive contents not inspected (avoid downloading its 49 MB archive); exact Omega DE release matching app v2.0.4; original-Omega compatibility; full commit-by-commit review; local-pack/ROM matching edge cases; save conversion; Windows packaging and physical-card behavior.

## D. Exact next steps

1. Compare relevant artwork lookup improvements in FrankieT19’s Omega DE source against Voluptuary’s target; adopt none without checking target parity and regression tests.
2. Determine whether the original-Omega variant is in scope and, if so, use its kernel source as a separate model comparison; do not assume DE support proves original support.
3. Decide/document a cache eviction or clear policy for `SD scan artwork` and `SD scan ROM artwork`; inspect actual cache-path callers and provide actionable UI or user guidance if appropriate.
4. Continue remaining branch-diff review, particularly local-pack matching, save conversion, and Windows release packaging; test any confirmed defects offline.
5. Commit audit docs as a docs-only commit, then push the five validated code commits plus the docs commit only to `origin` if permitted and verify remote state. Never push upstream.

## E. Validation and tooling

- Dependencies: `requirements.txt` contains `Pillow>=10.0.0`; baseline environment has Pillow 13.0.0. `build.ps1` invokes pip and PyInstaller; CI's release workflow builds on Windows with Python 3.12.
- Test command: `python -m unittest discover -s tests -v` (155 passed after current fixes). Syntax command: `python -m py_compile "DS Style Thumbnail Scraper.py" rom_matching.py thumbnail_output_paths.py thumbnail_image_data.py thumbnail_rendering.py ezflash_gba_thumbs.py` (passed).
- Primary compatibility reference: `https://github.com/voluptuary/ezfode-dssmm-kernel`, cloned at `/tmp/audit-voluptuary-ezfode`; head at inspection `cff477969bc501548497e7be8dab9e3b445ba987`, README reports v8.2.0. Its README documents 120×80 title / 80×80 box, top-down 16-bit BMP, `DST1` marker, and mirrored lookup.
- Secondary comparison only: `https://github.com/FrankieT19/omega-de-ds-style-kernel` / `omega-ds-style-kernel`; not the primary contract for this adapted version.
- Tests: `python -m unittest discover -s tests -v`; compile check as above. Kernel build and hardware behavior are not validated by this host-side DSSCC audit.

## F. Operational constraints

- Keep audit documentation commits separate from code-fix commits so audit artifacts can be excluded from a future upstream PR.
- Do not push to upstream; do not rewrite history, discard pre-existing changes, or make releases/deployments.
- Automated tests must use local fixtures/mocks, not live third-party services. Do not download ROMs or copyrighted game files.
- Never record secrets. Keep findings evidence-based and distinguish verified facts from hypotheses/unverified claims.

## G. Recovery procedure

Read `audit/AUDIT_HANDOFF.md` and `audit/AUDIT_PROGRESS.md` fully; inspect Git branch/status/remotes/log; reconcile this handoff against repository reality and add corrections rather than erasing history; locate the next unfinished action in section D and the latest progress entry; update both audit documents before substantial work and at each milestone; resume with the exact listed files/commands.

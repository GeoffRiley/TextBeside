# Contributing to TextBeside

Thanks for helping make transcription beside an image simpler. The project is small and at prototype stage. A focused change that can be tried on real files is more useful than a large framework added in anticipation.

## Before starting

1. Read the [README](README.md) and [roadmap](ROADMAP.md). Check the [open issues](https://github.com/GeoffRiley/TextBeside/issues) for the current checkpoint.
2. For a small fix, open a pull request and explain the problem. For a new feature, file an issue first with a user scenario and acceptance checks; discuss scope before doing extensive work.
3. Work on a short-lived branch from current `main`. Keep one pull request to one coherent change. Include the issue number in the PR description.
4. If the work changes file formats, save behavior, pairing rules, dependencies, or the licence, write down the decision and migration or compatibility impact in the PR.

## What a pull request should include

- A short description of what changes for a user, why, and any relevant issue.
- How you tried it, including OS and input files for UI or filesystem behavior.
- Focused tests for parsing, pairing, ordering, and operations that might lose or overwrite text. Avoid tests that merely duplicate the code's implementation.
- A manual check for zoom, pan, keyboard navigation, or screen layout when those are touched. A screenshot is helpful when it explains a UI change.
- Documentation updates when behavior, shortcuts, or installation steps change.
- Disclosure of new dependencies, licences, and any data sent off the user's machine.

Keep reviewable units small. It is fine to open a draft PR early to show a design or ask for feedback. Maintainers review for the documented behavior and clear failure handling, not for a rigid line count or perfect prose. A PR is ready to merge when its acceptance checks pass, relevant automated checks pass once available, and any material data-loss or compatibility concern has been addressed. A maintainer may ask to split a broad PR.

## Code conventions

- Follow the repository's Python and Qt choices in the README. Use clear type hints at file and data boundaries, and keep disk access separate from UI event handling where practical.
- Keep `.md` and `.txt` content as plain UTF-8 files. Do not silently move it into an application database or rewrite user files for cosmetic reasons.
- Treat saves, external edits, file switching, and errors as data-safety boundaries. Keep the user's unsaved text available after a failure and make conflicts visible.
- Use Ruff formatting and linting and pytest once configured in the repository. Until then, give exact commands or steps you used; do not claim checks ran if the tooling does not yet exist.
- Prefer meaningful examples and fixtures that exercise observable behavior. Keep tests deterministic and local; do not require internet access or modify the committed sample transcriptions.
- Make controls keyboard reachable and name UI actions clearly. Test Linux and Windows behavior when a change depends on path case, shortcuts, or packaging.

## Files, rights, and contributions

The repository is [MIT licensed](LICENSE). By submitting a contribution, you confirm you have the right to submit it under MIT and agree that it may be distributed under those terms. You retain your copyright. MIT permits commercial redistribution and sublicensing with notices preserved; it does not make a contributor's work exclusive to TextBeside. No separate contributor agreement is currently required. If a future plan requires rights beyond MIT, that will need an explicit conversation before such contributions are used that way.

Do not commit private documents, living people's records, credentials, or real scans without confirmed permission for redistribution. Prefer synthetic or clearly licensed sample material and record its source, licence, and any required attribution. Check dependencies' licences before proposing one, especially for a future packaged edition.

## Reporting problems

Describe what you expected, what happened, your OS, the image/text types and sizes, and the steps that reproduce it. For data-loss concerns, say whether the original text is still available, but redact private document content. For UI usability, note your input device and zoom/scale settings when relevant.

## Checkpoint reviews

The [checkpoint issues](https://github.com/GeoffRiley/TextBeside/issues?q=is%3Aissue+is%3Aopen+Checkpoint) contain exit checks. Link evidence there: relevant PRs, test results, and a short hands-on transcription note. Close a checkpoint only when its criteria are met, or record explicitly why a criterion changed. Revisit the schedule at each checkpoint; dates are estimates, not a reason to ship an unsafe save path.

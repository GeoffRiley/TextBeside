# TextBeside

**Your source. Your transcription. Side by side.**

TextBeside is an open-source, cross-platform desktop application for transcribing images into ordinary text or Markdown files.

It is intended for anyone who works from photographed or scanned material: genealogists, local historians, archivists, manuscript researchers, indexers, and others. The source image and transcription remain normal files in the user's chosen directory—there is no mandatory database, cloud account, import process, or proprietary project format.

## Licence and future editions

TextBeside is released under the [MIT licence](LICENSE). The current open-source code may be used, modified, redistributed, and sold, provided its copyright and licence notices are retained. This leaves room for a paid packaged edition, support, or additional future features. A separately licensed future edition is also possible for code whose rights permit it; PySide6/Qt and any other dependencies have their own distribution obligations.

A release already made under MIT remains available under MIT. A later fee cannot revoke those rights or make a previously published version trial-only. If the goal becomes mandatory payment after an evaluation period for *the same published code*, that is a different licensing model and should be decided before that code is released.

Contributions are accepted under MIT with their copyright retained by their authors; future distributions must preserve the required notices. A separate contributor agreement is not currently required. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Sample transcription files

The [examples/field-notes](examples/field-notes/) folder contains two paired sample pages with ordinary `.md` transcriptions. The source pages are synthetic and fictitious, with no third-party archival material. They are intended for checking the split view, basename pairing, navigation, and plain-file editing.

## The problem

General-purpose editors can open a text file beside a separate image viewer, but the two files are not treated as a single working unit. It is easy to lose one's place, edit the wrong transcription, or spend too much time arranging windows.

Specialist transcription tools offer an integrated interface, but often store transcriptions in a database, require uploads, or introduce subscription and workflow overhead.

TextBeside will occupy the useful space between them:

- a capable text editor on the left;
- a smooth, zoomable and pannable image viewer on the right;
- paired-file navigation that keeps the source and transcription together;
- local, portable files that remain fully under the user's control.

## Guiding principles

1. **Files remain sovereign.** A transcription is always an ordinary .md or .txt file.
2. **Local first.** Core transcription work must not require an account or internet connection.
3. **The pair is the unit of work.** Navigation changes the image and its matching transcription together.
4. **Image handling matters.** Zooming and panning should feel direct, predictable, and effortless.
5. **Start small.** TextBeside 0.1 is a focused transcription workbench, not a document-management or OCR suite.
6. **Linux and Windows are first-class platforms.** macOS support is desirable, subject to testing and packaging resources.
7. **Plain files stay useful elsewhere.** TextBeside-specific enhancements must not make the transcription unreadable in another editor.

## Technology

The prototype uses:

- **Python 3.11 or later**
- **PySide6 / Qt 6** for the desktop interface
- **pytest** for automated tests
- **Ruff** for linting and formatting

Distributable builds are still planned; **PyInstaller** or a comparable tool will be evaluated during packaging.

Qt provides native split panes, text editing, file watching, keyboard shortcuts, settings, and graphics-view support without requiring an embedded browser runtime.


### Development setup

TextBeside currently supports **Python 3.11 or later**.

On Linux, from a fresh checkout:

~~~bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
~~~

If `python -m pip install --upgrade pip` reports that pip is unavailable in the new environment, bootstrap it first with:

~~~bash
python -m ensurepip --upgrade
python -m pip install --upgrade pip
~~~

On Windows, ensure that Python 3.11 or later is installed and create the virtual environment with that interpreter explicitly if the default `python` command is older:

~~~powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
~~~

A newer installed interpreter can be selected instead, for example `py -3.14 -m venv .venv`.

Launch the prototype with:

~~~bash
textbeside
~~~

or, equivalently:

~~~bash
python -m textbeside.app
~~~

Run the current automated checks with:

~~~bash
pytest
ruff check .
ruff format --check .
~~~

## Current prototype: usage and status

Checkpoint 1's split-view, image controls and safe text saving are implemented on `main`. Checkpoint 2A adds nonrecursive image discovery and natural filename ordering; Checkpoint 2B adds explicit missing/matched/conflicting counterpart results. Previous/next navigation now connects these helpers to the interface. A folder browser, dedicated rescan command and page list remain outstanding.

Checkpoint 2C's **File → New transcription from image…** workflow is implemented on `main`, merged in [PR #19](https://github.com/GeoffRiley/TextBeside/pull/19). Manual filename-mismatch warnings and safer pair opening are also on `main`, merged in [PR #21](https://github.com/GeoffRiley/TextBeside/pull/21) for [#20](https://github.com/GeoffRiley/TextBeside/issues/20). The workflows were manually tested on Windows and Linux. Checkpoint 2D adds previous/next navigation under [#16](https://github.com/GeoffRiley/TextBeside/issues/16); Windows/Linux manual testing passed, and code review is pending.

### Open and edit an existing pair

1. Choose **File → Open pair…** (**Ctrl+O** on Linux/Windows).
2. Select the source image, then an existing UTF-8 `.md` or `.txt` transcription. This is a manual choice; the dialog does not automatically select a counterpart. If the filename stems differ, confirm **Open anyway** or choose **Cancel** (the default). Stems are compared exactly and case-sensitively on every platform, ignoring extensions and parent directories. Intentional mismatches remain supported, and Save uses the text file you selected.
3. Edit the text on the left and drag the splitter to resize the panes.
4. Choose **File → Save** or **Ctrl+S**. The text header shows **Saved** or **Modified**.

Cancelling either file picker or the mismatch warning retains the current pair and unsaved edits without writing files. The selected files are loaded before the **Save / Discard / Cancel** prompt for existing edits; a loading error retains the current work. Escape or closing the mismatch warning also cancels. See the [Linux/Windows walkthrough](docs/manual-pair-warning-walkthrough.md).

Markdown is edited as source text. For a quick trial, open either image and its matching `.md` file from [examples/field-notes](examples/field-notes/); use copies when testing saves.

### Start a new transcription from an image (Checkpoint 2C)

1. Choose **File → New transcription from image…** and select an image with no existing same-basename `.md` or `.txt` counterpart.
2. Type into the empty editor. Opening the image creates no transcription file; the header initially shows **Not saved**.
3. On the first **Save** (**Ctrl+S**), choose Markdown (`.md`) or plain text (`.txt`). TextBeside saves beside the image with the same basename: `page-001.jpg` becomes `page-001.md` or `page-001.txt`. There is no filename/location chooser or Save As command.
4. Later saves update that file normally.

If either counterpart already exists, the new-transcription command refuses to start; use **Open pair…** to select the existing file. If both exist, it does not choose between them. Before first save, counterparts are checked again, and creation cannot replace an existing target. The check and creation are separate operations: another process can still create the alternate extension in between, leaving both counterparts present. Cancelling the format choice, a newly detected counterpart, or a creation error leaves your text in the editor.

### Navigate paired pages (Checkpoint 2D)

Open an existing pair or start from an unpaired image, then use the **Previous page** / **Next page** toolbar buttons or **Navigate** menu. **Alt+Left** and **Alt+Right** provide the same actions. The status bar shows the current page position. Images in the active image's directory are ordered naturally; unavailable directions are disabled and navigation never wraps.

Each destination opens its same-basename transcription. A missing counterpart starts an empty in-memory transcription without creating a file; both `.md` and `.txt` prompt for an explicit choice, with Cancel as the default. Modified text prompts **Save / Discard / Cancel** before switching. Cancellation, failed saving or failed loading retains the current work. Intentional manual mismatches remain available; navigation uses the active image's directory and resolves each destination independently.

The active directory is watched for changes, refreshing page position and boundary controls when pages are added or removed. It is also rediscovered at each navigation; if the current image disappears, reopen a valid pair. Discovery, image decoding and transcription loading run in background workers, with a cancellable loading dialog for slow operations. Cancel keeps the current page; an operating-system read already in progress may finish in the background, but its cancelled result is ignored. Destination files and pairing are rechecked after dialogs before switching. See the [Windows/Linux navigation walkthrough](docs/page-navigation-walkthrough.md); Geoff confirmed all walkthrough tests passed on both platforms on 27 October 2026, with fast operation and predictable responses. Subsequent code-review changes add background-loading cancellation and live directory refresh; these additions still need a targeted Windows/Linux check.

### Image controls

| Action | Control |
| --- | --- |
| Zoom around the pointer | Mouse wheel |
| Pan | Hold the left mouse button and drag |
| Fit the whole image | **View → Fit image**, **Ctrl+0** |
| Show at 100% | **View → 100%**, **Ctrl+1** |

Newly opened images are fitted automatically. Fit mode follows pane resizing; manual zoom leaves fit mode. Manual zoom is bounded from 10% to 800%; **Fit image** may go outside those bounds to show the complete image. The image header displays the zoom percentage.

### Saving and current limitations

- Switching work or closing the window with modified text prompts **Save / Discard / Cancel**. Cancelling or a failed save retains the current work. An untouched empty new transcription has no edits and can be closed without a prompt or file creation.
- Saves encode the editor's plain text as UTF-8; Markdown is not rendered or reformatted. Loading through the text editor does not preserve the original byte representation of line endings.
- Existing-file saves use a temporary file in the same directory and atomic replacement. Transcription loading checks modification time and byte length before and after reading and rejects a detected change. External changes are also checked at save time using those values, with explicit overwrite confirmation. This is not continuous monitoring or a content comparison: changes retaining both values, or changes after the check, can be missed.
- First-save creation stages the text and publishes it without replacing an existing target using a hard link where supported. On filesystems without hard-link support it falls back to exclusive creation. If a fallback write fails, a partial counterpart may remain on disk; preserve the editor text and inspect/recover that file before retrying. Failed temporary-file cleanup can also leave a dot-prefixed `.tmp` file.
- Directory discovery currently filters by extension, ignores subdirectories and unrelated files, and sorts numbered names naturally (for example, `page-2` before `page-10`). It does not validate image contents. Image loading reports unreadable or unsupported images; no large-image performance guarantee is established.
- A dedicated folder-opening/rescan interface and a page list are not implemented; navigation starts from the current image and offers explicit counterpart-conflict choices. Fit width, rotation, per-image view restoration, find/replace, autosave/recovery and persistent window/recent-folder settings are also still planned.
- There are no packaged alpha builds yet. Linux and Windows are the primary targets; macOS testing and packaging remain future work. Unix permission-bit checks are skipped on Windows, whose permission model differs.

## Version 0.1 target scope

The following describes the intended release, not a list of features already available. See the current prototype instructions above for implemented behaviour.

### Essential workflow

The first usable release must allow a user to:

1. open a directory containing source images;
2. see the discovered images in a navigable list;
3. select an image and view it beside its corresponding transcription;
4. create the text counterpart when it does not yet exist;
5. edit and safely save .md or .txt files;
6. move to the previous or next pair without losing work.

### Image viewer

Version 0.1 should provide:

- smooth zoom centred on the pointer;
- click-and-drag panning;
- zoom in, zoom out, 100%, fit width, and fit image;
- 90-degree rotation;
- clear display of the current zoom level;
- restoration of the last view position for each image during the current session.

### Text editor

Version 0.1 should provide:

- direct editing of UTF-8 plain text and Markdown;
- undo and redo;
- find and replace;
- visible modified/saved status;
- configurable autosave, with conservative behaviour by default;
- protection against silently overwriting a file changed by another program;
- a choice of .md or .txt when creating counterparts.

Rendered Markdown preview and rich-text editing are explicitly outside the first release. Markdown remains source text.

### Pairing rules

The initial pairing rule is basename matching:

~~~text
page-001.jpg  <->  page-001.md
page-002.png  <->  page-002.txt
~~~

The prototype accepts these source-image extensions (case-insensitively):

~~~text
.jpg  .jpeg  .png  .webp  .tif  .tiff
~~~

The Checkpoint 2B resolver checks same-directory, same-basename paths with lowercase `.md` and `.txt` suffixes. No match means missing; one means matched; both mean conflict, with neither preferred. Multiple dots in a basename are retained. Files are inspected without being read or changed.

Path matching follows the filesystem's case rules: on a case-sensitive filesystem, `page.MD` is not the lowercase `page.md` candidate. There is no cross-platform case-normalisation policy yet. Natural image ordering is implemented in Checkpoint 2A, with deterministic ties. Previous/next navigation uses these results and prompts on conflicts; manual **Open pair…** still lets you select a transcription explicitly.

Manual **Open pair…** uses a separate, platform-consistent warning rule: exact case-sensitive filename stems, with extensions and directories ignored. A warning does not establish whether the text content matches the image.

PDF files and multi-page image containers are deferred until after 0.1. A multi-image manifest or control file associating several images with one transcription is also outside 0.1.

## Interface target

The current window has an editable text pane on the left, an image pane on the right, a draggable splitter, filename/state headers, File and View menus, and a basic status bar. The full 0.1 interface is planned to contain:

- a compact directory/pair navigator;
- an editable text pane;
- a draggable splitter;
- an image pane;
- a status bar showing filename, pair position, save state, and zoom;
- menus and keyboard shortcuts for file, edit, view, and navigation commands.

The default layout will put text on the left and the image on the right. Reversing the panes is a sensible later preference, but not required for the first prototype.

## Roadmap

For provisional dates, checkpoint evidence and the Gantt overview, see [ROADMAP.md](ROADMAP.md). The [checkpoint issues](https://github.com/GeoffRiley/TextBeside/issues) track live progress.

### Phase 0 — Define the project

- [x] Choose the name: TextBeside
- [x] Establish the product idea and core principles
- [x] Select Python and PySide6 for the prototype
- [x] Choose an open-source licence (MIT)
- [x] Document contribution and coding conventions
- [x] Turn the 0.1 scope into checkpoint issues and a provisional roadmap
- [x] Add a small, redistributable set of test images and matching text files

**Exit criterion:** the repository explains what TextBeside is, what 0.1 contains, and how development work will be organised.

### Phase 1 — Prove the central interaction

Implemented and reviewed in [Checkpoint 1 #2](https://github.com/GeoffRiley/TextBeside/issues/2):

- [x] a resizable text/image split view;
- [x] an editable text widget;
- [x] a graphics view with pointer-centred zoom and drag panning;
- [x] open/save actions;
- [x] a manually selected image/text pair.

**Exit criterion:** a real transcription can be comfortably edited beside its image, and the image controls feel good enough to justify continuing with the chosen toolkit.

This is the most important early checkpoint. If zooming or panning feels awkward, improve or replace the viewer implementation before building project machinery around it.

### Phase 2 — Add paired-file workflow

- [ ] Open and rescan a directory
- [x] Discover supported images (2A backend; UI integration pending)
- [x] Resolve .md/.txt counterparts as missing, matched or conflicting (2B backend)
- [x] Create a missing counterpart safely (2C, merged in PR #19)
- [x] Warn before manually opening mismatched filename stems, preserving intentional mismatches and safe cancellation (#20, merged in PR #21)
- [x] Add previous/next pair navigation (2D; Windows/Linux manual testing passed)
- [x] Add natural filename ordering (2A backend)
- [x] Protect modified text with Save / Discard / Cancel during page navigation
- [x] Check external modification time and byte length before saving the active transcription
- [x] Expose pairing conflicts with an explicit choice in the navigation UI

**Exit criterion:** a directory of sequential scans can be transcribed from beginning to end without separately opening or matching files.

### Phase 3 — Make it a dependable daily tool

- [ ] Complete image controls: fit image and 100% exist; fit width and rotation remain
- [ ] Remember window layout and recent directories
- [ ] Remember per-image zoom and pan state
- [ ] Add find and replace
- [ ] Add configurable autosave
- [ ] Complete keyboard shortcuts (Open, Save, Fit image and 100% already exist)
- [ ] Handle missing, moved, corrupt, and read-only files gracefully
- [ ] Add accessibility labels and full keyboard navigation
- [x] Add unit tests for file discovery, pairing, sorting, and save-conflict behaviour

**Exit criterion:** common mistakes do not lose transcription work, and the application is pleasant for a sustained transcription session.

### Phase 4 — Package an alpha release

- [ ] Select packaging tools after a small proof-of-build
- [ ] Produce Linux and Windows builds
- [ ] Add automated linting and tests in GitHub Actions
- [ ] Add application metadata, icon, versioning, and release notes
- [ ] Test on Ubuntu 24.04/26.04 and a current Windows 11 installation
- [ ] Document installation, first use, shortcuts, and known limitations
- [ ] Invite a small group of transcription users to test realistic collections

**Exit criterion:** a non-developer can install TextBeside, open a folder, and complete useful transcription work.

### Phase 5 — Respond to evidence

Prioritise these only after feedback from real use:

- horizontal reading guide;
- temporary pointer magnifier;
- mirrored or linked image positions across similar pages;
- Markdown preview;
- image adjustments such as brightness, contrast, inversion, and grayscale;
- arbitrary rotation or deskew;
- lightweight links from transcription text to image positions or regions;
- session restoration;
- optional OCR assistance;
- PDF and multi-page document support;
- macOS packaging.

These are candidates, not commitments. Each should preserve the local-files-first design.

## Current development focus

The first vertical slice, Checkpoint 2A/2B's discovery and pairing helpers, Checkpoint 2C's new-transcription workflow, and #20's manual mismatch warning are on `main`. Windows and Linux manual testing has confirmed the new-transcription and manual-pair workflows. Checkpoint 2D implements [#16: previous/next paired-page navigation](https://github.com/GeoffRiley/TextBeside/issues/16), reusing discovery, counterpart resolution and save protection; Windows/Linux interactive validation has passed and code review remains before closing that slice. Directory selection and the overall paired-directory checkpoint remain incomplete.

## Acceptance criteria for 0.1

Version 0.1 is ready when:

- text is stored only in the paired .md or .txt file;
- opening a directory does not copy or import the user's source files;
- pairing is deterministic and conflicts are clearly reported;
- unsaved work cannot be silently discarded during normal operation;
- zoom, pan, fit, and pair navigation work with both mouse and keyboard;
- the application remains responsive with realistically large scanned images;
- Linux and Windows builds can complete the same core workflow;
- the limits of the release are documented honestly.

## Deliberately out of scope for 0.1

- user accounts or cloud synchronisation;
- an internal catalogue or transcription database;
- rich-text storage;
- genealogy-specific fields or workflows;
- collaborative simultaneous editing;
- automatic OCR or handwriting recognition;
- PDF editing;
- image annotation;
- plugin architecture.

## Decisions to record before the first public release

- application configuration and cache locations on each platform;
- autosave default and recovery-file policy;
- whether UI state is stored globally or in an optional sidecar file;
- minimum supported Python, Qt, Linux, and Windows versions;
- release numbering and support policy;
- privacy statement, particularly if any later optional online feature is introduced.

## Contributing

The project has a working split-view prototype and is developing the paired-directory workflow. Early contributions are most useful when they test the central assumptions:

- Is basename pairing sufficient for real collections?
- Which zoom and pan controls feel most natural?
- What must happen before changing files to make data loss practically impossible?
- Which keyboard actions matter during long transcription sessions?
- What sizes and formats occur in real scanned collections?

The [contribution guide](CONTRIBUTING.md) explains how to propose work, make a focused pull request, check changes, and handle sample material and licensing.

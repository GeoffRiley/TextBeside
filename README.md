# TextBeside

**Your source. Your transcription. Side by side.**

TextBeside is a free, cross-platform desktop application for transcribing images into ordinary text or Markdown files.

It is intended for anyone who works from photographed or scanned material: genealogists, local historians, archivists, manuscript researchers, indexers, and others. The source image and transcription remain normal files in the user's chosen directory—there is no mandatory database, cloud account, import process, or proprietary project format.

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

## Proposed technology

The initial implementation will use:

- **Python 3.11 or later**
- **PySide6 / Qt 6** for the desktop interface
- **pytest** for automated tests
- **Ruff** for linting and formatting
- **PyInstaller** or a comparable tool for distributable application builds, to be evaluated during the packaging phase

Qt provides native split panes, text editing, file watching, keyboard shortcuts, settings, and graphics-view support without requiring an embedded browser runtime.

## Version 0.1 scope

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

Supported source-image extensions should initially include:

~~~text
.jpg  .jpeg  .png  .webp  .tif  .tiff
~~~

Rules requiring an explicit decision during prototyping:

- behaviour when both matching .md and .txt files exist;
- case-sensitive matching on platforms with different filesystem behaviour;
- natural ordering of numbered filenames such as page-2 and page-10;
- handling unsupported, corrupt, or exceptionally large images.

PDF files and multi-page image containers are deferred until after 0.1.

## Proposed interface

The main window will contain:

- a compact directory/pair navigator;
- an editable text pane;
- a draggable splitter;
- an image pane;
- a status bar showing filename, pair position, save state, and zoom;
- menus and keyboard shortcuts for file, edit, view, and navigation commands.

The default layout will put text on the left and the image on the right. Reversing the panes is a sensible later preference, but not required for the first prototype.

## Roadmap

### Phase 0 — Define the project

- [x] Choose the name: TextBeside
- [x] Establish the product idea and core principles
- [x] Select Python and PySide6 for the prototype
- [ ] Choose an open-source licence
- [ ] Agree contribution and coding conventions
- [ ] Turn the 0.1 scope into GitHub issues and milestones
- [ ] Add a small, redistributable set of test images and matching text files

**Exit criterion:** the repository explains what TextBeside is, what 0.1 contains, and how development work will be organised.

### Phase 1 — Prove the central interaction

Build a minimal vertical slice containing:

- [ ] a resizable text/image split view;
- [ ] an editable text widget;
- [ ] a graphics view with pointer-centred zoom and drag panning;
- [ ] open/save actions;
- [ ] one hard-coded or manually selected image/text pair.

**Exit criterion:** a real transcription can be comfortably edited beside its image, and the image controls feel good enough to justify continuing with the chosen toolkit.

This is the most important early checkpoint. If zooming or panning feels awkward, improve or replace the viewer implementation before building project machinery around it.

### Phase 2 — Add paired-file workflow

- [ ] Open and rescan a directory
- [ ] Discover supported images
- [ ] Pair images with .md or .txt files
- [ ] Create a missing counterpart safely
- [ ] Add previous/next pair navigation
- [ ] Add natural filename ordering
- [ ] Prompt or save appropriately before changing pairs
- [ ] Detect external changes to the active transcription
- [ ] Report pairing conflicts without guessing

**Exit criterion:** a directory of sequential scans can be transcribed from beginning to end without separately opening or matching files.

### Phase 3 — Make it a dependable daily tool

- [ ] Add fit image, fit width, 100%, and rotation controls
- [ ] Remember window layout and recent directories
- [ ] Remember per-image zoom and pan state
- [ ] Add find and replace
- [ ] Add configurable autosave
- [ ] Define and implement keyboard shortcuts
- [ ] Handle missing, moved, corrupt, and read-only files gracefully
- [ ] Add accessibility labels and full keyboard navigation
- [ ] Add unit tests for file discovery, pairing, sorting, and save-conflict behaviour

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

## Suggested first development slice

The first code milestone should be deliberately narrow:

> Open one image and one text file in a split window, edit and save the text, and make image zooming and panning feel excellent.

Recommended implementation order:

1. create the Python package and a minimal QMainWindow;
2. add a QSplitter with QPlainTextEdit and a custom image-view widget;
3. implement image loading, pointer-centred wheel zoom, drag panning, and zoom reset;
4. implement UTF-8 text loading, modified-state tracking, and atomic saving;
5. add a manual “Open pair” action;
6. test the interaction with small, large, portrait, and landscape images;
7. review the feel of the prototype before designing the directory browser.

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

- open-source licence;
- application configuration and cache locations on each platform;
- autosave default and recovery-file policy;
- whether UI state is stored globally or in an optional sidecar file;
- minimum supported Python, Qt, Linux, and Windows versions;
- release numbering and support policy;
- privacy statement, particularly if any later optional online feature is introduced.

## Contributing

The project is at the planning and prototype stage. Early contributions are most useful when they test the central assumptions:

- Is basename pairing sufficient for real collections?
- Which zoom and pan controls feel most natural?
- What must happen before changing files to make data loss practically impossible?
- Which keyboard actions matter during long transcription sessions?
- What sizes and formats occur in real scanned collections?

A fuller contribution guide will be added once the initial package structure and development workflow exist.

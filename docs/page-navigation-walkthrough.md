# Checkpoint 2D: Windows and Linux walkthrough

Run on both platforms before merging #16. Use copies in a temporary directory;
leave the committed samples unchanged. Automated headless tests are separate from
this interactive validation.

1. Copy both field-notes sample pairs into a temporary directory. Open the first
   pair through File → Open pair. Check the Page 1 of 2 status, disabled Previous,
   and enabled Next toolbar button and Navigate menu entry.
2. Use Next, Previous, Alt+Right and Alt+Left. Image and text should move together,
   each image initially fitted. At either end the unavailable direction is disabled;
   there is no wrapping.
3. Create copies named page-1.jpg, page-2.jpg and page-10.jpg. Confirm numeric order.
   Remove page-2's transcription: navigating there shows an empty editable new
   transcription without creating a file. First Save offers .md/.txt beside the image.
4. Edit existing text, then navigate. Exercise Save, Discard and Cancel. Cancel keeps
   the image, text and edits. Save writes to the old transcription before navigation.
   Repeat for a new transcription, cancelling the first-save format dialog.
5. Add both page-2.md and page-2.txt with recognisable different contents. Navigation
   must ask which to open; exercise each choice, Cancel, Escape and closing the dialog.
   Cancellation retains the current page, including unsaved edits.
6. Change the old text externally before choosing Save during navigation. Refusing
   overwrite must retain the current work. Repeat using a read-only save destination;
   a failed save must not navigate or discard editor contents.
7. Try a corrupt image, invalid UTF-8 text, removed current image, and unavailable
   directory. Expect a useful error with current work intact. Remove the destination
   while the unsaved-changes prompt is open and choose Discard: loading must fail
   without clearing the current text. Reopen a valid pair to recover the controls.
8. Open a deliberate manual mismatch, accepting its warning. Navigation is anchored
   to that image's directory and each destination resolves its own counterpart;
   it must not carry the manually selected text file to the next image.

The directory is rediscovered for each navigation. Files removed before a click
are absent from the new sequence; a disappeared current image requires reopening.
A directory watcher refreshes page position and boundary controls when images are
added or removed. There is no dedicated folder browser, rescan command or page list.

## Review follow-up checks (Windows and Linux)

- While positioned at the last page, add a new higher-numbered image to the folder.
  Next should enable automatically; navigate to the new page without reopening.
- Remove an adjacent page and check that the position/buttons refresh.
- Exercise a slow or large image/directory: the loading dialog should remain
  responsive and Cancel must retain the current work. A pending operating-system
  read cannot be forcibly stopped; its late result must not switch pages.
- Repeat unsaved Discard/Cancel and conflict-choice checks after this change.

The initial walkthrough passed on both platforms on 27 October 2026. The added
background-loading and directory-watcher behavior was subsequently retested successfully on both platforms by Geoff.
Record OS, results and any failures in the PR. No multi-image manifest is involved.

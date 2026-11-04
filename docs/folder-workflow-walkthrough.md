# Phase 2 folder workflow: Windows and Linux walkthrough

Status: 104 automated tests pass. Geoff confirmed testing passed on Windows and Linux on 4 November 2026, with positive feedback on the docking panel. Review follow-ups below need targeted Windows/Linux retesting, code review and merge.
Use temporary copies of `examples/field-notes`, never edit committed samples.

1. Choose File → Open folder (Ctrl+Shift+O) and select the sample-copy folder.
   The first naturally ordered image and its transcription should open. The Pages
   panel lists both image filenames, highlights the active one and shows the folder.
2. Click the second page and use the list's arrow keys to return. Check that image,
   text, selection, page position and Previous/Next controls stay in agreement.
   Verify Navigate menu actions and Alt+Left/Alt+Right still work.
3. With unsaved text, select another list entry and open another folder. Exercise
   Save, Discard and Cancel. Cancel and failed Save retain both current work and
   the current list selection; Discard switches only after successful loading.
4. Rename temporary copies to page-1, page-2 and page-10. Confirm natural order.
   Include unrelated files and a subfolder; neither should appear as a source page.
5. Remove a transcription and select its image: an empty new transcription opens
   without creating a file. Choose .md or .txt on first Save. Add both counterparts
   to another image: choosing that page must prompt explicitly, with safe Cancel.
6. Choose Navigate → Rescan folder (F5), or its toolbar button, while editing.
   It should update the list without reloading or clearing the text. Add/remove an
   image and verify both the directory watcher and explicit Rescan update the list.
7. Remove the active image, then Rescan. Its text should remain in the editor;
   selection clears and Previous/Next disable. Select an available page to continue,
   with Save/Discard/Cancel protection for any edits.
8. Try an empty folder, an unavailable folder, corrupt image and invalid UTF-8 text.
   Opening must report the problem and preserve the active work/folder/list. An
   empty folder leaves the active folder unchanged. Cancel the folder picker too.
9. Exercise loading Cancel on a slow folder/image. The old page and selection must
   remain; late background results must never switch pages. Test a Rescan failure:
   it must retain the existing list and editor and show a useful error.
10. Hide and restore the Pages panel using View → Pages. Open folder should show it
    again after success. Recheck deliberate manual mismatches through Open pair:
    the warning remains, saves use the selected text file, and directory navigation
    remains anchored to the image.

Record platform and results in the PR. Phase 2 remains open until this walkthrough
and review pass. No manifest, import, conversion, recursion or file renaming is added.


## Review follow-up checks

- Open a folder containing many images. The list should stay responsive while
  scrolling and selecting; visible row details are requested on demand.
- Cancel a deliberately slow read and retry while that same read is still pending.
  The status bar should explain that the previous read is finishing. The app must
  not start additional workers; after completion, retry normally. Current text
  remains available for saving after the loading dialog is cancelled.
- Open a different folder, then cancel its follow-up refresh or make that scan fail.
  The panel should retain the new folder's already-discovered pages, not old rows.
  A manually opened pair whose new folder cannot be scanned should show the new
  folder label and an empty list rather than the old folder's selectable pages.
- Remove and recreate the working folder while its parent remains available.
  Automatic updates should reconnect and show its new pages. If watching cannot
  be established, confirm the Pages panel explains that F5/manual Rescan is usable.

The original Windows/Linux test evidence remains recorded above. These later
changes are covered by automated regressions but await targeted manual retesting.

# Manual pair warning: Linux and Windows walkthrough

Run on both platforms before merging issue #20. Automated checks run headlessly;
this checklist records the remaining interactive validation.

Filename stems are compared exactly and case-sensitively on every platform.
Extensions and parent directories are excluded. Thus `page.jpg` / `page.md`
match, while `Page.jpg` / `page.md` warn. This warning does not inspect whether
the transcription content matches the image.

Use copies of the sample pages in a temporary folder. Keep source examples intact.

- Open the first matching sample pair: no mismatch warning should appear.
- Edit its transcription without saving. Start Open pair and cancel each file
  picker in turn: image, text, paths and unsaved edits should remain unchanged.
- Select an image and a different-stem text file. Check that both filenames appear
  in the warning, Cancel is the default, and Cancel, Escape and closing the warning
  each preserve the current work without writing any file.
- Repeat and choose Open anyway. Exercise Save, Discard and Cancel in the unsaved
  changes prompt. Save should save the old transcription before opening the chosen
  pair; Discard should open the pair; Cancel should retain the old unsaved work.
- Confirm that saving an intentional mismatch writes to the text file explicitly
  selected, without renaming either file or substituting a same-stem counterpart.
- Select an unreadable image, invalid UTF-8 transcription, or a file removed after
  selection. The error should retain the current work without a discard prompt.
- Reopen the current text file after editing and choosing Save: the displayed text
  should include the saved edits.
- Confirm that case-only stem differences also warn, and that matching stems in
  different directories can still be opened.

Record OS, results and any failures in the PR. No multi-image manifest is involved.

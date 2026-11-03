# Repository instructions

## Git development safety

- Perform all new preference-optimization development on `feature/preference-optimization`, including implementation, tests, and related documentation.
- Before editing, check the current branch and working-tree status. Do not develop directly on `main`.
- The verified stable baseline is commit `1be4b75a61e23148f993e0690f71a2683d36faed`, marked by `stable/preference-optimization-baseline-20261103`.
- Do not merge, rebase, or cherry-pick feature work into `main`, or push changes to `main`, without the user's explicit confirmation.
- Preserve all existing uncommitted changes. Do not overwrite or discard unrelated work.
- Do not perform destructive Git operations such as `git reset --hard`, `git clean -fd`, force pushes, or deletion of existing branches/tags.

## File deletion safety

- Never perform bulk deletion of files or directories.
- Never use destructive recursive deletion commands, including `del /s`, `rd /s`, `rmdir /s`, `Remove-Item -Recurse`, or `rm -rf`.
- File deletion is allowed only for one explicitly specified file path at a time.
- If bulk deletion is needed, stop and ask the user to delete those files manually.

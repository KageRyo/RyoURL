# Repository migration and cleanup

## Canonical repository

`KageRyo/RyoURL` is the canonical repository. The related repositories were imported without squashing their commit graphs:

| Former repository | Current path | Source head imported |
| --- | --- | --- |
| `KageRyo/RyoURL` | `backend/` and the root project files | `d62ddae` |
| `KageRyo/RyoURL-frontend` | `frontend/` | `9e7be5c` |
| `KageRyo/RyoURL-schema` | `backend/schemas/` | `e2c8846` |
| `KageRyo/RyoURL-test` | `tests/` | `1fd1974` |

Each imported repository is connected as a history-preserving subtree merge. For example, `git log --all -- frontend` reaches the former frontend commits, while the original backend history remains reachable through the existing backend commits and renames.

## Files intentionally consolidated

The canonical repository now has one project-level license, ignore file, pytest configuration, Docker development environment, and documentation set. The following duplicated repository scaffolding was removed from the child paths:

- standalone child README files;
- duplicate MIT license files;
- duplicate `.gitignore` files;
- the schema Git submodules;
- the test-only devcontainer and Compose file;
- the backend-only pytest configuration.

The source code and its commit history remain available in the imported commits and in the former repositories.

## Remote archive checklist

The archive notice commits are prepared locally on a `docs/archive-notice` branch in each former repository. After those branches and this consolidation branch are pushed and merged:

1. Merge the archive notice branch into each former repository's default branch.
2. Archive `RyoURL-frontend`, `RyoURL-schema`, and `RyoURL-test` on GitHub.
3. Check portfolio links, bookmarks, issue references, and clone instructions.
4. Keep the archived repositories until all important links have been verified.

Do not delete the former repositories immediately. Archiving keeps the old URLs, source history, and historical contribution records available while the canonical layout becomes the single maintained source.

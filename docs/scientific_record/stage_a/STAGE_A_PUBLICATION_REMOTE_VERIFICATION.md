# DEMAND-DRIVEN STAGE A RECORD PUBLISHED — MAIN UNCHANGED

All five remote verifications passed.

## Remote ref

```
refs/heads/publication/demand-driven-stage-a
https://github.com/konrazem/ebu.git
```

Upstream set: local `publication/demand-driven-stage-a` → `origin/publication/demand-driven-stage-a`.

## Verification results

**1 — Remote SHA.** Queried from the server via `git ls-remote`:

```
2c4b71d15fe8cb46592d9f2ead8f5f4e62fe9e32  refs/heads/publication/demand-driven-stage-a
```

Exactly the authorized SHA. **MATCH**

**2 — Remote tree.** Fetched the published commit back and resolved its tree:

```
fetched commit  2c4b71d15fe8cb46592d9f2ead8f5f4e62fe9e32
fetched tree    5afe39788ecc6bff675b0820eef1669fb8b78ebf
```

**MATCH** — the server holds the exact tree that was verified locally.

**3 — Outgoing range from `origin/main`.** Exactly one commit:

```
2c4b71d Publish the audited demand-driven Stage A record
```

No ancestor was dragged in. The 79 unpublished commits on `gaussian/stage-a-environment` — books, Stage B, homeostasis, SD programme, Dynamic EBU theory — remain unpublished.

**4 — No unintended ref moved.** Full `ls-remote` snapshots before and after, diffed ref by ref:

- 127 refs → 128 refs
- exactly one line differs: the new `publication/demand-driven-stage-a`
- **zero** refs changed value, **zero** deleted
- `main` before `660d6e5a56cb096fe6d1e4d202f592155d982c79`, after `660d6e5a56cb096fe6d1e4d202f592155d982c79` — **unchanged**

**5 — Disposition.** Published; `main` untouched.

## Boundaries honoured

No amend, no rewrite, no force push. No file modified, no artifact regenerated, no Stage-A episode rerun, no Stage B. No merge to main. **No pull request** — the `pull/new/...` line in the push output is GitHub's automatic hint, not an action; I ran no PR command. No additional local branch or worktree content was published: `gaussian/stage-a-environment` remains unpublished, still at `6538f919` with its 10 unrelated untracked dynamic-theory files left alone.

Verification after the push was read-only throughout — `ls-remote`, `fetch`, `rev-parse`, `log`.

Stage B remains unauthorized and unfrozen.
---
name: knowforge-github-issues
description: GitHub Issues API for etobo-tech/knowforge (PAT file + curl). Trigger list/read/create/update issues.
license: Apache-2.0
metadata:
  author: etobo
  version: "3.2"
---

`etobo-tech/knowforge` · PAT: `~/.config/github-knowforge.pat` (one line, `chmod 600`, never commit)

```bash
TOKEN="$(< ~/.config/github-knowforge.pat)"
H=(-H "Authorization: Bearer $TOKEN" -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28")
B="https://api.github.com/repos/etobo-tech/knowforge"
curl -s "${H[@]}" "$B/issues?state=open"
curl -s "${H[@]}" "$B/issues/N"
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" -d '{"title":"t","body":"b"}' "$B/issues"
curl -s -X PATCH "${H[@]}" -H "Content-Type: application/json" -d '{"body":"b"}' "$B/issues/N"
```

`N` = issue number in `/issues/N`. Do not log the token.

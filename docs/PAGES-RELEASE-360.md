# IBERFIT · Pages Release 360

The public website is in `candidate/v628`. The authoritative Git branch is
`production/web-iberfit`; `main` is historical and must never deploy.

## Release requests

After product PR CI and merge, use a separate PR changing only
`.iberfit/pages-release.json`. This is an explicit release intent, not an
automatic publication when code changes.

Preview request:
```json
{
  "schema": 1,
  "mode": "preview",
  "source": "<40-character integrated Git SHA>",
  "version": "<VERSION>",
  "previous_id": "<current successful Cloudflare production deployment UUID>"
}
```

Production request after human approval of the resulting immutable preview:
```json
{
  "schema": 1,
  "mode": "production",
  "source": "<same integrated Git SHA>",
  "version": "<same VERSION>",
  "previous_id": "<same current production UUID>",
  "preview_id": "<successful preview deployment UUID from evidence>",
  "approval": "<reviewer and review reference>"
}
```

Both requests certify the exact integrated commit with full history, run browser
checks at 390/768/1440px, package the website, separate credential-free
certification from publishing, and validate the package SHA-256 manifest.
Preview must preserve production. Production must match the reviewed preview,
active production and rollback target, then pass the live route and asset checks.
On failure, rollback is attempted only if the active production belongs to the
attempted source; an unrelated deployment is never reverted.

## Administration (mandatory before calling this hardened)

- Protect `production/web-iberfit` with PR-only changes, no force pushes/deletion,
  and successful required checks. Test rule behavior before requiring reviews
  in a single-maintainer repository. Do not use the historical main branch.
- Configure GitHub environments `web-preview` and `web-production`, with
  deployment branch restricted to `production/web-iberfit`; require an
  authorized reviewer for production when feasible. Move the Pages-only token
  to environment secrets once these rules are tested, then remove the
  repository-level copy only after confirming both flows. No secret in a PR.
- Token is restricted to the IBERFIT Cloudflare account, Pages Edit; it cannot
  be restricted to an individual Pages project by this workflow alone.
- Keep prior certified ZIP and its manifest in an access-controlled archive.
  Cloudflare rollback targets have finite retention; do not rely on an old
  deployment ID indefinitely. Redeploy the exact archived certified source
  through a reviewed recovery request if the old deployment has expired.
- Do not manually upload ZIPs to Cloudflare except documented incident recovery.
- No app/Supabase changes are part of this pipeline.

## Incident checks

Check the workflow evidence, canonical deployment ID, public VERSION and site.
If the active release is unrelated, stop rather than rollback someone else's
release. If the API or rollback fails, restore via Cloudflare's verified prior
production deployment and verify public health. A failed run is not a release.

The test suite injects failure and concurrent-deployment scenarios without
network access. It is not a substitute for a real isolated Cloudflare rollback
exercise or environment/branch protection setup. The existing product browser
suite is not a complete accessibility or performance audit.

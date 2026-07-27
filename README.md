# ads.vas-reversal.ca

Static asset host for Vas-Reversal paid advertising creative.

Exists for one reason: the Meta Marketing API can only ingest an image from a
publicly accessible URL. It will not accept a local file, and Meta Business
Suite's Media Library is a separate store the Marketing API cannot read. Putting
creative here gives every image a stable public URL that Meta can fetch once and
copy into the ad account.

Deliberately **not** part of the practice site. `vas-reversal.ca` is a Worker
serving the Hugo build; keeping ad creative out of that repo means marketing
assets can never affect what patients see, and the two deploy independently.

## Deploying

Requires `wrangler` (ships with Node). From this folder:

```bash
npx wrangler deploy
```

First deploy creates the Worker, binds `ads.vas-reversal.ca` as a custom domain,
and writes the DNS record. Later deploys upload only files whose contents
changed, so re-running it is cheap and safe.

To check what would upload without publishing:

```bash
npx wrangler versions upload --dry-run
```

## Adding creative

1. Drop the file in `assets/<YYYY-MM>/`, matching the campaign month.
2. Name it for what it is, not what it depicts: `worth-exploring-4x5.jpg`,
   not `IMG_2049.jpg`. The filename shows up in URLs and in the Meta asset list.
3. `npx wrangler deploy`.
4. The file is then at `https://ads.vas-reversal.ca/<YYYY-MM>/<filename>`.

Filenames are treated as immutable: `_headers` sets a one-year `immutable`
cache on images. Never edit a published file in place, since Meta and the CDN
may both hold a stale copy. Publish a new filename instead.

## Sizing

Meta feed placements, 4:5 portrait: **1080 x 1350**, JPEG quality 88, progressive.
That lands around 120–140 KB, which is comfortably under Meta's limits while
staying sharp on a modern phone.

Other placements, if needed later:

| Placement | Ratio | Pixels |
|---|---|---|
| Feed portrait | 4:5 | 1080 x 1350 |
| Story / Reels | 9:16 | 1080 x 1920 |
| Square | 1:1 | 1080 x 1080 |

## Search and privacy

`robots.txt` disallows everything and `_headers` sends
`X-Robots-Tag: noindex, nofollow, noarchive` on every response. This host must
never rank in search or compete with the practice site. If that ever changes,
it should be a deliberate decision, not a side effect.

Nothing here is patient information. Do not put consent forms, correspondence,
or anything identifying a patient on this host: it is public and unauthenticated
by design.

## Current contents

```
assets/
  robots.txt
  _headers
  index.html
  2026-07/
    worth-exploring-4x5.jpg        1080x1350  Instagram feed, "Worth exploring" test
    local-anaesthetic-4x5.jpg      1080x1350  Instagram feed, "Awake, and part of the decision" test
```

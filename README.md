# 🐦 Honk Demonlist

A difficulty-ranked leaderboard for [Honk](https://reddit.com/r/honk) levels.

## Adding / Editing Levels

Edit `data/stats.json` directly. Each entry looks like this:

```json
{
  "title": "He's beginning to believe",
  "url": "https://www.reddit.com/r/honk/comments/1s8z5m9/hes_beginning_to_believe/",
  "attempts": 10027,
  "completions": 30,
  "fastest_time": "11.033",
  "first_completion": "Immediate-Impact2637"
}
```

| Field | Required | Description |
|---|---|---|
| `title` | ✅ | Display name |
| `url` | ✅ | Reddit post link |
| `attempts` | ✅ | Total attempts (from flappy-goose's comment) |
| `completions` | ✅ | Total completions |
| `fastest_time` | optional | e.g. `"11.033"` or `"1:23.456"` |
| `first_completion` | optional | Username of first completer |

Success rate is calculated automatically as `(completions / attempts) × 100`, shown to **5 significant figures**. Levels are sorted hardest-first (lowest rate = #1).

## GitHub Pages Setup

1. Push this repo to GitHub.
2. Go to **Settings → Pages → Source → main branch / root**.
3. Live at `https://YOUR_USERNAME.github.io/honk-demonlist/`.

## File Structure

```
honk-demonlist/
├── index.html       ← Leaderboard page
└── data/
    └── stats.json   ← Manually maintained level data
```

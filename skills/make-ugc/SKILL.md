---
name: make-ugc
description: Generate AI UGC (User Generated Content) marketing videos using MakeUGC API — create avatar-based video ads with custom scripts.
homepage: https://www.makeugc.ai
metadata: {"openclaw":{"emoji":"🎬","requires":{"bins":["python3"],"env":["MAKEUGC_API_KEY"]}}}
---

# make-ugc 🎬

Generate AI avatar marketing videos via the MakeUGC API.

## Prerequisites

- Python 3.10+
- `MAKEUGC_API_KEY` environment variable set (requires MakeUGC Enterprise plan)
- `requests` Python package (`pip install requests`)

## Usage

Use the helper script at `{baseDir}/scripts/generate.py` to create videos.

### Generate a video

```bash
python3 "{baseDir}/scripts/generate.py" \
  --script "这款蓝牙耳机音质太棒了，续航超长，戴着也很舒服！" \
  --name "蓝牙耳机广告"
```

### With a specific avatar

```bash
python3 "{baseDir}/scripts/generate.py" \
  --script "Your ad script here" \
  --avatar "avatar-id-here" \
  --name "My Video Ad"
```

### List available avatars

```bash
python3 "{baseDir}/scripts/generate.py" --list-avatars
```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--script` | Yes (unless `--list-avatars`) | — | The spoken script/dialogue for the video |
| `--avatar` | No | API default | Avatar ID to use |
| `--name` | No | `"UGC Video"` | Name for the generated video |
| `--list-avatars` | No | — | List all available avatars and exit |

## How It Works

1. Sends a POST request to MakeUGC `/api/v1/videos/generate` with the script and avatar
2. Polls GET `/api/v1/videos/{id}` every 5 seconds until the video is ready
3. Returns the video download URL when complete (timeout: 10 minutes)

## When to Use

- User asks to create a marketing/ad video
- User wants an AI avatar to deliver a script or pitch
- User needs UGC-style content for social media ads

## Notes

- Video generation typically takes 1-5 minutes depending on script length
- The API key must be from a MakeUGC Enterprise plan
- If the API key is not set, the script will exit with an error message

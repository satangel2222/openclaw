#!/usr/bin/env python3
"""MakeUGC video generation script.

Generates AI avatar marketing videos via the MakeUGC API.
Requires MAKEUGC_API_KEY environment variable.
"""

import argparse
import json
import os
import sys
import time

try:
    import requests
except ImportError:
    print("Error: 'requests' package is required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)

BASE_URL = "https://app.makeugc.ai/api/v1"


def get_api_key():
    key = os.environ.get("MAKEUGC_API_KEY", "").strip()
    if not key:
        print("Error: MAKEUGC_API_KEY environment variable is not set.", file=sys.stderr)
        print("You need a MakeUGC Enterprise plan to get an API key.", file=sys.stderr)
        print("Visit https://www.makeugc.ai/pricing or contact help@makeugc.ai", file=sys.stderr)
        sys.exit(1)
    return key


def headers(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def list_avatars(api_key):
    """List all available avatars."""
    resp = requests.get(f"{BASE_URL}/avatars", headers=headers(api_key), timeout=30)
    resp.raise_for_status()
    data = resp.json()
    avatars = data if isinstance(data, list) else data.get("data", data.get("avatars", []))
    if not avatars:
        print("No avatars found.")
        return
    print(f"Available avatars ({len(avatars)}):\n")
    for av in avatars:
        av_id = av.get("id", "?")
        av_name = av.get("name", "Unnamed")
        print(f"  {av_id}  —  {av_name}")


def generate_video(api_key, script, avatar=None, name="UGC Video"):
    """Submit a video generation request and poll until complete."""
    payload = {
        "script": script,
        "name": name,
    }
    if avatar:
        payload["avatar_id"] = avatar

    print(f"Submitting video generation request: \"{name}\"")
    resp = requests.post(
        f"{BASE_URL}/videos/generate",
        headers=headers(api_key),
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    result = resp.json()

    video_id = result.get("id") or result.get("data", {}).get("id")
    if not video_id:
        print(f"Unexpected response: {json.dumps(result, indent=2)}", file=sys.stderr)
        sys.exit(1)

    print(f"Video ID: {video_id}")
    print("Waiting for video to be generated...")

    poll_interval = 5  # seconds
    max_wait = 600  # 10 minutes
    elapsed = 0

    while elapsed < max_wait:
        time.sleep(poll_interval)
        elapsed += poll_interval

        status_resp = requests.get(
            f"{BASE_URL}/videos/{video_id}",
            headers=headers(api_key),
            timeout=30,
        )
        status_resp.raise_for_status()
        status_data = status_resp.json()

        status = (
            status_data.get("status")
            or status_data.get("data", {}).get("status")
            or "unknown"
        )

        if status in ("completed", "done", "ready"):
            url = (
                status_data.get("download_url")
                or status_data.get("url")
                or status_data.get("data", {}).get("download_url")
                or status_data.get("data", {}).get("url")
            )
            print(f"\nVideo ready!")
            if url:
                print(f"Download URL: {url}")
            else:
                print(f"Full response: {json.dumps(status_data, indent=2)}")
            return status_data

        if status in ("failed", "error"):
            error_msg = status_data.get("error") or status_data.get("message") or "Unknown error"
            print(f"\nVideo generation failed: {error_msg}", file=sys.stderr)
            sys.exit(1)

        mins = elapsed // 60
        secs = elapsed % 60
        print(f"  Status: {status} ({int(mins)}m {int(secs)}s elapsed)", end="\r")

    print(f"\nTimeout: video not ready after {max_wait // 60} minutes.", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI UGC marketing videos via MakeUGC API"
    )
    parser.add_argument("--script", type=str, help="The spoken script/dialogue for the video")
    parser.add_argument("--avatar", type=str, default=None, help="Avatar ID to use (optional)")
    parser.add_argument("--name", type=str, default="UGC Video", help="Name for the video (default: 'UGC Video')")
    parser.add_argument("--list-avatars", action="store_true", help="List available avatars and exit")

    args = parser.parse_args()
    api_key = get_api_key()

    if args.list_avatars:
        list_avatars(api_key)
        return

    if not args.script:
        parser.error("--script is required (unless using --list-avatars)")

    generate_video(api_key, args.script, avatar=args.avatar, name=args.name)


if __name__ == "__main__":
    main()

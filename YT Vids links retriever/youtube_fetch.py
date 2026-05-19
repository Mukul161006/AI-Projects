#!/usr/bin/env python3
"""
youtube_fetch.py

Fetch all public video URLs for a YouTube channel (via uploads playlist)
and/or for one or more playlist IDs. Export results to an Excel workbook
(one sheet per query).
"""

import os
import time
import argparse
import logging
from typing import List, Dict, Optional
from itertools import islice

import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Constants
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
MAX_RESULTS_PER_PAGE = 50
VIDEO_BATCH_SIZE = 50
DEFAULT_OUTPUT = "youtube_videos.xlsx"
MAX_RETRIES = 5
BACKOFF_BASE = 1.5

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("youtube_fetch")

def load_api_key_from_env(env_path: Optional[str] = None) -> str:
    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError("YOUTUBE_API_KEY not found in environment. Create a .env file with YOUTUBE_API_KEY=your_key")
    return api_key

def build_youtube_client(api_key: str):
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=api_key, cache_discovery=False)

def resolve_channel_id(youtube, channel_id: Optional[str], username: Optional[str]) -> Optional[str]:
    """
    If channel_id is provided, return it. If username is provided, resolve to channel ID.
    If neither provided, return None.
    """
    if channel_id:
        return channel_id
    if username:
        try:
            resp = youtube.channels().list(part="id", forUsername=username, maxResults=1).execute()
            items = resp.get("items", [])
            if items:
                return items[0]["id"]
            logger.warning("No channel found for username: %s", username)
        except HttpError as e:
            logger.error("Error resolving username to channel ID: %s", e)
    return None

def get_uploads_playlist_id(youtube, channel_id: str) -> Optional[str]:
    try:
        resp = youtube.channels().list(part="contentDetails", id=channel_id, maxResults=1).execute()
        items = resp.get("items", [])
        if not items:
            logger.error("Channel not found for id: %s", channel_id)
            return None
        uploads_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        return uploads_id
    except HttpError as e:
        logger.error("Error fetching channel contentDetails: %s", e)
        return None

def paginate_playlist_items(youtube, playlist_id: str):
    """
    Generator that yields playlist item dicts for a playlist_id.
    """
    next_page_token = None
    while True:
        try:
            resp = youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=playlist_id,
                maxResults=MAX_RESULTS_PER_PAGE,
                pageToken=next_page_token
            ).execute()
        except HttpError as e:
            logger.error("HTTP error while fetching playlist items: %s", e)
            raise
        for item in resp.get("items", []):
            yield item
        next_page_token = resp.get("nextPageToken")
        if not next_page_token:
            break

def chunked_iterable(iterable, size):
    it = iter(iterable)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            break
        yield chunk

def fetch_video_details(youtube, video_ids: List[str]) -> Dict[str, Dict]:
    """
    Fetch video details for up to 50 video IDs. Returns dict keyed by videoId.
    """
    out = {}
    if not video_ids:
        return out
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=",".join(video_ids),
                maxResults=VIDEO_BATCH_SIZE
            ).execute()
            for v in resp.get("items", []):
                vid = v["id"]
                out[vid] = v
            return out
        except HttpError as e:
            logger.warning("videos.list error (attempt %d/%d): %s", attempt, MAX_RETRIES, e)
            if attempt == MAX_RETRIES:
                raise
            sleep_time = BACKOFF_BASE ** attempt
            time.sleep(sleep_time)
    return out

def iso8601_duration_to_readable(duration: str) -> str:
    """
    Convert ISO 8601 duration (e.g., PT1H2M3S) to H:MM:SS or M:SS.
    """
    hours = minutes = seconds = 0
    if duration.startswith("P"):
        time_part = duration.split("T")[-1] if "T" in duration else ""
        num = ""
        for ch in time_part:
            if ch.isdigit():
                num += ch
            else:
                if ch == "H":
                    hours = int(num) if num else 0
                elif ch == "M":
                    minutes = int(num) if num else 0
                elif ch == "S":
                    seconds = int(num) if num else 0
                num = ""
    total_seconds = hours * 3600 + minutes * 60 + seconds
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    else:
        return f"{m}:{s:02d}"

def build_video_row(video_item: Dict, playlist_title: Optional[str] = None) -> Dict:
    """
    Build a flat dict for a video item enriched with metadata.
    """
    vid = video_item.get("id")
    snippet = video_item.get("snippet", {})
    content = video_item.get("contentDetails", {})
    stats = video_item.get("statistics", {})

    title = snippet.get("title")
    published_at = snippet.get("publishedAt")
    channel_title = snippet.get("channelTitle")
    duration_iso = content.get("duration", "")
    duration = iso8601_duration_to_readable(duration_iso) if duration_iso else ""
    view_count = stats.get("viewCount", "")
    like_count = stats.get("likeCount", "")
    comment_count = stats.get("commentCount", "")

    url = f"https://www.youtube.com/watch?v={vid}"

    return {
        "video_id": vid,
        "url": url,
        "title": title,
        "channel_title": channel_title,
        "published_at": published_at,
        "duration": duration,
        "views": view_count,
        "likes": like_count,
        "comments": comment_count,
        "playlist": playlist_title or ""
    }

def fetch_playlist_videos(youtube, playlist_id: str, playlist_label: Optional[str] = None) -> List[Dict]:
    """
    Fetch all videos for a playlist ID, enrich them, and return list of rows.
    """
    logger.info("Fetching playlist: %s", playlist_id)
    playlist_items = []
    for item in paginate_playlist_items(youtube, playlist_id):
        content = item.get("contentDetails", {})
        video_id = content.get("videoId")
        snippet = item.get("snippet", {})
        playlist_items.append({
            "video_id": video_id,
            "snippet": snippet
        })

    rows = []
    video_id_list = [it["video_id"] for it in playlist_items if it.get("video_id")]
    for chunk in chunked_iterable(video_id_list, VIDEO_BATCH_SIZE):
        details = fetch_video_details(youtube, chunk)
        for vid in chunk:
            vdata = details.get(vid)
            if not vdata:
                logger.debug("Skipping missing video details for id: %s", vid)
                continue
            row = build_video_row(vdata, playlist_label)
            rows.append(row)
    logger.info("Fetched %d videos from playlist %s", len(rows), playlist_id)
    return rows

def fetch_videos_via_search(youtube, channel_id: str, max_results: int = 500) -> List[Dict]:
    """
    Fallback method: fetch videos using search.list for a channelId.
    Returns list of enriched video rows.
    """
    logger.info("Using search.list fallback for channel: %s", channel_id)
    rows = []
    next_page_token = None
    fetched = 0

    while True:
        resp = youtube.search().list(
            part="id",
            channelId=channel_id,
            type="video",
            order="date",
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        video_ids = [
            item["id"]["videoId"]
            for item in resp.get("items", [])
            if item.get("id", {}).get("kind") == "youtube#video"
        ]
        if not video_ids:
            break

        details = fetch_video_details(youtube, video_ids)
        for vid in video_ids:
            vdata = details.get(vid)
            if vdata:
                row = build_video_row(vdata, playlist_title="search_fallback")
                rows.append(row)

        fetched += len(video_ids)
        logger.info("Fetched %d videos so far...", fetched)

        next_page_token = resp.get("nextPageToken")
        if not next_page_token or fetched >= max_results:
            break

    logger.info("Total fetched via search: %d", len(rows))
    return rows

def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube video links by channel or playlist and export to Excel")
    parser.add_argument("--channel_id", help="YouTube channel ID (starts with UC...)")
    parser.add_argument("--username", help="YouTube channel username (legacy)")
    parser.add_argument("--playlists", nargs="*", help="One or more playlist IDs separated by space")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output Excel filename")
    parser.add_argument("--env", default=".env", help="Path to .env file containing YOUTUBE_API_KEY")
    args = parser.parse_args()

    api_key = load_api_key_from_env(args.env)
    youtube = build_youtube_client(api_key)

    sheets = {}

    # Channel uploads or fallback
    resolved_channel_id = resolve_channel_id(youtube, args.channel_id, args.username)
    if resolved_channel_id:
        uploads_playlist = get_uploads_playlist_id(youtube, resolved_channel_id)
        if uploads_playlist:
            try:
                rows = fetch_playlist_videos(youtube, uploads_playlist, playlist_label="channel_uploads")
                sheets[f"channel_{resolved_channel_id}"] = rows
            except HttpError as e:
                logger.error("Failed to fetch uploads for channel %s: %s", resolved_channel_id, e)
        else:
            rows = fetch_videos_via_search(youtube, resolved_channel_id)
            if rows:
                sheets[f"channel_{resolved_channel_id}_search"] = rows

    # Playlists provided explicitly
    if args.playlists:
        for pid in args.playlists:
            try:
                rows = fetch_playlist_videos(youtube, pid, playlist_label=pid)
                sheets[f"playlist_{pid}"] = rows
            except HttpError as e:
                logger.error("Failed to fetch playlist %s: %s", pid, e)

    if not sheets:
        logger.error("No data fetched. Provide a valid channel_id/username or playlist IDs.")
        return

    # Write to Excel (context manager ensures proper close)
    with pd.ExcelWriter(args.output, engine="openpyxl") as writer:
        for sheet_name, rows in sheets.items():
            df = pd.DataFrame(rows)
            cols = ["video_id", "url", "title", "channel_title", "published_at", "duration", "views", "likes", "comments", "playlist"]
            df = df.reindex(columns=cols)
            safe_sheet = sheet_name[:31]
            df.to_excel(writer, sheet_name=safe_sheet, index=False)

        meta = {
            "query_time": [pd.Timestamp.now().isoformat()],
            "queries": [", ".join(sheets.keys())]
        }
        pd.DataFrame(meta).to_excel(writer, sheet_name="metadata", index=False)

    logger.info("Exported results to %s", args.output)

if __name__ == "__main__":
    main()

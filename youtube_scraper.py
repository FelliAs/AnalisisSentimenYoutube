import os
import csv
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
    

VIDEOS = [
    {"id": "Hz2F_S3Tl0Y", "title": "I Jumped From Space (World Record Supersonic Freefall)"},
]

CSV_FILE = "comments.csv"
CSV_FIELDS = ["video_id", "comment_id", "author_name", "comment_text", "like_count", "published_at", "reply_count"]
TARGET_COMMENTS = 60000


def load_existing_ids(filepath):
    ids = set()
    if not os.path.exists(filepath):
        return ids
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ids.add(row["comment_id"])
    return ids


def get_video_comments(video_id, api_key):
    youtube = build("youtube", "v3", developerKey=api_key)
    comments = []
    page_token = None

    while True:
        for attempt in range(3):
            try:
                request = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=100,
                    textFormat="plainText",
                    pageToken=page_token
                )
                response = request.execute()
                break
            except HttpError as e:
                if attempt < 2:
                    wait = 2 ** (attempt + 1)
                    print(f"  Error: {e.resp.status} - Retrying in {wait}s (attempt {attempt + 1}/3)")
                    time.sleep(wait)
                else:
                    print(f"  Failed after 3 attempts: {e.resp.status} - {e._get_reason()}")
                    return comments
            except Exception as e:
                if attempt < 2:
                    wait = 2 ** (attempt + 1)
                    print(f"  Unexpected error - Retrying in {wait}s (attempt {attempt + 1}/3)")
                    time.sleep(wait)
                else:
                    print(f"  Failed after 3 attempts: {str(e)}")
                    return comments

        for item in response.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "video_id": video_id,
                "comment_id": item["snippet"]["topLevelComment"]["id"],
                "author_name": snippet["authorDisplayName"],
                "comment_text": snippet["textDisplay"],
                "like_count": snippet["likeCount"],
                "published_at": snippet["publishedAt"],
                "reply_count": item["snippet"]["totalReplyCount"]
            })

        print(f"  Fetched {len(comments)} comments so far...")

        page_token = response.get("nextPageToken")
        if not page_token:
            break

        time.sleep(1)

    return comments


def save_comments(comments, existing_ids):
    file_exists = os.path.exists(CSV_FILE)
    new_comments = [c for c in comments if c["comment_id"] not in existing_ids]

    if not new_comments:
        return 0

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, quoting=csv.QUOTE_ALL)
        if not file_exists:
            writer.writeheader()
        writer.writerows(new_comments)

    for c in new_comments:
        existing_ids.add(c["comment_id"])

    return len(new_comments)


def main():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("Error: YOUTUBE_API_KEY environment variable is not set.")
        return

    existing_ids = load_existing_ids(CSV_FILE)
    total_collected = len(existing_ids)
    print(f"Existing comments in CSV: {total_collected}")
    print(f"Target: {TARGET_COMMENTS} comments\n")

    for i, video in enumerate(VIDEOS, 1):
        print(f"Processing video {i}/{len(VIDEOS)}: {video['title']}")

        if total_collected >= TARGET_COMMENTS:
            print(f"Target of {TARGET_COMMENTS} comments reached. Stopping.")
            break

        comments = get_video_comments(video["id"], api_key)
        if not comments:
            print(f"  No comments retrieved. Skipping.\n")
            continue

        added = save_comments(comments, existing_ids)
        total_collected += added
        print(f"  Added {added} new comments (total: {total_collected})\n")

    print(f"Done. Total comments collected: {total_collected}")


if __name__ == "__main__":
    main()

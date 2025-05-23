from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound
)


def fetch_transcript_raw(video_id: str) -> list[dict] | None:
    """
    Fetches the raw transcript for a given YouTube video ID.

    Args:
        video_id (str): The 11-character YouTube video ID.

    Returns:
        list[dict] | None: The raw transcript as a list of dictionaries,
        or None if not available.
    """
    try:
        return YouTubeTranscriptApi.get_transcript(video_id)
    except TranscriptsDisabled:
        print(f"Transcripts are disabled for video ID: {video_id}")
    except NoTranscriptFound:
        print(f"No transcript found for video ID: {video_id}")
    except Exception as e:
        print(f"An error occurred while fetching the transcript: {repr(e)}")
    return None


def fetch_transcript(video_id: str) -> str | None:
    """
    Fethces the transcript for a given YouTube video ID.

    Args:
        video_id (str): The 11-character YouTube video ID.

    Returns:
        str | None: The transcript as plain text, or None if not available.
    """
    chunks = fetch_transcript_raw(video_id)
    if not chunks:
        return None
    return " ".join([chunk["text"] for chunk in chunks])

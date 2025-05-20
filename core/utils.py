import re


def extract_youtube_video_id(input_str: str) -> str | None:
    """
    Extracts a YouTube video ID from a full URL or returns the input string if
    it is already a valid ID.

    Args:
        input_str (str): A Youtube URL or a Youtube video ID.

    Returns:
        str | None: The extracted video IF if found, otherwise None.
    """

    # Common YouTube video ID patterns
    patterns = [
        r"youtu\.be\/([a-zA-Z0-9_-]{11})",
        r"youtube\.com\/.*v=([a-zA-Z0-9_-]{11})",
        r"youtube\.com\/embed\/([a-zA-Z0-9_-]{11})"
    ]

    # Try to match the input string against the patterns
    # and extract the video ID
    for pattern in patterns:
        match = re.search(pattern, input_str)
        if match:
            return match.group(1)
    # If input is already a valid YouTube video ID, return it
    if re.match(r"^[a-zA-Z0-9_-]{11}$", input_str):
        return input_str
    return None

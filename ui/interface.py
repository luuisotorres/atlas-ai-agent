import streamlit as st
import os
import json
import shutil

from core.utils import extract_youtube_video_id
from processors.section_splitter import SectionSplitter
from processors.transcript_fetcher import fetch_transcript_raw


def run_interface():
    """
    Run the Streamlit interface for the Atlas AI YouTube Transcript Fetcher.
    """
    st.title("Atlas AI - YouTube Transcript Fetcher")

    user_input = st.text_input("Enter YouTube video URL or ID:")

    if st.button("Run"):
        video_id = extract_youtube_video_id(user_input)

        if not video_id:
            st.error("Invalid YouTube URL or ID.")
        else:
            chunks = fetch_transcript_raw(video_id)
            if not chunks:
                st.error("No transcript found or transcripts are disabled.")
            else:
                splitter = SectionSplitter()
                sections = splitter.run(chunks)

                output_folder = "transcript_file"

                if os.path.exists(output_folder):
                    shutil.rmtree(output_folder)
                os.makedirs(output_folder, exist_ok=True)

                output_path = os.path.join(output_folder, 
                                           f"sections_{video_id}.json")
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(sections, f, ensure_ascii=False, indent=2)

                st.success(f"Transcript sections saved to {output_path}")

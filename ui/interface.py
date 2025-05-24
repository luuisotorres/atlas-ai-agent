import streamlit as st
import os
import json
import shutil

from core.utils import extract_youtube_video_id
from processors.section_splitter import SectionSplitter
from processors.transcript_fetcher import fetch_transcript_raw
from agents.summarizer_agent import summarize_sections_from_file
from agents.research_agent import extract_topics_from_json, enrich_topic
from agents.atlas_agent import (
    build_lesson,
    create_page,
    append_blocks
    )


def run_interface():
    """
    Run the Streamlit interface for the Atlas AI YouTube Transcript Fetcher.
    """
    st.markdown(
        "<h1 style='text-align: center; "
        "font-size: 3em; "
        "font-weight: bold; "
        "background-image: linear-gradient(to right, #FFD700, #FF8C00); "
        "-webkit-background-clip: text; "
        "-webkit-text-fill-color: transparent; "
        "font-family: Arial, sans-serif;'>"
        "🏛️ Atlas AI</h1>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("assets/atlas_image.png", width=600)

    st.markdown(
        """
        <div style='text-align: center; margin-top: -20px;'>
            <h3>Welcome, Explorer! 👋</h3>
            <p style='font-size: 18px; color: #CCCCCC;'>
                I am <strong>Atlas</strong>, your mythological AI guide.
                Drop in a YouTube link or video ID,
                and I will convert it into a beautifully structured Notion
                lesson page – like magic ✨
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form(key="input_form"):
        user_input = st.text_input("",
                                   placeholder="Enter YouTube video URL or ID")
        submitted = st.form_submit_button("Start")

    if submitted:
        video_id = extract_youtube_video_id(user_input)

        if video_id:
            video_id = video_id.strip()

        if not video_id:
            st.error("Invalid YouTube URL or ID.")
        else:
            with st.status("Extracting Transcript", expanded=True):
                st.write(
                    "📜 **Extracting ancient scrolls from YouTube archives...**"
                )
                chunks = fetch_transcript_raw(video_id)
                if not chunks:
                    st.error(
                        "No transcript found or transcripts are disabled."
                    )
                    return

            with st.status("Splitting Transcript", expanded=True):
                st.write("🪓 **Splitting scroll into readable runes...**")
                splitter = SectionSplitter()
                sections = splitter.run(chunks)

            with st.status("Summarization Ritual", expanded=True):
                st.write("🔥 **Preparing for Summarization Ritual...**")
                output_folder = "transcript_files"

                if os.path.exists(output_folder):
                    shutil.rmtree(output_folder)
                os.makedirs(output_folder, exist_ok=True)

                output_path = os.path.join(output_folder,
                                           f"sections_{video_id}.json")
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(sections, f, ensure_ascii=False, indent=2)

                st.write(
                    "✍🏻 **Summarizer Agent is transcribing each rune with "
                    "insight…**"
                )
                summarized_path = os.path.join(
                    output_folder, f"summarized_sections_{video_id}.json")
                summarized_sections = summarize_sections_from_file(output_path)
                with open(summarized_path, "w", encoding="utf-8") as f:
                    json.dump(summarized_sections, f, ensure_ascii=False,
                              indent=2)

            with st.status("Analyzing Topics",
                           expanded=True):
                st.write(
                    "🕵🏼‍♂️ **Research Agent is analyzing and "
                    "extracting key topics...**"
                )
                topics = extract_topics_from_json(summarized_path)
                st.write(
                    "🔍 Topics identified for research: "
                    f"{' | '.join(topics)}"
                )
                enrichment_data = {}

            with st.status("Enriching Topics", expanded=True):
                for topic in topics:
                    st.write(
                        f"📚 **Researching: {topic}...**"
                    )
                    enrichment_data[topic] = enrich_topic(topic)
                    with open(os.path.join(
                        output_folder, f"enrichment_data_{video_id}.json"
                    ), "w", encoding="utf-8") as enrichment_file:
                        json.dump(enrichment_data, enrichment_file,
                                  ensure_ascii=False, indent=2)

            with st.status("Crafting Notion Page", expanded=True):
                st.write(
                    "🏛️ **Atlas is crafting your Notion page...**"
                )
                blocks = []

                for section in summarized_sections:
                    summary = section.get("summary", "")
                    matched_topics = next(
                        (
                            key
                            for key in enrichment_data
                            if key.lower() in summary.lower()
                        ),
                        None
                    )
                    enrichment = enrichment_data.get(
                        matched_topics, ""
                    ) if matched_topics else ""
                    blocks.extend(build_lesson(summary, enrichment))

                page_id = create_page(f"YouTube Video ID – {video_id}")
                append_blocks(page_id, blocks)
                cleaned_page_id = page_id.replace('-', '')
                notion_link = f"https://www.notion.so/{cleaned_page_id}"

            st.success("🏛️ **Your Notion page is ready!** "
                       f"[Click here to view it]({notion_link})")

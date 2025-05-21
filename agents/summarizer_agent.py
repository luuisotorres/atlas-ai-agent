import os
import json
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
import re

# Load environment variables from .env file
load_dotenv()

# Initialize the summarizer agent
summarizer_agent = Agent(
    name="Summarizer",
    role="Summarize each transcript section",
    model=OpenAIChat(id="gpt-4o"),
    description=(
        """
        You are a concise, insightful assistant that summarizes video sections
        with clarity.
        """
    ),
    instructions=[
        (
            "Read the transcript chunk carefully and generate a clear, "
            "high-quality summary."
        ),
        (
            "Focus on extracting the key ideas, arguments, and topics "
            "discussed."
        ),
        (
            "Use concise language that could fit well in a Notion document."
        ),
        (
            "Avoid repeating the speaker's filler words or tangents. "
            "Focus on substance."
        ),
        (
            "If the section includes numbers, stats, names, or sources, "
            "preserve them."
        ),
        (
            "Do not use terms like 'This section covers…', "
            "'This section explains…', 'The speaker discusses…', "
            "'Let's dive into', or 'Here, the speaker unpacks…'"
        ),
        (
            "Format important terms in **bold**, and use *italics* for "
            "emphasis when needed."
        ),
        (
            "Ensure your summary can stand on its own: don't refer to the "
            "video, just the ideas."
        ),
        (
            "Use Markdown formatting. Prefer paragraphs over bullet points."
        ),
        (
            "Do not hallucinate or add commentary. Be faithful to the "
            "speaker's ideas."
        ),
        (
            "Make sure the output will be useful for a formatting agent, "
            "a research agent, and a Notion exporter downstream."
        ),
        (
            "If the transcript contains promotional content, advertisements, "
            "or sponsorship, ignore them completely and do not include "
            "them in the summary."

        ),
        (
            "Ensure consistency in your markdown structure, always following "
            "the format: "
            "1. A summary paragraph. "
            "2. A key points section (with bullets). "
            "3. Notable quotes (if relevant)."
        ),
        (
            "The text should be structured as follows: "
            "## Summary\n"
            "The summary paragraph of the section.\n\n"
            "## Key Points\n"
            "- Bullet 1\n"
            "- Bullet 2\n"
            "- Bullet 3\n\n"
            "## Notable Quotes\n"
            "- Quote 1\n"
        ),
    ],
    markdown=True
)


def summarize_sections_from_file(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        sections = json.load(f)

    summarized = []
    for section in sections:
        response = summarizer_agent.run(section["text"])
        section["summary"] = str(response.content)
        summarized.append(section)
    return summarized


if __name__ == "__main__":
    # Extract video_id dynamically from the filename pattern
    input_dir = "transcript_file"
    # Find the first file matching the pattern sections_*.json
    files = [f for f in os.listdir(input_dir) if re.match(
        r"sections_(.+)\.json", f
    )]
    if not files:
        raise FileNotFoundError(
            "No transcript section files found in transcript_file directory."
        )
    input_filename = files[0]
    match = re.match(r"sections_(.+)\.json", input_filename)
    video_id = match.group(1) if match else "example_video_id"

    input_path = os.path.join(input_dir, input_filename)
    result = summarize_sections_from_file(input_path)

    output_filename = f"summarized_sections_{video_id}.json"
    output_path = os.path.join(input_dir, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✅ Summarized file saved to {output_path}")

import os
import json
import re
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# Load environment variables from .env file
load_dotenv()


# Initialize the formatter agent
formatter_agent = Agent(
    name="Formatter",
    role=("Enhance and polish markdown summaries for readability and "
          "Notion export."),
    model=OpenAIChat(id="gpt-4o"),
    description=(
        """
        You are a formatting assistant that turns raw markdown into clea,
        well-structured, elegant content with headings, emojis, spacing,
        and readability.
        """
    ),
    instructions=[
        (
            "You will receive a markdown-formatted summary of a video section."
        ),
        (
            "Polish the formatting to make it visually clean and professional "
            "for display in Notion. Always start with a single '#' level "
            "heading that introduces the entire section (e.g., a title like "
            "'Overview of Memory Management' or 'What is a CPU?'). "
            "Avoid using '## Summary' or generic headings."
        ),
        (
            "Use consistent headings, spacing, and markdown elements. Fix any "
            "formatting inconsistencies or awkward phrasing."
        ),
        (
            "Enhance readability by adding spacing between sections, "
            "cleaning up bullets, and optionally adding relevant emojis."
        ),
        (
            "Do not use terms like 'This section covers…', "
            "'This section explains…', 'The speaker discusses…', "
            "'Let's dive into', or 'Here, the speaker unpacks…'"
        ),
        (
            "Suggest where callouts, dividers, or expandable toggles sections "
            "could be used, but do not use Notion block syntax."
        ),
        (
            "Where applicable, suggest that content could be placed inside "
            "a toggle or callout block using cues like 'Consider place the "
            "in a toggle block:'."
        ),
        (
            "Do not change the meaning of the content. "
            "Do not add new information."
        ),
        (
            "Ensure the final output is suitable for a "
            "Notion blog-style document."
        ),
        (
            "Ensure heading levels are consistent: use "
            "'#' for the main section title, '##' for major subsections, "
            "'###' for smaller parts. Never begin a section with '## Summary' "
        )
    ],
    markdown=True
)


def format_sections_from_file(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        sections = json.load(f)

    formatted = []
    for section in sections:
        summary = section.get("summary")
        if not summary:
            continue
        response = formatter_agent.run(summary)
        section["formatted_summary"] = str(response.content)
        formatted.append(section)
    return formatted


if __name__ == "__main__":
    input_dir = "transcript_file"
    files = [f for f in os.listdir(input_dir) if re.match(
        r"summarized_sections_(.+)\.json", f
    )]
    if not files:
        raise FileNotFoundError(
            "No summarized section files found in transcript_file directory."
            )

    input_filename = files[0]
    match = re.match(r"summarized_sections_(.+)\.json", input_filename)
    video_id = match.group(1) if match else "example_video_id"

    input_path = os.path.join(input_dir,
                              input_filename)
    result = format_sections_from_file(input_path)

    output_filename = f"formatted_sections_{video_id}.json"
    output_path = os.path.join(input_dir, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"✅ Formatted sections saved to {output_path}")

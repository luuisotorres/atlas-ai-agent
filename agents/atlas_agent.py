import random
import os
import json
import re
from notion_client import Client
from dotenv import load_dotenv
from typing import List, Dict, Tuple
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# Load environment variables from .env file
load_dotenv()

# Initialize Notion client
notion = Client(auth=os.getenv("NOTION_TOKEN"))


atlas_agent = Agent(
    name="Atlas",
    role=(
        "Tansform summaries and research into structured "
        "educational lessons."
    ),
    model=OpenAIChat(id="gpt-4o"),
    description=(
        "You are a brilliant educational agent with a passion for "
        "clear explanations. "
        "Your job is to take summarized content and external research "
        "on the same topic. "
        "and combine them into a single, engaging, well-structured "
        "textbook lesson. "
    ),
    instructions=[
        (
            "Combine the summarized content and the enrichhment "
            "into a cohesive lesson. "
        ),
        (
            "Structure it clearly using markdown headings, subheadings, "
            "bullet points, quotes, toggle lists, callout boxes, "
            "and paragraphs. "
        ),
        (
            "Avoid redundancy. Rephrase overlapping points and integrate "
            "definitions and examples from enrichment when helpful."
        ),
        (
            "Ensure it reads like a high-quality educational blog "
            "or chapter from a learning course."
        ),
        (
            "Always begin with a single main heading (#) as the lesson title"
        ),
        (
            "Then structure the lesson with logical sections (##) and "
            "smaller subsections (###) as approriate."
        ),
        (
            "Make the lesson visually appealing, using quotes "
            "and lists when helpful."
        ),
        (
            "Do NOT mention 'summary' or 'enrichment'. Merge them naturally "
            "into a fluid lesson"
        ),
        (
            "Use code blocks as examples when appropriate."
        ),
        (
            """Always put quotes and non-code examples in Notion's "
            "quotes blocks by adding a '" ' before the text."""
        ),
        (
            "Do not use any HTML tags under any circumstances."
            "Tags like <details> and <summary> are not allowed."
        ),
        (
            "When using URLs, always put them below a "
            "'### For Further Reading' section."
        ),
        (
            "Do not organize URLs like this: [text](url) or ![text](url). "
            "Never! "
            "Instead, paste the full URL."
        ),
    ],
    markdown=True
)


def parse_markdown_to_rich_text(line: str) -> List[Dict]:
    segments = []
    pattern = r'(\*\*.*?\*\*|\*.*?\*|[^*]+)'
    matches = re.findall(pattern, line)
    for match in matches:
        if match.startswith('**') and match.endswith('**'):
            segments.append({
                "type": "text",
                "text": {"content": match[2:-2]},
                "annotations": {"bold": True, "italic": False}
            })
        elif match.startswith('*') and match.endswith('*'):
            segments.append({
                "type": "text",
                "text": {"content": match[1:-1]},
                "annotations": {"bold": False, "italic": True}
            })
        else:
            segments.append({
                "type": "text",
                "text": {"content": match},
                "annotations": {"bold": False, "italic": False}
            })
    return segments


def load_json(file_prefix: str) -> Tuple[List[Dict], str]:
    input_dir = "transcript_files"
    files = [
        f for f in os.listdir(input_dir) if f.startswith(file_prefix)
    ]
    if not files:
        raise FileNotFoundError(f"No files found with prefix: {file_prefix}")
    with open(os.path.join(input_dir, files[0]), "r", encoding="utf-8") as f:
        return json.load(f), re.search(
            rf"{file_prefix}_(.+)\.json", files[0]
        ).group(1)


def build_blocks(section: Dict) -> List[Dict]:
    text = section.get("summary", "")
    lines = text.strip().split("\n")
    blocks = []

    within_code_block = False
    code_lines = []
    code_language = ""

    for line in lines:
        if line.strip().startswith("```") and not within_code_block:
            within_code_block = True
            code_language = line.strip().replace("```", "").strip().lower()
            valid_languages = {
                "abap", "agda", "arduino", "ascii art", "assembly", "bash",
                "basic", "bnf", "c", "c#", "c++", "clojure", "coffeescript",
                "coq", "css", "dart", "dhall", "diff", "docker", "ebnf",
                "elixir", "elm", "erlang", "f#", "flow", "fortran", "gherkin",
                "glsl", "go", "graphql", "groovy", "haskell", "hcl", "html",
                "idris", "java", "javascript", "json", "julia", "kotlin",
                "latex", "less", "lisp", "livescript", "llvm ir", "lua",
                "makefile", "markdown", "markup", "matlab", "mathematica",
                "mermaid", "nix", "notion formula", "objective-c", "ocaml",
                "pascal", "perl", "php", "plain text", "powershell", "prolog",
                "protobuf", "purescript", "python", "r", "racket", "reason",
                "ruby", "rust", "sass", "scala", "scheme", "scss", "shell",
                "smalltalk", "solidity", "sql", "swift", "toml", "typescript",
                "vb.net", "verilog", "vhdl", "visual basic", "webassembly",
                "xml", "yaml", "java/c/c++/c#", "notionscript"
            }
            if code_language not in valid_languages:
                code_language = "plain text"
            code_lines = []
        elif line.strip().startswith("```") and within_code_block:
            within_code_block = False
            blocks.append({
                "object": "block",
                "type": "code",
                "code": {
                    "rich_text": [{"type": "text", "text": {
                        "content": "\n".join(code_lines)
                    }}],
                    "language": code_language
                }
            })
            code_language = ""
            continue
        elif within_code_block:
            code_lines.append(line)
            continue

        elif line.startswith("# "):
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": parse_markdown_to_rich_text(line[2:].strip())
                }
            })
        elif line.startswith("## "):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": parse_markdown_to_rich_text(line[3:].strip())
                }
            })

        elif line.startswith("### "):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": parse_markdown_to_rich_text(line[3:].strip())
                }
            })

        elif line.startswith("#### "):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": parse_markdown_to_rich_text(line[5:].strip())
                }
            })
        elif line.startswith("•") or line.startswith("- "):
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": parse_markdown_to_rich_text(line.lstrip(
                        "•- "
                    ).strip())
                }
            })
        elif line.strip() == "---":
            blocks.append({
                "object": "block",
                "type": "divider", "divider": {}
            })
        elif line.startswith("> "):
            blocks.append({
                "object": "block",
                "type": "quote",
                "quote": {
                    "rich_text": parse_markdown_to_rich_text(line[2:].strip())
                }
            })
        elif line:
            chunks = [line[i:i+2000] for i in range(0, len(line), 2000)]
            for chunk in chunks:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": parse_markdown_to_rich_text(chunk.strip())
                    }
                })
    return blocks


def build_lesson(summary: str, enrichment: str) -> List[Dict]:
    lesson_input = (
        f"=== Summarized Content ===\n{summary.strip()}\n\n"
        f"=== Enrichment ===\n{enrichment.strip()}\n\n"
    )
    response = atlas_agent.run(lesson_input)
    return build_blocks({
        "summary": str(response.content)
    })


def create_page(title: str) -> str:
    education_icons = ["📚", "🧠", "🎓", "📖", "📝", "💡", "🧑‍🏫", "🔬", "📐", "🌐"]
    education_covers = [
        "https://images.unsplash.com/photo-1551385917-889e48f92c21",
        "https://images.unsplash.com/photo-1568667256549-094345857637",
        "https://images.unsplash.com/photo-1625053376622-e462848c453f",
        "https://images.unsplash.com/photo-1543191878-2baa4ff8a570",
        "https://images.unsplash.com/photo-1567910640027-4029c4d8e9e0",
        "https://images.unsplash.com/photo-1521917441209-e886f0404a7b",
        "https://images.unsplash.com/photo-1506619216599-9d16d0903dfd"
    ]

    selected_icon = random.choice(education_icons)
    selected_cover = random.choice(education_covers)

    page = notion.pages.create(
        parent={"page_id": os.getenv("NOTION_PARENT_PAGE_ID")},
        properties={
            "title": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": f"Atlas Summary: {title}"}
                    }
                ]
            }
        },
        icon={"type": "emoji", "emoji": selected_icon},
        cover={"type": "external", "external": {"url": selected_cover}},
    )
    return page["id"]


def append_blocks(page_id: str, blocks: List[Dict]):
    for i in range(0, len(blocks), 100):
        batch = blocks[i:i + 100]
        notion.blocks.children.append(block_id=page_id, children=batch)


if __name__ == "__main__":
    sections, video_id = load_json("summarized_sections")
    print(f"Loading: summarized_sections_{video_id}.json")

    blocks: List[Dict] = []

    enrichment_path = f"transcript_files/research_enrichment_{video_id}.json"
    with open(enrichment_path, "r", encoding="utf-8") as f:
        enrichment_data = json.load(f)
    print(f"\nLoading enrichment file: research_enrichment_{video_id}.json")
    print("\nAtlas is working on building a lesson…")

    for section in sections:
        summary = section.get("summary", "")
        topic_keys = enrichment_data.keys()
        matched_topics = next(
            (key for key in topic_keys if key.lower() in summary.lower()), None
        )
        enrichment = enrichment_data.get(
            matched_topics, ""
        ) if matched_topics else ""
        blocks.extend(build_lesson(summary, enrichment))

    print(f"\nTotal blocks: {len(blocks)}")
    print("\n Atlas is creating page in Notion...")
    page_id = create_page(title=f"YouTube Video ID – {video_id}")
    append_blocks(page_id, blocks)
    print(
        f"\n✅ Page created: https://www.notion.so/{page_id.replace('-', '')}"
    )

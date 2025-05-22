import random
import os
import json
import re
from notion_client import Client
from dotenv import load_dotenv
from typing import List, Dict, Tuple

# Load environment variables from .env file
load_dotenv()

# Initialize Notion client
notion = Client(auth=os.getenv("NOTION_TOKEN"))


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
    input_dir = "transcript_file"
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
    text = section.get("formatted_summary", "")
    lines = text.strip().split("\n")
    blocks = []

    for line in lines:
        if line.startswith("# "):
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
        elif line.startswith("- "):
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": parse_markdown_to_rich_text(line[2:].strip())
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
        elif line.startswith("•"):
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": parse_markdown_to_rich_text(line[1:].strip())
                }
            })
        elif line:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": parse_markdown_to_rich_text(line.strip())
                }
            })
    return blocks


def create_page(title: str, children: List[Dict]) -> Dict:
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

    return notion.pages.create(
        parent={
            "page_id": os.getenv("NOTION_PARENT_PAGE_ID")
        },
        properties={
            "title": {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": f"Atlas Summary: {title}"
                        }
                    }
                ]
            }
        },
        cover={
            "type": "external",
            "external": {
                "url": selected_cover
            }
        },
        icon={
            "type": "emoji",
            "emoji": selected_icon
        },
        children=children
    )


if __name__ == "__main__":
    sections, video_id = load_json("formatted_sections")
    print(f"Loading: formatted_section_{video_id}.json")

    blocks: List[Dict] = []
    for section in sections:
        blocks.extend(build_blocks(section))
    print(f"Total blocks: {len(blocks)}")
    print("Creating page in Notion...")
    created = create_page(
        title=f"YouTube Video {video_id}",
        children=blocks
    )
    print(f"\n Page created: {created['url']}")

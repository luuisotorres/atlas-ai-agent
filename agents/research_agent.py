import re
import os
import json
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools

# Load environment variables from .env file
load_dotenv()

research_agent = Agent(
    name="Research Agent",
    role=(
        "Perform contextual research based on summarized sections of content."
    ),
    model=OpenAIChat(id="gpt-4o"),
    description=(
        "You are a technical researcher. You take a topic and enrich it by "
        "researching the web using DuckDuckGo. You prefer reliable "
        "and educational sources."
    ),
    instructions=[
        (
            "You will be given a technical topic (e.g., 'SQL injection', "
            "'Binary Search Tree')."
        ),
        (
            "Search DuckDuckGo for recent and reliable information "
            "about the topic."
        ),
        (
            "Prioritize results from .edu, .org, or official "
            "documentation websites."
        ),
        (
            "Avoid unreliable sources, forums, and user-generated content "
            "unless it's from a credible authority."
        ),
        (
            "For each topic, return the following in markdown format:"
            "## 🔍 Enrichment: [Topic]"
            "**Definition:** Brief definition or summary of the topic."
            "**Example:** A real-world use case or application of the topic. "
            "Include code snippets if the topic is a programming concept "
            "such as loops, data structures, conditionals, etc."
            "**Further Reading:** A bulleted list of relevant sources with"
            "clickable links."
        ),
        (
            "Ensure all URLs are valid and properly formatted.",
            "Do not hallucinate URLs. Only include links that "
            "appear in search results."
        )
    ],
    tools=[DuckDuckGoTools()],
    show_tool_calls=True,
    markdown=True
)


def extract_topics_from_json(path: str, max_topics: int = 5) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        sections = json.load(f)

    candidates = set()
    for section in sections:
        text = section.get("formatted_summary", "")
        matches = re.findall(r'\*\*(.*?)\*\*', text)  # Look for bolded itens
        candidates.update(matches)

    topics = set()
    for c in candidates:
        cleaned = c.strip().strip(":;,.()[]{}").lower()
        if 2 < len(cleaned) < 50:
            topics.add(cleaned)

    return list(topics)[:max_topics]


def enrich_topic(topic: str) -> str:
    response = research_agent.run(f"Research and explain the topic: {topic}")
    return re.sub(r"(?s)^.*?##", "##", str(response.content))


if __name__ == "__main__":
    input_dir = "transcript_file"
    files = [f for f in os.listdir(input_dir) if f.startswith(
        "formatted_sections_"
    )]
    if not files:
        raise FileNotFoundError(
            "No formatted_sections JSON file found in transcript_file"
        )

    input_filename = files[0]  # Use the first one
    input_path = os.path.join(input_dir, input_filename)
    print(f"📄 Using input: {input_filename}")

    # Extract dynamic topics
    topics = extract_topics_from_json(input_path)
    print(f"\n🔍 Topics extracted:\n{topics}\n")

    # Run enrichment
    enriched_outputs = {}
    for topic in topics:
        print(f"🔎 Researching: {topic}")
        enriched_outputs[topic] = enrich_topic(topic)

    # Save results
    video_id = re.search(
        r"formatted_sections_(.+)\.json", input_filename
    ).group(1)
    output_path = os.path.join(
        input_dir, f"research_enrichment_{video_id}.json"
    )
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enriched_outputs, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Enrichment saved to {output_path}")

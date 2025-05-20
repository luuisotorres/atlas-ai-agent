class SectionSplitter:
    def run(self, transcript_chunks: list[dict]) -> list[dict]:
        """
        Groups raw transcripts chunks into logical sections.

        Args:
            transcript_chunks (list[dict]): List of dicts with keys 'text',
            'start', and 'end'.

        Returns:
            list[dict]: List of sections with keys 'text', 'start', and 'end'.
        """
        SECONDS_PER_SECTION = 300  # We will define 5 minutes per chunk
        sections = []
        current_section = []
        section_start = 0
        current_time = 0

        for chunk in transcript_chunks:
            current_time += chunk['duration']
            current_section.append(chunk["text"])

            if current_time - section_start >= SECONDS_PER_SECTION:
                sections.append({
                    "start": section_start,
                    "end": current_time,
                    "text": " ".join(current_section)
                })
                section_start = current_time
                current_section = []

        # Add any remaining chunks to the last section
        if current_section:
            sections.append({
                "start": section_start,
                "end": current_time,
                "text": " ".join(current_section)
            })
        return sections

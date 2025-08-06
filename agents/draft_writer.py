from .base_agent import BaseAgent
import json

class DraftWriterAgent(BaseAgent):
    # Writing the main draft is a critical task requiring the best model.
    model_name: str = "gemini-1.5-pro-latest"

    """
    PROFESSIONAL content writer that takes a strategic outline and generates a
    full-length, high-quality blog post, section by section.
    This corresponds to agent A8.
    """

    def run(self, state: dict) -> dict:
        """
        Generates a full article draft by executing the plan from the outline.

        Args:
            state: Shared state dictionary, must contain 'outline' and 'topic'.

        Returns:
            A dictionary containing the full article draft.
        """
        if not self.llm:
            return {'error': 'Gemini API key not configured'}

        outline = state.get('outline')
        topic = state.get('topic', 'the specified topic')
        tone = state.get('tone', 'professional') # Get tone from initial state

        if not outline or not isinstance(outline, list):
            return {'error': 'A valid outline from the OutlineGeneratorAgent is required.'}

        full_draft_sections = []
        
        system_prompt = f"""You are an expert blog and content writer specializing in SEO. Your writing style is engaging, clear, and authoritative. You write in a {tone} tone. Your task is to write a single, specific section of a blog post based on a detailed instruction set. Do NOT write the entire blog post. Only write the content for the section you are asked to write. Do not add any introductory or concluding phrases unless the instructions for the section explicitly ask for them."""

        # Iterate through each section of the outline and generate content
        for i, section in enumerate(outline):
            section_title = section.get('title', f'Section {i+1}')
            subsections = section.get('subsections', [])
            keywords = section.get('keywords_to_include', [])

            # Create a specific prompt for this section
            user_prompt = f"""
            Write the full content for the following section of a blog post about "{topic}".

            **Section Title:** {section_title}

            **Instructions & Key Points to Cover:**
            {json.dumps(subsections, indent=2)}

            **Keywords to Naturally Integrate:**
            {json.dumps(keywords, indent=2)}

            ---
            Write ONLY the content for this section. Start directly with the text. Do not repeat the title or instructions. The content should be detailed, comprehensive, and engaging.
            """

            # Generate the content for this section
            section_content = self.execute_prompt(system_prompt, user_prompt)
            
            full_draft_sections.append({
                "title": section_title,
                "content": section_content
            })
        
        # Assemble the final draft
        # A simple title for now, can be refined by a later agent
        draft_title = state.get('topic').title()
        full_text = f"# {draft_title}\n\n"
        full_text += "\n\n".join([f"## {s['title']}\n{s['content']}" for s in full_draft_sections])

        final_draft = {
            "title": draft_title,
            "sections": full_draft_sections,
            "full_text": full_text
        }

        state['draft'] = final_draft
        return state

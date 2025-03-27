import os
from anthropic import Anthropic
from django.conf import settings

class ClaudeHelper:
    def __init__(self):
        # Initialize the Anthropic client with the API key from settings
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-haiku-20240307"  # Updated to use current stable model

    def generate_flashcard_explanation(self, card_front, card_back):
        """
        Generate an explanation for a flashcard using Claude
        
        Args:
            card_front (str): The front content of the flashcard
            card_back (str): The back content of the flashcard
            
        Returns:
            str: Generated explanation or error message
        """
        try:
            # Create a system prompt that defines Claude's role and task
            system_prompt = """You are a knowledgeable tutor helping students understand concepts through flashcards. 
            Your explanations should be:
            - Clear and concise
            - Easy to understand
            - Focused on connecting the front and back of the card
            - Include relevant examples when helpful
            - Highlight key relationships between concepts"""

            # Create the user message with the flashcard content
            user_message = f"""Please explain this flashcard:
            Front: {card_front}
            Back: {card_back}
            
            Provide a clear explanation that helps understand the relationship between these concepts."""

            # Make the API call using Claude's messages API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )

            # Extract the explanation from Claude's response
            explanation = response.content[0].text.strip()
            
            # Format the explanation for better readability
            formatted_explanation = explanation.replace('\n\n', '\n').strip()
            
            return formatted_explanation

        except Exception as e:
            print(f"Error generating explanation: {str(e)}")
            return "Sorry, I couldn't generate an explanation at this time. Please try again later."

    def suggest_related_cards(self, content):
        """
        Generate suggestions for related flashcard content using Claude
        
        Args:
            content (str): The content to base suggestions on
            
        Returns:
            list: List of suggested related topics/concepts
        """
        try:
            system_prompt = """You are a knowledgeable tutor helping students create comprehensive flashcard sets.
            Suggest related concepts that would be valuable to study alongside the given content.
            Focus on:
            - Closely related topics
            - Prerequisites
            - Advanced concepts that build on this topic
            - Practical applications"""

            user_message = f"""Based on this flashcard content:
            {content}
            
            Suggest 3-5 related concepts that would be valuable to create flashcards for.
            Format each suggestion as a bullet point."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )

            # Extract and format suggestions
            suggestions = response.content[0].text.strip()
            # Convert bullet points to list items
            suggestion_list = [s.strip('- ').strip() for s in suggestions.split('\n') if s.strip()]
            
            return suggestion_list

        except Exception as e:
            print(f"Error generating suggestions: {str(e)}")
            return ["Unable to generate suggestions at this time."] 
        
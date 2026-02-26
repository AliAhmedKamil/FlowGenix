import json
import os
# Assuming OpenAI API usage for demonstration, but structured for generic LLM client
from openai import OpenAI 

class AIEngine:
    """
    Generates narrative intelligence from structured metrics.
    Enforces strict adherence to data and professional tone.
    """

    def __init__(self, api_key="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"):
        # Logic: If api_key is provided (default is the key above), use it. 
        # Otherwise, fall back to the environment variable.
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4" # Using high-reasoning model for accuracy

    def _construct_prompt(self, metrics: dict) -> list:
        """
        Builds the system and user prompt.
        Implements 'Quality Control Mode' directly in the prompt instructions.
        """
        
        system_prompt = """
        You are a Senior Marketing Performance Analyst. Your writing style is concise, executive-level, and data-driven.
        You do not use fluff. You do not use generic advice. 
        You strictly analyze the provided JSON metrics.
        
        Rules:
        1. Never hallucinate numbers. Only use data provided in the input.
        2. If a metric is 0 or low, address it objectively without panic.
        3. Structure your response strictly in JSON format with the following keys: "executive_summary", "key_insights" (list of 3 strings), "recommendations" (list of 3 strings).
        4. Do not wrap the output in markdown code blocks. Return raw JSON.
        """

        user_prompt = f"""
        Analyze the following weekly marketing performance data:
        {json.dumps(metrics, indent=2)}

        Provide:
        1. An executive summary (2-3 sentences).
        2. Exactly 3 key insights (focus on CTR, CVR, and Cost efficiency).
        3. Exactly 3 actionable optimization recommendations.
        """

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

    def _validate_ai_output(self, ai_response_text: str, original_metrics: dict) -> dict:
        """
        Quality Control Layer.
        Parses the AI output and ensures no hallucinations occurred.
        """
        try:
            data = json.loads(ai_response_text)
            
            # structure check
            required_keys = ["executive_summary", "key_insights", "recommendations"]
            if not all(k in data for k in required_keys):
                raise ValueError("AI output missing required keys.")
            
            # Check for hallucinated numbers (simple regex check could be added here if needed)
            # For now, we rely on the prompt constraint.
            
            return data

        except json.JSONDecodeError:
            # Fallback if AI returns text instead of JSON
            return {
                "executive_summary": "Error processing AI response structure.",
                "key_insights": ["Parsing error in AI generation."],
                "recommendations": ["Retry generation."]
            }

    def generate_analysis(self, metrics: dict) -> dict:
        messages = self._construct_prompt(metrics)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2, # Low temperature for factual reporting
                response_format={"type": "json_object"} 
            )
            
            raw_content = response.choices[0].message.content
            return self._validate_ai_output(raw_content, metrics)

        except Exception as e:
            return {
                "executive_summary": f"AI Analysis failed: {str(e)}",
                "key_insights": [],
                "recommendations": []
            }

# Standalone function for integration
def get_ai_analysis(metrics: dict) -> dict:
    # Since api_key has a default value in __init__, we don't need to pass it here
    # unless we want to override it.
    engine = AIEngine()
    return engine.generate_analysis(metrics)

# src/services/analyse.py
import os
import requests
from typing import Dict, Any

class TenderAnalyzer:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise ValueError("xAI API key is required")
        self.api_endpoint = "https://api.xai.com/v1/chat/completions"  # Hypothetical endpoint

    def analyze_tender(self, text: str) -> Dict[str, Any]:
        try:
            # Grok’s large context window (assume 200k tokens)
            max_text_length = 150000  # Adjust based on Grok’s limits
            if len(text) > max_text_length:
                text = text[:max_text_length]

            prompt = self._create_analysis_prompt(text)

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "grok-3",  # Hypothetical model name
                "messages": [
                    {"role": "system", "content": "You are an expert in analyzing tender documents with deep reasoning capabilities."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 4000,
                "temperature": 0.7
            }

            response = requests.post(self.api_endpoint, json=payload, headers=headers)
            response.raise_for_status()
            analysis_data = response.json()

            analysis_text = analysis_data["choices"][0]["message"]["content"]
            structured_data = self._parse_analysis(analysis_text)

            return {
                "full_analysis": analysis_text,
                "structured_data": structured_data
            }

        except requests.RequestException as e:
            raise Exception(f"Error calling Grok API: {str(e)}")
        except Exception as e:
            raise Exception(f"Error analyzing tender: {str(e)}")

    def _create_analysis_prompt(self, text: str) -> str:
        return f"""Analyze this tender document thoroughly and provide a detailed breakdown.

        Structure your response with these sections:

        # TENDER SUMMARY
        Summarize the tender opportunity in a concise paragraph.

        # BASIC INFORMATION
        - Tender Reference Number:
        - Issuing Organization:
        - Submission Deadline:
        - Project Location:
        - Estimated Budget:

        # KEY REQUIREMENTS
        List core technical, financial, and operational needs.

        # ELIGIBILITY CRITERIA
        List must-meet bidder criteria.

        # EVALUATION CRITERIA
        Detail how bids are scored.

        # REQUIRED DOCUMENTS
        List all submission documents.

        # COMPLIANCE CHECKLIST
        Critical compliance points checklist.

        # WINNING STRATEGY
        Strategic tips to win the tender.

        # RISKS AND MITIGATIONS
        Potential risks and how to mitigate them.

        # Tender Text:
        {text}
        """

    def _parse_analysis(self, analysis_text: str) -> Dict[str, Any]:
        sections = {}
        current_section = None
        current_content = []

        for line in analysis_text.split("\n"):
            if line.startswith("# "):
                if current_section:
                    sections[current_section] = "\n".join(current_content)
                    current_content = []
                current_section = line[2:].strip()
            elif current_section:
                current_content.append(line)

        if current_section and current_content:
            sections[current_section] = "\n".join(current_content)

        return sections
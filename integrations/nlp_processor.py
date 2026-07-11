"""
Enhanced NLP Processor for Cline-like Command Understanding
==========================================================

Provides robust NLP command parsing with:
- Intent confidence scoring
- Command disambiguation
- Structured response formats
- Better context extraction
"""

import re
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class Intent(Enum):
    """Supported intent types."""
    ANALYZE = "analyze"
    CODE = "code"
    TEST = "test"
    RESEARCH = "research"
    OLLAMA = "ollama"
    PROJECT = "project"
    UNKNOWN = "unknown"


@dataclass
class ParsedIntent:
    """Structured intent with confidence scores."""
    intent: Intent
    action: str
    confidence: float
    parameters: Dict[str, Any]
    context: Dict[str, Any]
    requires_confirmation: bool = False


class NLPProcessor:
    """Enhanced NLP command parser with confidence scoring."""

    def __init__(self):
        self.intent_patterns = {
            Intent.ANALYZE: [
                (r"\b(analyze|review|check|assess|audit|inspect)", 0.9),
                (r"\b(codebase|quality|issues|problems)", 0.8),
            ],
            Intent.CODE: [
                (r"\b(create|add|build|implement|write|generate)", 0.9),
                (r"\b(api|endpoint|function|component|module)", 0.7),
            ],
            Intent.TEST: [
                (r"\b(test|spec|unit|e2e|check|verify)", 0.9),
                (r"\b(run\s+test|fix\s+test)", 0.95),
            ],
        }

    def parse(self, command: str, project_context: Optional[str] = None) -> ParsedIntent:
        """Parse natural language command into structured intent."""
        command_lower = command.lower().strip()

        scores: Dict[Intent, float] = {}
        for intent, patterns in self.intent_patterns.items():
            score = 0.0
            for pattern, weight in patterns:
                matches = re.findall(pattern, command_lower)
                if matches:
                    score += weight * len(matches)
            scores[intent] = min(score, 1.0)

        best_intent = max(scores, key=scores.get) if scores else Intent.UNKNOWN
        confidence = scores.get(best_intent, 0.0)

        parameters = self._extract_parameters(command, best_intent, project_context)

        return ParsedIntent(
            intent=best_intent,
            action=self._intent_to_action(best_intent),
            confidence=confidence,
            parameters=parameters,
            context={"project_path": project_context} if project_context else {},
        )

    def _extract_parameters(self, command: str, intent: Intent, project_context: Optional[str]) -> Dict[str, Any]:
        """Extract relevant parameters from command."""
        params = {"raw": command}

        path_match = re.search(r"(/[\w/.-]+)", command)
        if path_match:
            params["target_path"] = path_match.group(1)

        return params

    def _intent_to_action(self, intent: Intent) -> str:
        """Convert intent to action name."""
        mapping = {
            Intent.ANALYZE: "review_code",
            Intent.CODE: "create_code",
            Intent.TEST: "run_test",
            Intent.UNKNOWN: "ask_agent",
        }
        return mapping.get(intent, "ask_agent")
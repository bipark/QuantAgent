"""
Shared utilities for agent output parsing.
"""

import json
import re


def parse_direction_confidence(text: str) -> dict:
    """
    Extract the last JSON block containing 'direction' and 'confidence' from LLM output text.
    Returns safe defaults if parsing fails.
    """
    if not text:
        return {"direction": "NEUTRAL", "confidence": 50}

    # Find all JSON-like blocks that contain "direction"
    matches = re.findall(r'\{[^{}]*"direction"[^{}]*\}', text)
    if matches:
        try:
            data = json.loads(matches[-1])
            direction = data.get("direction", "NEUTRAL").upper().strip()
            if direction not in ("LONG", "SHORT", "NEUTRAL"):
                direction = "NEUTRAL"
            confidence = max(0, min(100, int(data.get("confidence", 50))))
            return {"direction": direction, "confidence": confidence}
        except (json.JSONDecodeError, ValueError, TypeError):
            pass

    return {"direction": "NEUTRAL", "confidence": 50}

import json
import logfire

from typing import Literal

from pydantic import BaseModel, Field

from langchain_groq import ChatGroq

from app.config import settings
from app.classifier.prompts import CLASSIFIER_PROMPT


class IntentResult(BaseModel):
    intent: Literal[
        "TECHNICAL",
        "GREETING",
        "CAPABILITIES",
        "OFF_TOPIC",
        "JAILBREAK",
        "FAREWELL",
    ]

    confidence: float = Field(
        default=0.0,
        ge=0,
        le=1
    )


_classifier = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model="llama-3.1-8b-instant",
    temperature=0,
)


def classify(query: str) -> IntentResult:
    """
    Semantic intent classifier.

    Returns:

    IntentResult(
        intent="TECHNICAL",
        confidence=0.99
    )
    """

    with logfire.span("🧠 Intent Classification"):

        response = _classifier.invoke(
            [
                {
                    "role": "system",
                    "content": CLASSIFIER_PROMPT,
                },
                {
                    "role": "user",
                    "content": query,
                },
            ]
        )

        content = response.content.strip()

        try:

            result = IntentResult.model_validate_json(content)

            logfire.info(
                f"Intent={result.intent} "
                f"Confidence={result.confidence:.2f}"
            )

            return result

        except Exception:

            logfire.warning(
                f"Classifier parsing failed.\nOutput:\n{content}"
            )

            return IntentResult(
                intent="TECHNICAL",
                confidence=0.0,
            )
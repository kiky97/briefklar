from typing import Literal

from pydantic import BaseModel, Field

LETTER_TYPES = [
    "tax",
    "fine",
    "residence_permit",
    "health_insurance",
    "debt_collection",
    "social_services",
    "school",
    "housing",
    "employment",
    "other",
]
DATE_KINDS = ["deadline", "appointment", "effective", "other"]


class KeyDate(BaseModel):
    date: str  # ISO YYYY-MM-DD
    kind: Literal["deadline", "appointment", "effective", "other"] = "other"
    what: str = ""
    verified: bool = False  # True if the date literally appears in the letter text


class Amount(BaseModel):
    value: float
    currency: str = "CHF"
    what: str = ""
    verified: bool = False  # True if the number literally appears in the letter text


class Facts(BaseModel):
    sender: str | None = None
    letter_language: str = "unknown"
    letter_type: str = "other"
    summary_en: str = ""
    key_dates: list[KeyDate] = Field(default_factory=list)
    amounts: list[Amount] = Field(default_factory=list)
    reference_numbers: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
    urgency: Literal["low", "medium", "high"] = "medium"
    warnings: list[str] = Field(default_factory=list)


class AnalyzeRequest(BaseModel):
    letter: str = Field(min_length=20)
    language: str = "English"


class AnalyzeResponse(BaseModel):
    facts: Facts
    explanation: str


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class AskRequest(BaseModel):
    letter: str
    facts: Facts
    language: str = "English"
    question: str = Field(min_length=1)
    history: list[ChatTurn] = Field(default_factory=list)


class ReplyRequest(BaseModel):
    letter: str
    facts: Facts
    language: str = "English"
    intent: str = Field(min_length=1)


class TextResponse(BaseModel):
    text: str

#!/usr/bin/env python3
"""Vritti quality gate — Stop hook that catches substanceless responses
and feeds correction instructions back to Claude."""

import json
import re
import sys

HEDGING_PHRASES = [
    "it depends",
    "there are trade-offs",
    "there are tradeoffs",
    "consider your needs",
    "consider your specific",
    "your mileage may vary",
    "generally speaking",
    "in most cases",
    "there are several approaches",
    "there are many ways",
    "you might want to consider",
    "it really comes down to",
    "there's no one-size-fits-all",
    "each approach has its pros and cons",
    "the best approach depends",
    "the right choice depends",
    "without more context",
    "it varies depending",
    "there are many factors",
    "you could go either way",
]

SUBSTANCE_PATTERNS = [
    r"```",                          # code blocks
    r"[/\\][\w.-]+/[\w.-]+",        # file paths
    r":\d+",                         # line numbers
    r"\b\d+(\.\d+)+\b",             # version numbers
    r"`[a-zA-Z_][\w.]+`",           # inline code references
    r"https?://",                    # URLs
    r"\$ ",                          # shell commands
    r"\b(def|class|function|const|let|var|import|from)\b",  # code keywords
]


def extract_last_assistant_text(transcript_path):
    """Read transcript JSONL backward to find last assistant text."""
    last_assistant = None
    try:
        with open(transcript_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("type") == "assistant":
                    last_assistant = entry
    except (FileNotFoundError, PermissionError):
        return None

    if not last_assistant:
        return None

    content = last_assistant.get("message", {}).get("content", [])
    texts = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            texts.append(block["text"])
        elif isinstance(block, str):
            texts.append(block)
    return "\n".join(texts) if texts else None


def split_sentences(text):
    """Split text into rough sentence units."""
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`[^`]+`", "CODE", text)
    sentences = re.split(r"[.!?\n]+", text)
    return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]


def count_hedging(sentences):
    """Count sentences that contain hedging phrases."""
    count = 0
    for sentence in sentences:
        lower = sentence.lower()
        if any(phrase in lower for phrase in HEDGING_PHRASES):
            count += 1
    return count


def count_substance(text):
    """Count substance markers in the text."""
    count = 0
    for pattern in SUBSTANCE_PATTERNS:
        count += len(re.findall(pattern, text))
    return count


def build_correction(hedging_ratio, substance_count, sentences):
    """Build a specific correction instruction based on what was detected."""
    parts = []

    if hedging_ratio > 0.8:
        parts.append(
            "Your response is mostly hedging and vague qualifiers. "
            "Replace phrases like 'it depends' and 'consider your needs' "
            "with a direct answer and concrete recommendation."
        )

    if substance_count < 2 and len(sentences) > 3:
        parts.append(
            "Your response lacks concrete details. "
            "Include file paths, code, specific values, or references "
            "from this conversation."
        )

    hedging_only = hedging_ratio > 0.5 and substance_count < 2
    if hedging_only and not parts:
        parts.append(
            "Your response reads as generic advice that could apply to "
            "any project. Reference the user's specific situation, codebase, "
            "or prior conversation context."
        )

    return " ".join(parts)


def evaluate(text):
    """Evaluate response quality. Returns (allow: bool, correction: str)."""
    if not text or not text.strip():
        return True, ""

    words = text.split()

    # Short responses (status updates, acknowledgements) — allow
    if len(words) < 20:
        return True, ""

    sentences = split_sentences(text)
    if not sentences:
        return True, ""

    hedging_count = count_hedging(sentences)
    hedging_ratio = hedging_count / len(sentences) if sentences else 0
    substance_count = count_substance(text)

    # Block: high hedging AND low substance
    if hedging_ratio > 0.8 and substance_count < 2:
        correction = build_correction(hedging_ratio, substance_count, sentences)
        return False, correction

    # Block: moderate hedging with zero substance on a long response
    if hedging_ratio > 0.5 and substance_count == 0 and len(sentences) > 5:
        correction = build_correction(hedging_ratio, substance_count, sentences)
        return False, correction

    return True, ""


def main():
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    transcript_path = hook_input.get("transcript_path")
    if not transcript_path:
        sys.exit(0)

    text = extract_last_assistant_text(transcript_path)
    if text is None:
        sys.exit(0)

    allowed, correction = evaluate(text)

    if allowed:
        sys.exit(0)
    else:
        print(correction, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

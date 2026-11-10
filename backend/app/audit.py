import re
from difflib import SequenceMatcher
from typing import Any
from app.repositories import now


AMBIGUOUS = {"fast", "quickly", "user-friendly", "appropriate", "sufficient", "as needed", "etc", "normal", "reasonable", "easy"}


def evidence(chunk: dict[str, Any]) -> dict[str, Any]:
    return {key: chunk.get(key) for key in ("document_id", "filename", "chunk_id", "text", "page_number", "section", "score")}


def make_finding(project_id: str, issue_type: str, title: str, explanation: str, chunks: list[dict], confidence: float) -> dict:
    return {"project_id": project_id, "issue_type": issue_type, "title": title, "explanation": explanation, "confidence": confidence, "grounded": True, "review_status": "pending", "evidence": [evidence(c) for c in chunks], "created_at": now(), "reviewed_at": None, "review_comment": None}


def audit_chunks(project_id: str, chunks: list[dict[str, Any]]) -> list[dict]:
    findings: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for chunk in chunks:
        lower = chunk["text"].lower()
        words = sorted(term for term in AMBIGUOUS if term in lower)
        if words:
            findings.append(make_finding(project_id, "ambiguity", "Ambiguous wording needs clarification", f"Potentially subjective terms detected: {', '.join(words)}.", [chunk], 0.72))
        measurable = re.search(r"\b\d+(?:\.\d+)?\s*(ms|seconds?|minutes?|hours?|days?|%|mb|gb)\b", lower)
        if re.search(r"\b(shall|must|should)\b", lower) and not measurable and any(x in lower for x in ("performance", "response", "available", "secure", "scalable")):
            findings.append(make_finding(project_id, "missing_information", "Requirement may not be measurable", "This quality expectation has no obvious measurable acceptance threshold.", [chunk], 0.68))
    for index, left in enumerate(chunks[:120]):
        for right in chunks[index + 1:120]:
            if left["chunk_id"] == right["chunk_id"]: continue
            ratio = SequenceMatcher(None, left["text"].lower(), right["text"].lower()).ratio()
            pair = tuple(sorted((left["chunk_id"], right["chunk_id"])))
            if ratio >= 0.86 and pair not in seen:
                findings.append(make_finding(project_id, "duplicate", "Semantically similar requirements", "These passages are highly similar and may describe the same requirement.", [left, right], round(min(ratio, .98), 2)))
                seen.add(pair)
            left_time = re.search(r"(\d+)\s*(minutes?|hours?)", left["text"].lower())
            right_time = re.search(r"(\d+)\s*(minutes?|hours?)", right["text"].lower())
            shared = {"session", "timeout", "expire"} & set(re.findall(r"\w+", left["text"].lower())) & set(re.findall(r"\w+", right["text"].lower()))
            if left_time and right_time and left_time.group(0) != right_time.group(0) and shared and pair not in seen:
                findings.append(make_finding(project_id, "contradiction", "Conflicting time constraints", f"Related passages specify different durations: {left_time.group(0)} and {right_time.group(0)}.", [left, right], .84))
                seen.add(pair)
    return findings[:50]


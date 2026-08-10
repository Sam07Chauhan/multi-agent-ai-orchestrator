import logging
import re

import config

logger = logging.getLogger("m4_nexus")

_CLIP_TOKENIZER = None
MAX_CLIP_TOKENS = 75

def _get_tokenizer():
    global _CLIP_TOKENIZER
    if _CLIP_TOKENIZER is None:
        from transformers import CLIPTokenizer
        try:
            _CLIP_TOKENIZER = CLIPTokenizer.from_pretrained(
                config.INPAINT_MODEL_PATH,
                subfolder="tokenizer",
                local_files_only=True,
            )
        except OSError:
            _CLIP_TOKENIZER = CLIPTokenizer.from_pretrained(
                config.INPAINT_MODEL_PATH,
                subfolder="tokenizer",
            )
    return _CLIP_TOKENIZER

def count_clip_tokens(text: str) -> int:
    return len(_get_tokenizer()(text, add_special_tokens=False).input_ids)

def _extract_clause(pattern: str, text: str):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None

def _build_compact_prompt(prompt: str) -> str:
    parts = []

    if re.search(r"\bstudio\b|\bportrait\b", prompt, re.IGNORECASE):
        parts.append("studio portrait photograph")

    if re.search(r"facial features|same face|same woman", prompt, re.IGNORECASE):
        parts.append("same woman same facial features")

    clothing = _extract_clause(
        r"wearing\s+(.+?)(?:\.|,\s*she\s+is\s+posed|,\s*holding|\s+against\b)",
        prompt,
    )
    if clothing:
        parts.append(clothing)
    else:
        clothing = _extract_clause(r"wearing\s+([^.;]+)", prompt)
        if clothing:
            parts.append(clothing)

    if re.search(r"maroon|curtain|backdrop", prompt, re.IGNORECASE):
        parts.append("solid dark maroon curtain backdrop")

    if re.search(r"\bbag\b", prompt, re.IGNORECASE):
        parts.append("holding small black leather shoulder bag")

    if re.search(r"lighting|high.?fashion", prompt, re.IGNORECASE):
        parts.append("crisp studio lighting, high fashion")

    return ", ".join(parts) if parts else prompt

def fit_clip_prompt(prompt: str, max_tokens: int = MAX_CLIP_TOKENS) -> str:
    prompt = re.sub(r"\s+", " ", prompt.strip())

    try:
        if count_clip_tokens(prompt) <= max_tokens:
            return prompt
    except Exception as exc:
        logger.warning("CLIP tokenizer unavailable (%s); using compact rewrite", exc)
        return _build_compact_prompt(prompt)

    compact = _build_compact_prompt(prompt)
    try:
        if compact and count_clip_tokens(compact) <= max_tokens:
            logger.info("Prompt rewritten for CLIP (%d tokens)", count_clip_tokens(compact))
            return compact
    except Exception:
        if len(compact.split()) <= 55:
            return compact

    sentences = re.split(r"(?<=[.!?])\s+", prompt)
    while len(sentences) > 1 and count_clip_tokens(" ".join(sentences)) > max_tokens:
        sentences.pop()

    trimmed = " ".join(sentences)
    if count_clip_tokens(trimmed) <= max_tokens:
        logger.info("Prompt trimmed to %d tokens", count_clip_tokens(trimmed))
        return trimmed

    tokenizer = _get_tokenizer()
    ids = tokenizer(compact or prompt, add_special_tokens=False).input_ids[:max_tokens]
    truncated = tokenizer.decode(ids, skip_special_tokens=True)
    logger.warning("Prompt hard-truncated to %d tokens", count_clip_tokens(truncated))
    return truncated
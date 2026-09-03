# engines/prompt_utils.py
import logging
import re
import config

logger = logging.getLogger("m4_nexus")

_CLIP_TOKENIZER = None
# Allow up to ~20 CLIP chunks (~1500 tokens / 1000+ words) to pass to Compel
MAX_CLIP_TOKENS = 1500

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
    try:
        return len(_get_tokenizer()(text, add_special_tokens=False).input_ids)
    except Exception:
        # Approximate fallback if tokenizer fails
        return int(len(text.split()) * 1.3)

def fit_clip_prompt(prompt: str, max_tokens: int = MAX_CLIP_TOKENS) -> str:
    """
    Cleans up whitespace and ensures prompt stays within max_tokens ceiling.
    Compel in InpaintEngine handles chunking and multi-tensor encoding seamlessly.
    """
    cleaned_prompt = re.sub(r"\s+", " ", prompt.strip())
    token_count = count_clip_tokens(cleaned_prompt)
    
    if token_count <= max_tokens:
        logger.info(f"Passing full prompt ({token_count} CLIP tokens) to Compel multi-chunk engine.")
        return cleaned_prompt

    # If an enormous prompt (>1500 tokens) is passed, safely truncate at sentence boundary
    logger.warning(f"Prompt ({token_count} tokens) exceeds safety limit of {max_tokens}. Trimming.")
    sentences = re.split(r"(?<=[.!?])\s+", cleaned_prompt)
    while len(sentences) > 1 and count_clip_tokens(" ".join(sentences)) > max_tokens:
        sentences.pop()
    
    trimmed = " ".join(sentences)
    if count_clip_tokens(trimmed) <= max_tokens:
        return trimmed

    # Hard-truncate only as last resort
    tokenizer = _get_tokenizer()
    ids = tokenizer(cleaned_prompt, add_special_tokens=False).input_ids[:max_tokens]
    return tokenizer.decode(ids, skip_special_tokens=True)
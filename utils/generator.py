import re

def generate_title_prompts(title):
    title = title.strip()
    if not title:
        return []

    prompts = [title]  # Always include full title

    # --- Step 1: Split by "|" ---
    pipe_parts = [p.strip() for p in title.split("|") if p.strip()]

    if len(pipe_parts) > 1:
        left_part = pipe_parts[0]
        right_part = pipe_parts[1]

        prompts.append(left_part)
        prompts.append(right_part)
    else:
        left_part = title

    # --- Step 2: Split by ":" ---
    colon_parts = [p.strip() for p in left_part.split(":") if p.strip()]

    if len(colon_parts) > 1:
        match_part = colon_parts[0]
        suffix_part = colon_parts[1]

        prompts.append(match_part)
        prompts.append(suffix_part)
    else:
        match_part = left_part

    # --- Step 3: Split match_part (A vs B OR A - B) ---
    separator_pattern = r"\s+(?:vs\.?|[-])\s+"
    match = re.search(separator_pattern, match_part, flags=re.IGNORECASE)

    if match:
        left = match_part[:match.start()].strip()
        right = match_part[match.end():].strip()

        if left:
            prompts.append(left)
        if right:
            prompts.append(right)

    # --- Remove duplicates (preserve order) ---
    seen = set()
    final_prompts = []
    for p in prompts:
        key = p.lower()
        if key not in seen:
            seen.add(key)
            final_prompts.append(p)

    return final_prompts
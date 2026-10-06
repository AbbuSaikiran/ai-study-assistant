"""Prompt Builder: turns the student's input into high-quality prompts for the AI."""

SYSTEM_PROMPT = (
    "You are an expert, engaging, and patient study mentor for students. "
    "Structure your responses clearly with clean Markdown headings, bullet points, and code/math blocks where appropriate. "
    "Keep explanations intuitive, concise, and easy to memorize."
)

MODES = (
    "Ask Question",
    "Summarize Notes",
    "Generate Quiz",
    "Create Flashcards",
    "Explain Like I'm 5",
)

MODE_ICONS = {
    "Ask Question": "💡",
    "Summarize Notes": "📝",
    "Generate Quiz": "🎯",
    "Create Flashcards": "🗂️",
    "Explain Like I'm 5": "🐣",
}

MODE_DESCRIPTIONS = {
    "Ask Question": "Get clear, step-by-step explanations with examples.",
    "Summarize Notes": "Extract key takeaways, bullets, and core vocabulary.",
    "Generate Quiz": "Create multiple-choice practice tests with answer keys.",
    "Create Flashcards": "Generate high-yield Front/Back active recall cards.",
    "Explain Like I'm 5": "Break down complex topics into simple everyday analogies.",
}


def build_prompt(
    mode: str,
    text: str,
    num_questions: int = 5,
    difficulty: str = "Intermediate",
) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for the chosen mode."""
    if mode == "Ask Question":
        user = (
            f"Difficulty Level: {difficulty}\n\n"
            f"Please answer this student's question clearly with intuition, structured steps, and a practical example:\n\n"
            f"Question:\n{text}"
        )
    elif mode == "Summarize Notes":
        user = (
            f"Summarize the following study material:\n\n"
            f"1. **Core Concept Overview** (2-3 sentences)\n"
            f"2. **Key Takeaways & High-Yield Points** (bullet list)\n"
            f"3. **Essential Terms & Definitions** (table or bullet terms with 1-line definitions)\n"
            f"4. **Quick Memory Hook / Mnemonic**\n\n"
            f"Material:\n{text}"
        )
    elif mode == "Generate Quiz":
        user = (
            f"Create a {num_questions}-question multiple-choice practice quiz ({difficulty} level) from the material below.\n\n"
            f"Format requirements:\n"
            f"- Number each question clearly (e.g. **Question 1:**)\n"
            f"- Provide 4 choices (A, B, C, D)\n"
            f"- At the very end, include an **Answer Key & Detailed Explanations** section explaining why each answer is correct.\n\n"
            f"Study Material:\n{text}"
        )
    elif mode == "Create Flashcards":
        user = (
            f"Create {num_questions} high-yield study flashcards from the text below.\n"
            f"Format each card as:\n"
            f"**Card [N]**\n"
            f"- **Front (Prompt/Question):** ...\n"
            f"- **Back (Answer/Concept):** ...\n\n"
            f"Material:\n{text}"
        )
    elif mode == "Explain Like I'm 5":
        user = (
            f"Explain this concept as if I am 5 years old. Use a fun, vivid real-world analogy, "
            f"avoid complicated jargon, and finish with a 1-sentence summary that sticks:\n\n"
            f"Topic/Concept:\n{text}"
        )
    else:
        raise ValueError(f"Unknown mode: {mode}")

    return SYSTEM_PROMPT, user

import json
import logging
import os
from pathlib import Path

from groq import Groq, APIConnectionError, APIStatusError, RateLimitError
from dotenv import load_dotenv

load_dotenv()
print(os.getenv("GROQ_API_KEY"))
logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "prompt.md"
MODEL = "llama-3.1-8b-instant"
TEMPERATURE = 0
MAX_RETRIES = 3
REQUIRED_FIELDS = {"score", "verdict", "missing_requirements", "justification"}


def load_prompt() -> str:
    """Read and return the prompt template from prompt.md."""
    try:
        return PROMPT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt file not found at: {PROMPT_PATH}")
    except OSError as e:
        raise OSError(f"Failed to read prompt file: {e}") from e


def build_prompt(jd_text: str, resume_text: str) -> str:
    """Inject JD and resume text into the prompt template."""
    if not jd_text or not jd_text.strip():
        raise ValueError("jd_text must be a non-empty string.")
    if not resume_text or not resume_text.strip():
        raise ValueError("resume_text must be a non-empty string.")

    template = load_prompt()
    prompt = template.replace("{{JD_TEXT}}", jd_text.strip())
    prompt = prompt.replace("{{RESUME_TEXT}}", resume_text.strip())
    return prompt


def call_llm(prompt: str) -> str:
    """Send the prompt to Groq API and return the raw text response."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY environment variable is not set.")

    client = Groq(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Groq API returned an empty response.")
        return content

    except RateLimitError as e:
        logger.error("Groq rate limit exceeded: %s", e)
        raise
    except APIConnectionError as e:
        logger.error("Groq API connection error: %s", e)
        raise
    except APIStatusError as e:
        logger.error("Groq API status error [%s]: %s", e.status_code, e.message)
        raise


def validate_json(response: str) -> dict:
    """
    Parse response string as JSON and validate required fields are present.
    Returns the parsed dict on success.
    Raises ValueError if JSON is invalid or required fields are missing.
    """
    # Strip markdown code fences if present
    cleaned = response.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        cleaned = "\n".join(
            line for line in lines if not line.strip().startswith("```")
        ).strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Response is not valid JSON: {e}\nRaw response:\n{cleaned}") from e

    if not isinstance(parsed, dict):
        raise ValueError(f"Expected a JSON object, got: {type(parsed).__name__}")

    missing_fields = REQUIRED_FIELDS - parsed.keys()
    if missing_fields:
        raise ValueError(f"Response JSON is missing required fields: {missing_fields}")

    return parsed


def evaluate_resume(jd_text: str, resume_text: str) -> dict:
    """
    Orchestrate prompt building, LLM call, and JSON validation.
    Retries up to MAX_RETRIES times on invalid JSON.
    Returns parsed evaluation dict on success.
    """
    prompt = build_prompt(jd_text, resume_text)

    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        logger.info("LLM evaluation attempt %d/%d", attempt, MAX_RETRIES)
        try:
            raw_response = call_llm(prompt)
            result = validate_json(raw_response)
            logger.info("LLM evaluation succeeded on attempt %d", attempt)
            return result

        except ValueError as e:
            last_error = e
            logger.warning(
                "Attempt %d/%d — invalid JSON response: %s",
                attempt,
                MAX_RETRIES,
                e,
            )
            continue

        except (RateLimitError, APIConnectionError, APIStatusError) as e:
            last_error = e
            logger.error(
                "Attempt %d/%d — Groq API error, aborting retries: %s",
                attempt,
                MAX_RETRIES,
                e,
            )
            raise

    raise ValueError(
        f"Failed to obtain valid JSON from LLM after {MAX_RETRIES} attempts. "
        f"Last error: {last_error}"
    )
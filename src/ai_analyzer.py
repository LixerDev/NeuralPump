import json
from openai import AsyncOpenAI
from src.logger import get_logger
from config import config

logger = get_logger(__name__)

ANALYSIS_PROMPT = """You are NeuralPump, an expert AI agent specializing in analyzing meme coin launches on the Solana PumpFun platform.

Your job is to analyze a newly launched token and score its potential. Be critical and realistic — most tokens are scams or will fail.

Analyze the following token and respond ONLY with valid JSON in this exact format:
{
  "name_score": <0-20>,
  "narrative_score": <0-25>,
  "red_flag_score": <0-25>,
  "community_score": <0-20>,
  "timing_score": <0-10>,
  "total_score": <0-100>,
  "verdict": "<STRONG_BUY|BUY|WATCH|SKIP|AVOID>",
  "reasoning": "<2-3 sentence explanation>",
  "red_flags": ["<flag1>", "<flag2>"],
  "positives": ["<positive1>", "<positive2>"]
}

Scoring criteria:
- name_score (0-20): Is the name original, catchy, memorable? Does it have meme potential?
- narrative_score (0-25): Does it have a strong story or narrative? Is it relevant to current trends (AI, gaming, culture)?
- red_flag_score (0-25): Are there red flags? (generic name, copy-paste description, no socials, suspicious pattern). Higher = FEWER red flags.
- community_score (0-20): Community/viral potential. Does it have Twitter, Telegram, website?
- timing_score (0-10): Is the launch timing good? Early in a trend is better.

Verdicts:
- STRONG_BUY: Score 80-100, very high confidence
- BUY: Score 65-79, good opportunity
- WATCH: Score 50-64, monitor for momentum
- SKIP: Score 30-49, low potential
- AVOID: Score 0-29, high risk or obvious scam

Token to analyze:
"""


class AIAnalyzer:
    """Uses GPT to analyze a PumpFun token and return a structured score."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

    async def analyze(self, token_data: dict) -> dict | None:
        """
        Analyze a token using GPT.

        Parameters:
        - token_data (dict): Token metadata from PumpFun.

        Returns:
        - dict: Structured analysis result, or None if analysis failed.
        """
        prompt = ANALYSIS_PROMPT + json.dumps(token_data, indent=2)

        try:
            response = await self.client.chat.completions.create(
                model=config.GPT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=config.GPT_MAX_TOKENS,
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            raw = response.choices[0].message.content
            result = json.loads(raw)

            # Validate required fields
            required = ["total_score", "verdict", "reasoning", "red_flags", "positives"]
            if not all(k in result for k in required):
                logger.warning(f"Incomplete AI response for {token_data.get('name')}")
                return None

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            return None
        except Exception as e:
            logger.error(f"AI analysis error for {token_data.get('name')}: {e}")
            return None

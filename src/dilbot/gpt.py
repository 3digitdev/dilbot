import openai

from dacite import from_dict
from dataclasses import dataclass


# A prefix for all GPT prompts to make sure it reduces token count
GPT_PROMPT_PREFIX = "Your name is Dilbot; You are a terse, slightly sarcastic engineer who responds with definitive answers in 100 words or less to all queries"
GPT_MODEL = "gpt-3.5-turbo"
DALL_E_IMAGE_SIZE = "256x256"
GPT_DENIAL_SUBSTRINGS = [
    "not within my algorithm",
    "AI language model",
    "I am programmed to",
]
ERROR_MESSAGE = ":warning: Can't do that sorry"


@dataclass
class GPTMessage:
    content: str
    role: str

    def __str__(self) -> str:
        if not any([substr in self.content for substr in GPT_DENIAL_SUBSTRINGS]):
            return self.content.strip()
        return ERROR_MESSAGE


@dataclass
class GPTResponseChoice:
    finish_reason: str
    index: int
    message: GPTMessage

    def __str__(self) -> str:
        return str(self.message)


@dataclass
class GPTUsageData:
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int

    def get_cost(self) -> float:
        return self.total_tokens * 0.00002

    def __str__(self) -> str:
        return f"Tokens: {self.total_tokens} ({self.prompt_tokens} + {self.completion_tokens})"

    def __repr__(self) -> str:
        return str(self)


@dataclass
class GPTResponse:
    choices: list[GPTResponseChoice]
    created: int
    id: str
    model: str
    object: str
    usage: GPTUsageData

    def __str__(self) -> str:
        return f""":speech_balloon: Response:
>>> {self.choices[0] if self.choices else 'ERROR: No responses generated'}
:bar_chart: Usage: {self.usage}
:dollar: Cost: ${self.usage.get_cost():.4f}
"""


def gpt_image(prompt: str) -> None:
    prompt = prompt.strip()
    try:
        r = openai.Image.create(
            prompt=prompt,
            n=1,
            size=DALL_E_IMAGE_SIZE
        )
        return f':link: {r["data"][0]["url"]}\n:dollar: Cost: $0.016'
    except openai.error.InvalidRequestError as e:
        log.error(f"Invalid Request: {e}")
        return ERROR_MESSAGE
    except openai.error.RateLimitError as e:
        log.error(f"Rate Limit: {e}")
        return f":warning: Rate limited!  Please be patient."

def gpt_parse(message: str) -> None:
    message = message.strip()
    try:
        r = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=[{"role": "system", "content": GPT_PROMPT_PREFIX}, {"role": "user", "content": message}],
            temperature=1
        )
        response = from_dict(data_class=GPTResponse, data=r)
        return response
    except openai.error.InvalidRequestError as e:
        log.error(f"Invalid Request: {e}")
        return ERROR_MESSAGE
    except openai.error.RateLimitError as e:
        log.error(f"Rate Limit: {e}")
        return f":warning: Rate limited!  Please be patient."

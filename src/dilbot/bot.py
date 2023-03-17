import discord
import os
import requests
import re
import logging

from googlesearch import search

from .gpt import *

HELP_MSG = """
Hello there!  I'm Dilbot, and I'm just here to help you suffer through your workday. :sun_with_face:

**How to use me:**

All commands start with pinging me (noted by `<ping>` below):
```
<ping> image of {prompt}  | Generate image with DALL-E
<ping> xkcd {prompt}      | Search for an XKCD by that prompt
<ping> {anything else}    | Run the text in OpenAI GPT 3.5
```

If DALL-E or GPT functions would return an error, or if you butt up against the
GPT content moderation rules, I will simply reply with
> :warning: Can't do that sorry
GPT can be...wordy with those responses.  Nobody needs that.

Additionally, GPT functionality is setup to only respond in **100 words or less!**
_This is to save Max money.  Shit's expensive, yo._

_Please note that DALL-E and GPT 3.5 commands cost Max money! Be nice.
**I keep track of usage, and will send you an invoice if you misbehave**_ :smiling_imp:
"""
BOT_ROLE = '1086130719849463822'

logging.basicConfig(level=logging.INFO)


class ChatClient(discord.Client):
    message: list[str] = []

    async def on_ready(self):
        print(f"{self.user} has connected to Discord")

    async def on_message(self, message: discord.Message):
        # Ignore own messages
        if message.author == self.user:
            return
        logging.info(f"MESSAGE: {message.content}\nAUTHOR: {message.author}\nBOT: {self.user}")
        # Matches both pinging the bot and the role, just in case
        ping_regex = re.compile(f'^<@&?(?:{self.user.id}|{BOT_ROLE})> (.*)')
        result = ping_regex.findall(message.content)
        # Bot was pinged
        if result:
            prompt = result[0]
            if "help" == prompt.lower():
                resp = HELP_MSG
            elif "image of " == prompt[0:9]:
                resp = gpt_image(prompt[9:])
            elif prompt.startswith("xkcd "):
                result = search(prompt, tld='com', num=1, stop=1)
                link = next(result)
                print(f"Link: {link}")
                resp = f":link: {link}"
            else:
                resp = gpt_parse(prompt)
            await message.reply(resp)
            return


def main():
    token = os.getenv("DISCORD_TOKEN")
    openai.organization = os.getenv("GPT_ORG")
    openai.api_key = os.getenv("GPT_TOKEN")
    if not token or not openai.api_key or not openai.organization:
        print("ERROR:  MISSING ONE OF ['DISCORD_TOKEN', 'GPT_TOKEN', 'GPT_ORG'] ENV VARIABLES")
        exit(1)
    client = ChatClient()
    client.run(token)

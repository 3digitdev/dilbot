FROM python:3.11.2-slim

RUN pip install poetry~=1.4.0
RUN mkdir discord_bot
WORKDIR discord_bot
COPY src/ ./src
COPY pyproject.toml ./
COPY poetry.lock ./
RUN poetry install

ENTRYPOINT ["poetry", "run", "bot"]

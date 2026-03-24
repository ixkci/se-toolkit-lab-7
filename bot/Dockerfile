# Используем образ с предустановленным uv
ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}astral/uv:python3.14-bookworm-slim AS builder

WORKDIR /app

# Копируем только конфигурацию
COPY pyproject.toml ./

# uv sync создаст виртуальное окружение (.venv) и установит туда зависимости
RUN uv sync --no-install-project

# Копируем остальной код бота
COPY . .

# Запускаем бота через uv run, чтобы использовать созданное виртуальное окружение
CMD ["uv", "run", "python", "bot.py"]

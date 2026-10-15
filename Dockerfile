FROM python:3.12-slim
WORKDIR /app
COPY . .
ENV PYTHONUNBUFFERED=1
RUN python -m unittest -v test_games.py
CMD ["python", "bot.py"]

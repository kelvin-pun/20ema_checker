FROM python:3.12.5-slim-bullseye

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container
COPY . .

# Upgrade pip
RUN pip install --upgrade pip --progress-bar off

# Then install the rest of the dependencies
RUN pip install --no-cache-dir --progress-bar off -r requirements.txt

# Set environment variables (these will be overridden by docker run command)
ENV ALLOWED_USER_ID=0
ENV BOT_TOKEN=your_bot_token

# Run bot
CMD ["python", "bot.py"]

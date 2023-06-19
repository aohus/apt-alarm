import os
import socket
import datetime
from slack_sdk import WebClient
from dataclasses import dataclass
from configs.config import SLACK_TOKEN, SLACK_CHANNEL


@dataclass
class SlackContent:
    message: str
    error: str = ""


hex = {
    "green": "#00ff00",
    "red": "ff0000",
    "yellow": "#ffba01",
    "white": "ffffff",
}


# token = os.getenv("SLACK_TOKEN")
# client = WebClient(token=token)
# channel = os.getenv("SLACK_CHANNEL")
# host = socket.gethostname()
token = SLACK_TOKEN
client = WebClient(token=token)
channel = SLACK_CHANNEL


def post_message(color: str, slack_content: SlackContent):
    attachments = generate_attachments(color, slack_content)
    response = client.chat_postMessage(channel=channel, attachments=attachments)


def generate_attachments(color: str, slack_content: SlackContent) -> str:
    ts = datetime.datetime.utcnow()
    ts = ts.isoformat("T") + "Z"
    msg = f"`TS`: {ts}\n{slack_content.message}\n"

    if slack_content.error:
        msg += "*ERROR*\n```{}```".format(slack_content.error)

    return [{"color": hex[color], "title": "매일 아파트 알림", "text": msg}]


def info(message: str):
    post_message("green", SlackContent(message=message))


def error(message: str, error_message: str = ""):
    post_message(
        "red",
        SlackContent(message=message, error=error_message),
    )


def warning(message: str):
    post_message("yellow", SlackContent(message=message))

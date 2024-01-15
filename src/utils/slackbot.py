import datetime
import os
from dataclasses import dataclass
from typing import Dict
from typing import List

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


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


token = os.getenv("SLACK_TOKEN")
client = WebClient(token=token)
channel = os.getenv("SLACK_CHANNEL")


def post_apt_message(complex_name: str, available_apt_list: List[Dict]):
    attachments = generate_apt_info(complex_name, available_apt_list)
    try:
        response = client.chat_postMessage(channel=channel, **attachments)
    except SlackApiError as e:
        print(f"메시지 전송 실패: {e.response['error']}")


def generate_apt_info(complex_name: str, available_apt_list: List[Dict]):
    if available_apt_list == []:
        return {"title": complex_name, "text": f"{complex_name}: 확인된 매물이 없습니다."}

    row_text = ""
    for apt in available_apt_list:
        row_text += "{} <https://m.land.naver.com/article/info/{}|아파트이름: {}>\n".format(
            apt.get("noticed_label"), apt.get("item_id"), apt.get("title")
        )
        row_text += "동: {}\n".format(apt.get("building"))
        row_text += "가격: {}\n".format(apt.get("price"))
        row_text += "평형: {}\n".format(apt.get("size"))
        row_text += "층: {}\n".format(apt.get("floor"))
        row_text += "거실창 방향: {}\n".format(apt.get("direction"))
        row_text += "기타: {}\n".format(apt.get("describe"))
        row_text += "\n"
    if len(row_text) > 3000:
        row_text = row_text[:3000]
    text = "아파트 매일 알람"
    blocks = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"{row_text}"},
        }
    ]
    return {
        "title": f"{complex_name}",
        "text": text,
        "blocks": blocks,
    }


def post_log_message(color: str, slack_content: SlackContent):
    attachments = generate_attachments(color, slack_content)
    try:
        response = client.chat_postMessage(channel=channel, attachments=attachments)
    except SlackApiError as e:
        print(f"메시지 전송 실패: {e.response['error']}")


def generate_attachments(color: str, slack_content: SlackContent) -> str:
    ts = datetime.datetime.now()
    ts = ts.isoformat("T") + "Z"
    msg = f"`TS`: {ts}\n{slack_content.message}\n"

    if slack_content.error:
        msg += "*ERROR*\n```{}```".format(slack_content.error)

    return [{"color": hex[color], "title": "아파트 알리미 로그", "text": msg}]


def info(message: str):
    post_log_message("green", SlackContent(message=message))


def error(message: str, error_message: str = ""):
    post_log_message(
        "red",
        SlackContent(message=message, error=error_message),
    )


def warning(message: str):
    post_log_message("yellow", SlackContent(message=message))

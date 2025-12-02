import requests
import json
import os
from config import CORP_ID, CORP_SECRET, AGENT_ID, TO_USER


# 1. 获取 access_token
def get_token():
    url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={CORP_ID}&corpsecret={CORP_SECRET}"
    data = requests.get(url).json()
    return data["access_token"]


# 2. 通过企业微信上传文件，获得 media_id
def upload_file(filepath, token):
    url = f"https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={token}&type=file"
    with open(filepath, "rb") as f:
        files = {"media": (os.path.basename(filepath), f, "application/octet-stream")}
        res = requests.post(url, files=files).json()
    print("上传结果:", res)
    return res.get("media_id")


# 3. 发送文件消息
def send_file(media_id, token):
    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"
    data = {
        "touser": TO_USER,
        "msgtype": "file",
        "agentid": AGENT_ID,
        "file": {"media_id": media_id},
        "safe": 0
    }
    res = requests.post(url, json=data).json()
    print("发送结果:", res)


if __name__ == "__main__":
    # 你本地生成的课程表文件路径（请改成你真实的）
    filepath = r"./..//crawler//extracted_courses//courses_week_11.xlsx"

    print("正在获取 access_token...")
    token = get_token()

    print("正在上传文件到企业微信...")
    media_id = upload_file(filepath, token)
    if not media_id:
        raise SystemExit("❌ 文件上传失败，无法发送。")

    print("正在发送文件消息...")
    send_file(media_id, token)

    print("\n🎉 完成！请打开【微信 → 企业微信互通应用】查收文件。")

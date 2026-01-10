# parse_course_all_week.py
# -*- coding: utf-8 -*-
# 自动登录教务系统并导出 1~21 周课程表
#
# 验证码识别策略（最终版）：
# ✅ 仅使用 ddddocr
# ✅ 最多尝试 10 次
# ✅ 识别结果包含 i → 丢弃重新获取
# ❌ 不使用 Tesseract
# ❌ 不使用人工输入兜底

import os
import time
import urllib.parse
from pathlib import Path
from datetime import datetime

import requests
from PIL import Image  # 仅用于保存调试，无 OCR 处理
import ddddocr

# ================= CONFIG =================
BASE = "https://jwyth.hnkjxy.net.cn"
LOGIN_PAGE = BASE + "/"
SESS_URL = BASE + "/Logon.do?method=logon&flag=sess"
LOGIN_POST = BASE + "/Logon.do?method=logon"
CAPTCHA_URL = BASE + "/verifycode.servlet"
COURSE_EXPORT_URL = BASE + "/jsxsd/xskb/xskb_print.do"

COMMON_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/142.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
}

USERNAME = os.environ.get("JW_USERNAME")
PASSWORD = os.environ.get("JW_PASSWORD") or ""

if not USERNAME:
    raise SystemExit("❌ 请设置环境变量 JW_USERNAME / JW_PASSWORD")

# ================= UTIL =================
def save_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def make_encoded(username, password, scode, sxh):
    """
    教务系统特有的密码混淆算法
    """
    code = f"{username}%%%{password}"
    encoded = ""
    i = 0
    for ch in code:
        n = int(sxh[i]) if i < len(sxh) and sxh[i].isdigit() else 0
        encoded += ch + scode[:n]
        scode = scode[n:]
        i += 1
    return encoded

# ================= OCR CORE（最终收敛版） =================
print("✅ ddddocr 可用（唯一验证码识别方案）")
_ocr = ddddocr.DdddOcr(show_ad=False, beta=True)

def recognize_captcha_dddocr(image_path: str) -> str:
    """
    使用 ddddocr 识别验证码
    """
    try:
        with open(image_path, "rb") as f:
            res = _ocr.classification(f.read())
        res = "".join(c for c in res.lower() if c.isalnum())
        if len(res) >= 4:
            print(f"🤖 ddddocr 识别验证码: {res[:4]}")
            return res[:4]
        return ""
    except Exception as e:
        print(f"🤖 ddddocr 识别异常: {e}")
        return ""

def is_invalid_captcha(code: str) -> bool:
    """
    已知问题：
    - ddddocr 可能将 l 识别为 i
    - 实际验证码中不会出现 i
    """
    return "i" in code

def download_captcha_and_ocr(session, max_retry=10) -> str:
    """
    验证码获取与识别（最终策略）：
    - 只使用 ddddocr
    - 含 i → 丢弃
    - 最多尝试 max_retry 次
    """
    save_dir = Path(__file__).parent / "captcha_image_library"
    save_dir.mkdir(exist_ok=True)

    for attempt in range(1, max_retry + 1):
        r = session.get(
            CAPTCHA_URL + "?t=" + str(int(time.time() * 1000)),
            timeout=15
        )
        r.raise_for_status()

        img_path = save_dir / f"captcha_{datetime.now():%Y%m%d_%H%M%S_%f}.png"
        img_path.write_bytes(r.content)

        print(f"🖼 验证码已保存 ({attempt}/{max_retry}): {img_path}")

        code = recognize_captcha_dddocr(str(img_path))

        if not code:
            print("⚠️ ddddocr 未识别出结果，重新获取验证码")
            continue

        if is_invalid_captcha(code):
            print(f"♻️ 检测到非法字符 i（疑似 l→i）：{code}，重新获取验证码")
            continue

        print(f"✅ 使用验证码: {code}")
        return code

    raise RuntimeError("❌ 连续 10 次验证码识别失败（ddddocr）")

# ================= LOGIN =================
def login_via_raw_body():
    s = requests.Session()
    s.headers.update(COMMON_HEADERS)

    print("Step1: GET 登录页")
    r1 = s.get(LOGIN_PAGE, timeout=15)
    save_text(Path("debug/debug_loginpage.html"), r1.text)

    print("Step2: 获取 scode / sxh")
    r_sess = s.post(SESS_URL, timeout=15)
    scode, sxh = r_sess.text.strip().split("#", 1)

    captcha = download_captcha_and_ocr(s)
    encoded = make_encoded(USERNAME, PASSWORD, scode, sxh)

    body = (
        f"userAccount={USERNAME}"
        f"&userPassword="
        f"&RANDOMCODE={urllib.parse.quote_plus(captcha)}"
        f"&encoded={urllib.parse.quote_plus(encoded)}"
    )

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": BASE,
        "Referer": LOGIN_PAGE,
        "User-Agent": COMMON_HEADERS["User-Agent"],
    }

    print("Step3: 提交登录请求")
    r_post = s.post(
        LOGIN_POST,
        data=body.encode(),
        headers=headers,
        allow_redirects=False
    )
    return s, r_post

# ================= EXPORT =================
def export_course_xls(session, login_resp):
    if "Location" not in login_resp.headers:
        print("❌ 登录失败")
        return

    loc = login_resp.headers["Location"]
    if loc.startswith("/"):
        loc = BASE + loc

    session.get(loc, timeout=15)
    out_dir = Path("extracted_courses")
    out_dir.mkdir(exist_ok=True)

    for week in range(1, 22):
        print(f"📤 导出第 {week} 周课程表")
        params = {
            "xnxq01id": "2025-2026-1",
            "zc": str(week),
            "kbjcmsid": "C26030BDC5F8456CBE75B8779AED2F8A",
            "wkbkc": "1",
        }

        r = session.get(COURSE_EXPORT_URL, params=params, timeout=20)
        save_path = out_dir / f"courses_week_{week:02}.xls"
        save_path.write_bytes(r.content)

        if b"loginForm" in r.content:
            print(f"❌ 第 {week} 周失败（登录失效）")
        else:
            print(f"✅ 第 {week} 周成功: {save_path}")

    print("🎉 1~21 周课程导出完成")

# ================= MAIN =================
if __name__ == "__main__":
    session, resp = login_via_raw_body()
    export_course_xls(session, resp)

# parse_course_by_week.py
# -*- coding: utf-8 -*-
# pip install requests beautifulsoup4 pillow pytesseract

import os
import time
import urllib.parse
import webbrowser
from pathlib import Path
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageFilter, ImageOps
import pytesseract

# ---------------- CONFIG ----------------
BASE = "https://jwyth.hnkjxy.net.cn"
LOGIN_PAGE = BASE + "/"
SESS_URL = BASE + "/Logon.do?method=logon&flag=sess"
LOGIN_POST = BASE + "/Logon.do?method=logon"
CAPTCHA_URL = BASE + "/verifycode.servlet"
COURSE_EXPORT_URL = BASE + "/jsxsd/xskb/xskb_print.do"

# OCR 配置
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # 如果已加入环境变量，可留空
if TESSERACT_PATH and os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
}

USERNAME = os.environ.get("JW_USERNAME")
PASSWORD = os.environ.get("JW_PASSWORD") or ""
if USERNAME is None:
    raise SystemExit("请先通过环境变量 JW_USERNAME / JW_PASSWORD 提供登录凭证")

# ---------------- UTIL ----------------
def extract_hidden_fields(html):
    soup = BeautifulSoup(html, "html.parser")
    return {i.get("name"): i.get("value", "") for i in soup.select("input[type=hidden]") if i.get("name")}

def make_encoded(username, password, scode, sxh):
    code = f"{username}%%%{password}"
    encoded = ""
    i = 0
    while i < len(code):
        if i < 20:
            try:
                n = int(sxh[i])
            except:
                n = 0
            encoded += code[i]
            if n > 0:
                encoded += scode[:n]
                scode = scode[n:]
        else:
            encoded += code[i:]
            break
        i += 1
    return encoded

def save_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return str(path)

# ---------------- OCR 验证码识别 ----------------
def preprocess_image(image_path: Path):
    """对验证码图片进行预处理，提高 OCR 识别率"""
    img = Image.open(image_path).convert("L")  # 灰度化
    img = ImageOps.invert(img)  # 反色，白底黑字
    img = img.filter(ImageFilter.MedianFilter())  # 中值滤波去噪
    threshold = 150
    img = img.point(lambda x: 255 if x > threshold else 0)  # 二值化
    return img

def recognize_captcha(image_path: str) -> str:
    """对验证码图片进行预处理并使用OCR识别"""
    try:
        img = Image.open(image_path)

        # 转为灰度图
        img = img.convert("L")

        # 二值化（去背景）
        threshold = 140
        img = img.point(lambda x: 255 if x > threshold else 0)

        # 去除边缘噪点
        img = ImageOps.expand(img, border=5, fill="white")
        img = img.filter(ImageFilter.MedianFilter(size=3))

        # OCR识别
        config = "--psm 7 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        text = pytesseract.image_to_string(img, config=config)

        # 清洗输出结果
        text = "".join(ch for ch in text.strip() if ch.isalnum())
        if len(text) < 4:  # 验证码一般为4位
            raise ValueError("识别结果过短")
        print(f"🤖 OCR 识别验证码: {text}")
        return text
    except Exception as e:
        print(f"🤖 OCR 识别验证码: [识别失败]（{e}）")
        return ""

def download_captcha_and_ocr(session):
    """下载验证码 -> OCR 识别"""
    r = session.get(CAPTCHA_URL + "?t=" + str(int(time.time())), headers=COMMON_HEADERS, timeout=15)
    r.raise_for_status()
    save_dir = Path(__file__).parent / "captcha_image_library"
    save_dir.mkdir(exist_ok=True)
    filename = f"captcha_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    save_path = save_dir / filename

    with open(save_path, "wb") as f:
        f.write(r.content)
        f.flush()
    print("🖼 验证码已保存到:", save_path)

    captcha_text = recognize_captcha(save_path)
    if not captcha_text or len(captcha_text) < 4:
        print("⚠️ OCR 识别不稳定，请人工输入:")
        try:
            webbrowser.open("file://" + str(save_path))
        except Exception:
            pass
        captcha_text = input("请输入验证码（区分大小写）：").strip()
    return captcha_text

# ---------------- LOGIN ----------------
def login_via_raw_body():
    s = requests.Session()
    s.headers.update(COMMON_HEADERS)

    print("Step1: GET 登录页")
    s.get(LOGIN_PAGE, timeout=15)

    print("Step2: 获取 scode/sxh")
    r_sess = s.post(SESS_URL, headers=COMMON_HEADERS, timeout=15)
    if "#" not in r_sess.text:
        raise RuntimeError("flag=sess 未返回 scode/sxh")
    scode, sxh = r_sess.text.strip().split("#", 1)
    print("scode len:", len(scode), "sxh len:", len(sxh))

    captcha = download_captcha_and_ocr(s)
    encoded = make_encoded(USERNAME, PASSWORD, scode, sxh)
    encoded_q = urllib.parse.quote_plus(encoded)
    body = f"userAccount={USERNAME}&userPassword=&RANDOMCODE={urllib.parse.quote_plus(captcha)}&encoded={encoded_q}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": BASE,
        "Referer": LOGIN_PAGE,
    }

    print("Step3: 发送登录请求...")
    r_post = s.post(LOGIN_POST, data=body.encode("utf-8"), headers=headers, allow_redirects=False, timeout=20)
    return s, r_post

# ---------------- EXPORT XLS ----------------
def export_course_xls(session, login_resp):
    if 300 <= login_resp.status_code < 400 and login_resp.headers.get("Location"):
        loc = login_resp.headers["Location"]
        if loc.startswith("/"):
            loc = BASE.rstrip("/") + loc
        print(f"✅ 登录成功！访问重定向地址以激活登录态: {loc}")
        session.get(loc, headers=COMMON_HEADERS, timeout=15)

        week_number = input("请输入要导出的周数（留空则导出全部）：").strip()
        zc_param = week_number if week_number else ""
        print(f"📅 请求导出第 {week_number or '全部'} 周课程表...")

        params = {
            "xnxq01id": "2025-2026-1",
            "zc": zc_param,
            "kbjcmsid": "C26030BDC5F8456CBE75B8779AED2F8A",
            "wkbkc": "1",
        }
        r_export = session.get(COURSE_EXPORT_URL, headers=COMMON_HEADERS, params=params, timeout=20)

        out_dir = Path("extracted_courses")
        out_dir.mkdir(exist_ok=True)
        save_path = out_dir / f"courses_week_{zc_param or 'all'}.xls"
        with open(save_path, "wb") as f:
            f.write(r_export.content)

        content_bytes = r_export.content
        if b"loginForm" in content_bytes or "请输入账号".encode("utf-8") in content_bytes:
            print("❌ 导出失败: 登录态失效，返回登录页 HTML")
        else:
            print(f"✅ 导出成功: {save_path}")
    else:
        print("登录未成功，请检查 debug_raw_post.html")

# ---------------- MAIN ----------------
if __name__ == "__main__":
    session, login_resp = login_via_raw_body()
    export_course_xls(session, login_resp)

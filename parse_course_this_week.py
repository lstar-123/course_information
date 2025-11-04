# -*- coding: utf-8 -*-
# 自动登录教务系统并导出当前周课程表（支持OCR验证码识别）
# 环境依赖: pip install requests beautifulsoup4 pillow pytesseract lxml openpyxl

import os
import time
import urllib.parse
from pathlib import Path
from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageFilter, ImageEnhance
import pytesseract
import webbrowser

# ---------------- CONFIG ----------------
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
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
}

USERNAME = os.environ.get("JW_USERNAME")
PASSWORD = os.environ.get("JW_PASSWORD") or ""
if USERNAME is None:
    raise SystemExit("❌ 请先通过环境变量 JW_USERNAME / JW_PASSWORD 提供登录凭证")

# ---------------- UTIL ----------------
def extract_hidden_fields(html):
    soup = BeautifulSoup(html, "html.parser")
    return {i.get("name"): i.get("value", "") for i in soup.select("input[type=hidden]") if i.get("name")}

def make_encoded(username, password, scode, sxh):
    code = f"{username}%%%{password}"
    encoded = ""
    i = 0
    for ch in code:
        if i < len(sxh) and sxh[i].isdigit():
            n = int(sxh[i])
        else:
            n = 0
        encoded += ch + scode[:n]
        scode = scode[n:]
        i += 1
    return encoded

def save_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return str(path)

# ---------- OCR 部分 ----------
def preprocess_image(image_path):
    """对验证码图像进行预处理"""
    img = Image.open(image_path).convert("L")
    img = img.filter(ImageFilter.MedianFilter())
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)
    threshold = 140
    img = img.point(lambda x: 0 if x < threshold else 255, '1')
    return img

def recognize_captcha(image_path, retries=3):
    """多次识别验证码，自动过滤非字母数字"""
    for i in range(retries):
        img = preprocess_image(image_path)
        text = pytesseract.image_to_string(
            img,
            config="--psm 7 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        )
        text = "".join(c for c in text if c.isalnum()).strip()
        if len(text) == 4:
            print(f"🤖 OCR 识别中间结果: {text}")
            return text
        time.sleep(0.5)
    print("🤖 OCR 识别失败，进入人工输入模式。")
    return None

def download_captcha_and_ocr(session):
    r = session.get(CAPTCHA_URL + "?t=" + str(int(time.time())), headers=COMMON_HEADERS, timeout=15)
    r.raise_for_status()
    save_dir = Path(__file__).parent / "captcha_image_library"
    save_dir.mkdir(exist_ok=True)
    filename = f"captcha_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    save_path = save_dir / filename
    with open(save_path, "wb") as f:
        f.write(r.content)
    print("🖼 验证码已保存到:", save_path)

    captcha_text = recognize_captcha(save_path)
    if not captcha_text:
        try:
            if os.name == "nt":
                os.startfile(str(save_path))
            else:
                webbrowser.open("file://" + str(save_path))
        except Exception:
            print("⚠️ 无法自动打开验证码，请手动查看:", save_path)
        captcha_text = input("请输入验证码（区分大小写）：").strip()
    else:
        print(f"🤖 OCR 自动识别验证码: {captcha_text}")
    return captcha_text

# ---------------- LOGIN ----------------
def login_via_raw_body():
    s = requests.Session()
    s.headers.update(COMMON_HEADERS)
    print("Step1: GET 登录页")
    r1 = s.get(LOGIN_PAGE, timeout=15)
    save_text(Path("debug") / "debug_loginpage.html", r1.text)

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
        "User-Agent": COMMON_HEADERS["User-Agent"],
    }

    print("Step3: 发送登录请求...")
    r_post = s.post(LOGIN_POST, data=body.encode("utf-8"), headers=headers, allow_redirects=False, timeout=20)
    return s, r_post

# ---------------- 自动判断当前周 ----------------
def get_current_week():
    open_day = datetime(2025, 9, 15, tzinfo=timezone(timedelta(hours=8)))  # 开学日
    now = datetime.now(timezone(timedelta(hours=8)))
    days_diff = (now - open_day).days
    if days_diff < 0:
        return 1
    return (days_diff // 7) + 1

# ---------------- EXPORT XLS ----------------
def export_course_xls(session, login_resp):
    if 300 <= login_resp.status_code < 400 and login_resp.headers.get("Location"):
        loc = login_resp.headers["Location"]
        if loc.startswith("/"):
            loc = BASE.rstrip("/") + loc
        print(f"✅ 登录成功！访问重定向地址以激活登录态: {loc}")
        session.get(loc, headers=COMMON_HEADERS, timeout=15)

        week_number = get_current_week()
        print(f"📅 自动识别当前为第 {week_number} 周")

        params = {
            "xnxq01id": "2025-2026-1",
            "zc": str(week_number),
            "kbjcmsid": "C26030BDC5F8456CBE75B8779AED2F8A",
            "wkbkc": "1",
        }

        export_headers = {
            "Referer": f"{BASE}/jsxsd/xskb/xskb_list.do",
            "Origin": BASE,
            "User-Agent": COMMON_HEADERS["User-Agent"],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        print(f"📤 正在导出第 {week_number} 周课程表...")
        r_export = session.get(COURSE_EXPORT_URL, headers=export_headers, params=params, timeout=20)

        out_dir = Path("extracted_courses")
        out_dir.mkdir(exist_ok=True)
        save_path = out_dir / f"courses_week_{week_number:02}.xls"
        with open(save_path, "wb") as f:
            f.write(r_export.content)

        content_bytes = r_export.content
        if b"loginForm" in content_bytes or "请输入账号".encode("utf-8") in content_bytes:
            print("❌ 导出失败: ⚠️ 登录态失效，返回的是登录页 HTML")
        else:
            print(f"✅ 导出成功: {save_path}")
    else:
        print("❌ 登录未成功，请检查 debug_raw_post.html")

# ---------------- MAIN ----------------
if __name__ == "__main__":
    session, login_resp = login_via_raw_body()
    export_course_xls(session, login_resp)

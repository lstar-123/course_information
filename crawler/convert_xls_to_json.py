import xlrd
import json
from pathlib import Path
from datetime import datetime, timedelta

# ------------------ 配置 --------------------
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# 设置学期开始日期
TERM_START = datetime(2025, 9, 15) # 第一周的周一

# ------------------ 日期计算 --------------------
def get_date_for_week_and_day(week_num, weekday_index):
    """
    :param week_num: "01" ~ "21"
    :param weekday_index: 0=Monday ... 6=Sunday
    :return:
    """
    week_offset = int(week_num) - 1
    delta_days = week_offset * 7 + weekday_index
    return (TERM_START + timedelta(days=delta_days)).strftime("%Y-%m-%d")

# ------------------ XLS 解析单周 --------------------
def parse_one_xls(path, week_num):
    book = xlrd.open_workbook(path)
    sheet = book.sheet_by_index(0)

    courses = []

    # 行 4-9 对应 section（index 从 3 开始）
    for row in range(3, 9):
        section_raw = sheet.cell_value(row, 0).strip()
        section = section_raw.replace("\n", " ")  # 简单处理

        # 列 1–7 = 周一到周日
        for col in range(1, 8):
            weekday = WEEKDAYS[col - 1]
            weekday_index = col - 1

            # 生成该天的日期
            date_str = get_date_for_week_and_day(week_num, weekday_index)

            cell = sheet.cell_value(row, col)
            if not cell or str(cell).strip() == "":
                continue  # 无课程

            lines = [l.strip() for l in str(cell).split("\n") if l.strip()]

            if len(lines) < 1:
                continue # 一行数据都没有，直接跳过

            name = lines[0] # 第一行 = 课程名称

            if len(lines) >= 4:
                classroom = lines[3] # 正常情况
            else:
                classroom = "未知教室" # 不够四行 → 自动填补

            courses.append({
                "weekday": weekday,
                "date": date_str,        # 👈 新增：日期
                "section": section,
                "name": name,
                "classroom": classroom
            })

    return courses

# ------------------ 解析整个目录 --------------------
def parse_all(directory="extracted_courses"):
    directory = Path(directory)
    results = {}

    for xls in sorted(directory.glob("*.xls")):
        week_num = xls.stem.split("_")[-1]  # courses_week_01 → 01
        courses = parse_one_xls(xls, week_num)
        results[week_num] = courses

    # 输出 JSON
    out_path = Path("data/all_weeks_courses.json")
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    print("完成：已生成", out_path)
    return results


if __name__ == "__main__":
    parse_all()

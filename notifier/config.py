# ================================================
# config.py
# 企业微信推送配置文件
# ================================================

# ⚙️ 企业ID
# 登录企业微信管理后台 → 我的企业 → 企业信息 → 企业ID
CORP_ID = "wwea577c780e37a5c8"

# ⚙️ 应用信息
# 管理后台 → 应用管理 → 你创建的自建应用 → 查看AgentId 与 Secret
AGENT_ID = 1000002  # 示例值，请替换为你应用的 AgentId
CORP_SECRET = "JCBQ-dHe-mc0g26Jnjh045pFWlsof45pN5NhQTzX1B8"

# ⚙️ 默认推送对象
# 可以是 "@all"（全体成员）或指定成员账号（如 "lingxing"）
TO_USER = "@all"

# ⚙️ 课程文件路径（程序会自动检测最新周次）
COURSE_DIR = r"../crawler/extracted_courses"
FILE_PREFIX = "courses_week_"
FILE_EXT = ".xls"

# ⚙️ 日志文件输出路径
LOG_FILE = "wecom_notifier.log"

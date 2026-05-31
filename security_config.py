# ============================================
# AI代码助手 - 安全配置文件
# ============================================
# 配置说明：
# 1. 所有敏感配置优先从环境变量读取，兜底使用默认值
# 2. 请勿将此文件分享给他人
# ============================================

import os

# ============ 管理员配置 ============
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "1993285394@qq.com")

# ============ 邮箱SMTP配置 ============
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "1993285394@qq.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# ============ 访问密码配置 ============
ACCESS_PASSWORD = os.getenv("ACCESS_PASSWORD", "ai2026code")
EMERGENCY_PASSWORD = os.getenv("EMERGENCY_PASSWORD", "Frede2026safe")

# ============ 安全设置 ============
MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "3"))
LOCKOUT_DURATION = int(os.getenv("LOCKOUT_DURATION", "300"))
ACCESS_CODE_EXPIRY = int(os.getenv("ACCESS_CODE_EXPIRY", "3600"))
LOG_FILE = os.getenv("LOG_FILE", "access_logs.txt")

# ============ 安全模式 ============
STRICT_MODE = os.getenv("STRICT_MODE", "True").lower() == "true"

# ============================================
# AI代码助手 - 安全配置文件
# ============================================
# 配置说明：
# 1. 此文件包含所有安全配置
# 2. 请勿将此文件分享给他人
# 3. 如需重置，删除此文件重新生成
# ============================================

# ============ 管理员配置 ============
ADMIN_EMAIL = "1993285394@qq.com"  # 接收通知的邮箱

# ============ 邮箱SMTP配置 ============
# QQ邮箱SMTP配置
SMTP_HOST = "smtp.qq.com"           # QQ邮箱SMTP服务器
SMTP_PORT = 465                     # SSL端口（固定）
SMTP_USER = "1993285394@qq.com"     # 你的邮箱地址
SMTP_PASSWORD = "khqaepslbppodehj"   # SMTP授权码（非邮箱密码）

# ============ 访问密码配置 ============
# 第一层保护：用户访问密码
ACCESS_PASSWORD = "ai2026code"      

# 第二层保护：管理员专用密码
EMERGENCY_PASSWORD = "Frede2026safe" 

# ============ 安全设置 ============
MAX_LOGIN_ATTEMPTS = 3              # 最大登录失败次数
LOCKOUT_DURATION = 300              # 锁定时长（秒）
ACCESS_CODE_EXPIRY = 3600           # 访问码有效期（秒）
LOG_FILE = "access_logs.txt"        # 访问日志文件

# ============ 安全模式 ============
# True = 严格模式（所有访问需要审批）
# False = 宽松模式（直接访问）
STRICT_MODE = True

# ============ SMTP状态检测 ============
# 自动检测SMTP是否可用
SMTP_CHECK_ENABLED = True           # 启动时检测SMTP

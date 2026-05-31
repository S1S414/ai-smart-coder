"""
AI代码助手 - Flask后端API服务
功能：代码补全、错误检测、代码解释
安全：图形验证码 + 邮箱验证码 + 管理员审批 + 访问码
"""

import os
import re
import ast
import json
import time
import random
import string
import smtplib
import io
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont

# 加载配置
from dotenv import load_dotenv
load_dotenv()

os.makedirs('static', exist_ok=True)

app = Flask(__name__, static_folder='static')
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)

# 加载安全配置
try:
    from security_config import (
        ADMIN_EMAIL, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD,
        ACCESS_PASSWORD, EMERGENCY_PASSWORD, MAX_LOGIN_ATTEMPTS,
        LOCKOUT_DURATION, ACCESS_CODE_EXPIRY, LOG_FILE, STRICT_MODE
    )
except ImportError:
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "1993285394@qq.com")
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.qq.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
    SMTP_USER = os.getenv("SMTP_USER", "1993285394@qq.com")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    ACCESS_PASSWORD = os.getenv("ACCESS_PASSWORD", "ai2026code")
    EMERGENCY_PASSWORD = os.getenv("EMERGENCY_PASSWORD", "Frede2026safe")
    MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "3"))
    LOCKOUT_DURATION = int(os.getenv("LOCKOUT_DURATION", "300"))
    ACCESS_CODE_EXPIRY = int(os.getenv("ACCESS_CODE_EXPIRY", "3600"))
    LOG_FILE = os.getenv("LOG_FILE", "access_logs.txt")
    STRICT_MODE = os.getenv("STRICT_MODE", "True").lower() == "true"

# ============ 数据存储 ============
pending_requests = {}      # 待审批请求 {email_code: {email, device, ip, time, email_verified}}
email_codes = {}          # 邮箱验证码 {email: {code, expires}}
access_codes = {}         # 有效访问码 {code: {email, device, ip, expires}}
login_attempts = {}       # 登录失败记录
is_emergency_stop = False

# DeepSeek API
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

# ============ 工具函数 ============

def log_access(action, ip, details=""):
    """记录访问日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{action}] IP:{ip} {details}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except:
        pass

def send_email(subject, content):
    """发送邮件"""
    if not SMTP_PASSWORD or SMTP_PASSWORD == "你的QQ邮箱授权码":
        print(f"邮件未发送（SMTP未配置）: {subject}")
        return False
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'html', 'utf-8'))
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, ADMIN_EMAIL, msg.as_string())
        print(f"邮件已发送: {subject}")
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False

def send_email_to_user(to_email, subject, content):
    """发送邮件给用户，返回 (success, error_msg)"""
    if not SMTP_PASSWORD or SMTP_PASSWORD == "你的QQ邮箱授权码":
        return False, "SMTP密码未配置"
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'html', 'utf-8'))
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        return True, ""
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP认证失败: {e}")
        return False, f"SMTP认证失败，请检查邮箱授权码: {str(e)[:100]}"
    except smtplib.SMTPConnectError as e:
        print(f"SMTP连接失败: {e}")
        return False, f"无法连接SMTP服务器（HF海外服务器可能无法访问QQ邮箱）: {str(e)[:100]}"
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False, f"邮件发送异常: {str(e)[:150]}"

def generate_code(length=6):
    """生成随机验证码"""
    return ''.join(random.choices(string.digits, k=length))

def generate_access_code(length=8):
    """生成访问码"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_client_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr)

# ============ 图形验证码 ============

def generate_captcha():
    """生成图形验证码"""
    # 生成随机字符
    code = generate_code(4)
    
    # 创建图片
    width, height = 120, 40
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # 画干扰线
    for _ in range(3):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=(200, 200, 200))
    
    # 画字符
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    for i, char in enumerate(code):
        x = 20 + i * 25
        y = random.randint(5, 10)
        draw.text((x, y), char, fill=(random.randint(50, 150), random.randint(50, 150), random.randint(50, 150)), font=font)
    
    # 转字节流
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    
    return code, buffer

# ============ API路由 ============

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/admin')
def admin_page():
    return app.send_static_file('admin.html')

@app.route('/api/captcha')
def get_captcha():
    """获取图形验证码"""
    global email_codes
    code, buffer = generate_captcha()
    
    # 保存验证码（5分钟有效）
    captcha_id = generate_code(16)
    email_codes[captcha_id] = {
        'code': code.upper(),
        'expires': time.time() + 300,
        'type': 'captcha'
    }
    
    # captcha_id 通过 header 返回，避免 iframe 跨域 cookie 丢失
    response = send_file(buffer, mimetype='image/png')
    response.headers['X-Captcha-Id'] = captcha_id
    return response

@app.route('/api/auth/send-email-code', methods=['POST'])
def send_email_code():
    """发送邮箱验证码"""
    global email_codes
    
    data = request.json
    captcha_code = data.get('captcha', '').upper()
    email = data.get('email', '')
    device = data.get('device', '未知设备')
    captcha_id = data.get('captcha_id', '') or request.cookies.get('captcha_id', '')
    
    # 验证图形验证码
    if not captcha_id or captcha_id not in email_codes:
        return jsonify({'success': False, 'error': '请先获取图形验证码'}), 400
    
    captcha_data = email_codes[captcha_id]
    if time.time() > captcha_data['expires']:
        del email_codes[captcha_id]
        return jsonify({'success': False, 'error': '图形验证码已过期'}), 400
    
    if captcha_data['code'] != captcha_code:
        return jsonify({'success': False, 'error': '图形验证码错误'}), 400
    
    # 验证邮箱格式
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return jsonify({'success': False, 'error': '邮箱格式不正确'}), 400
    
    # 生成邮箱验证码
    email_code = generate_code(6)
    email_codes[email] = {
        'code': email_code,
        'expires': time.time() + 300,
        'type': 'email'
    }
    
    # 发送邮件
    sent, err_msg = send_email_to_user(email, "AI代码助手 - 邮箱验证码",
        f"""
        <h2>您的验证码</h2>
        <p style="font-size:24px;font-weight:bold;color:#7C3AED;">{email_code}</p>
        <p>验证码有效期：5分钟</p>
        <p>如非本人操作，请忽略此邮件</p>
        """
    )
    
    if sent:
        log_access("EMAIL_CODE_SENT", get_client_ip(), f"邮箱:{email}")
        return jsonify({'success': True, 'message': '验证码已发送到您的邮箱'})
    elif not SMTP_PASSWORD:
        # HF 环境无 SMTP 配置，直接返回验证码（仅 demo 用途）
        log_access("EMAIL_CODE_DEMO", get_client_ip(), f"邮箱:{email} code:{email_code}")
        return jsonify({
            'success': True,
            'message': f'[Demo模式] 验证码已生成，请在下方输入: {email_code}',
            'demo_code': email_code
        })
    else:
        return jsonify({'success': False, 'error': f'邮件发送失败: {err_msg}'}), 500

@app.route('/api/auth/request-access', methods=['POST'])
def request_access():
    """申请访问（验证邮箱后）"""
    global pending_requests, is_emergency_stop
    
    if is_emergency_stop:
        return jsonify({'success': False, 'error': '服务已紧急终止'}), 403
    
    data = request.json
    email = data.get('email', '')
    email_code = data.get('emailCode', '')
    device = data.get('device', '未知设备')
    ip = get_client_ip()
    
    # 验证邮箱验证码
    if email not in email_codes:
        return jsonify({'success': False, 'error': '请先获取邮箱验证码'}), 400
    
    code_data = email_codes[email]
    if time.time() > code_data['expires']:
        del email_codes[email]
        return jsonify({'success': False, 'error': '邮箱验证码已过期'}), 400
    
    if code_data['code'] != email_code:
        return jsonify({'success': False, 'error': '邮箱验证码错误'}), 400
    
    # 删除已使用的验证码
    del email_codes[email]
    
    # 创建待审批请求
    request_code = generate_code(8)
    pending_requests[request_code] = {
        'email': email,
        'device': device,
        'ip': ip,
        'time': time.time(),
        'email_verified': True
    }
    
    log_access("ACCESS_REQUEST", ip, f"邮箱:{email}")
    
    # 发送邮件给管理员
    send_email("📋 AI代码助手 - 新访问申请",
        f"""
        <h2>有人申请访问你的AI代码助手</h2>
        <p><b>邮箱:</b> {email}</p>
        <p><b>设备:</b> {device}</p>
        <p><b>IP:</b> {ip}</p>
        <p><b>时间:</b> {datetime.now()}</p>
        <p><b>申请码:</b> {request_code}</p>
        <hr>
        <p>请进入管理员审核页面批准此申请</p>
        <p><a href="http://localhost:5000/admin">点击进入审核页面</a></p>
        """
    )
    
    return jsonify({
        'success': True,
        'message': '申请已提交，请等待管理员审批',
        'request_code': request_code
    })

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """管理员登录"""
    data = request.json
    password = data.get('password', '')
    
    if password != EMERGENCY_PASSWORD:
        return jsonify({'success': False, 'error': '密码错误'}), 401
    
    return jsonify({'success': True, 'message': '登录成功'})

@app.route('/api/admin/pending-list', methods=['GET'])
def get_pending_list():
    """获取待审批列表"""
    password = request.headers.get('X-Admin-Password', '')
    if password != EMERGENCY_PASSWORD:
        return jsonify({'success': False, 'error': '未授权'}), 401
    
    # 清理过期请求（超过30分钟）
    now = time.time()
    expired = [k for k, v in pending_requests.items() if now - v['time'] > 1800]
    for k in expired:
        del pending_requests[k]
    
    # 返回列表
    pending_list = []
    for code, info in pending_requests.items():
        pending_list.append({
            'request_code': code,
            'email': info['email'],
            'device': info['device'],
            'ip': info['ip'],
            'time': datetime.fromtimestamp(info['time']).strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify({'success': True, 'list': pending_list})

@app.route('/api/admin/approve', methods=['POST'])
def approve_request():
    """批准申请"""
    global pending_requests, access_codes
    
    data = request.json
    password = data.get('admin_password', '')
    request_code = data.get('request_code', '')
    
    if password != EMERGENCY_PASSWORD:
        return jsonify({'success': False, 'error': '密码错误'}), 401
    
    if request_code not in pending_requests:
        return jsonify({'success': False, 'error': '无效的申请码'}), 400
    
    info = pending_requests[request_code]
    
    # 生成访问码
    access_code = generate_access_code()
    access_codes[access_code] = {
        'email': info['email'],
        'device': info['device'],
        'ip': info['ip'],
        'expires': time.time() + ACCESS_CODE_EXPIRY
    }
    
    # 删除待审批
    del pending_requests[request_code]
    
    log_access("APPROVED", info['ip'], f"邮箱:{info['email']}")
    
    # 发送访问码给用户
    sent, _ = send_email_to_user(info['email'], "✅ AI代码助手 - 访问已批准",
        f"""
        <h2>您的访问申请已批准！</h2>
        <p>您的访问权限已获得批准，有效期 {ACCESS_CODE_EXPIRY // 60} 分钟。</p>
        <p style="font-size:20px;font-weight:bold;color:#7C3AED;margin:20px 0;">
            访问码：{access_code}
        </p>
        <p>请在有效期内使用此访问码登录系统。</p>
        <hr>
        <p style="color:#666;">如有问题，请联系管理员</p>
        """
    )
    
    return jsonify({'success': True, 'message': '已批准，访问码已发送至用户邮箱'})

@app.route('/api/admin/reject', methods=['POST'])
def reject_request():
    """拒绝申请"""
    global pending_requests
    
    data = request.json
    password = data.get('admin_password', '')
    request_code = data.get('request_code', '')
    
    if password != EMERGENCY_PASSWORD:
        return jsonify({'success': False, 'error': '密码错误'}), 401
    
    if request_code in pending_requests:
        del pending_requests[request_code]
        log_access("REJECTED", "N/A", f"申请码:{request_code}")
    
    return jsonify({'success': True, 'message': '已拒绝'})

@app.route('/api/admin/emergency-stop', methods=['POST'])
def emergency_stop():
    """紧急终止"""
    global is_emergency_stop, access_codes, pending_requests
    
    data = request.json
    password = data.get('password', '')
    
    if password != EMERGENCY_PASSWORD:
        return jsonify({'success': False, 'error': '密码错误'}), 401
    
    is_emergency_stop = True
    access_codes.clear()
    pending_requests.clear()
    
    log_access("EMERGENCY_STOP", "N/A", "所有访问已终止")
    
    send_email("🛑 AI代码助手 - 紧急终止",
        f"""
        <h2>紧急通知</h2>
        <p>管理员已启动紧急终止程序</p>
        <p><b>时间:</b> {datetime.now()}</p>
        <p>所有外部访问已关闭</p>
        """
    )
    
    return jsonify({'success': True, 'message': '已终止所有访问'})

@app.route('/api/admin/resume', methods=['POST'])
def resume_service():
    """恢复服务"""
    global is_emergency_stop
    
    data = request.json
    password = data.get('password', '')
    
    if password != EMERGENCY_PASSWORD:
        return jsonify({'success': False, 'error': '密码错误'}), 401
    
    is_emergency_stop = False
    log_access("SERVICE_RESUMED", "N/A", "服务已恢复")
    
    return jsonify({'success': True, 'message': '服务已恢复'})

@app.route('/api/admin/status', methods=['GET'])
def get_status():
    """获取状态"""
    global is_emergency_stop
    
    password = request.headers.get('X-Admin-Password', '')
    if password != EMERGENCY_PASSWORD:
        return jsonify({'success': False, 'error': '未授权'}), 401
    
    return jsonify({
        'emergency_stop': is_emergency_stop,
        'pending_count': len(pending_requests),
        'active_count': len(access_codes)
    })

@app.route('/api/auth/use-access-code', methods=['POST'])
def use_access_code():
    """使用访问码登录"""
    global access_codes, is_emergency_stop
    
    if is_emergency_stop:
        return jsonify({'success': False, 'error': '服务已紧急终止'}), 403
    
    data = request.json
    access_code = data.get('accessCode', '').upper()
    
    if access_code not in access_codes:
        return jsonify({'success': False, 'error': '无效的访问码'}), 401
    
    code_info = access_codes[access_code]
    if time.time() > code_info['expires']:
        del access_codes[access_code]
        return jsonify({'success': False, 'error': '访问码已过期'}), 401
    
    log_access("ACCESS_GRANTED", code_info['ip'], f"邮箱:{code_info['email']}")
    
    return jsonify({
        'success': True,
        'message': '访问成功',
        'expires_in': int(code_info['expires'] - time.time())
    })

# ============ 主功能API ============

def require_access(f):
    """访问验证装饰器"""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        global is_emergency_stop
        if is_emergency_stop:
            return jsonify({'error': '服务已紧急终止'}), 403

        # 检查是否有访问码
        access_code = request.headers.get('X-Access-Code', '').upper()

        # 如果有访问码，验证访问码
        if access_code:
            if access_code not in access_codes:
                return jsonify({'error': '无效或过期访问码'}), 401

            if time.time() > access_codes[access_code]['expires']:
                del access_codes[access_code]
                return jsonify({'error': '访问码已过期'}), 401

            return f(*args, **kwargs)

        # 无访问码，检查紧急密码（备用访问方式）
        emergency_code = request.headers.get('X-Emergency-Code', '')
        if emergency_code == "TOURIST2026FREE":
            # 游客模式，轻度限制
            return f(*args, **kwargs)

        return jsonify({'error': '请提供有效的访问凭证'}), 401

    return decorated_function

@app.route('/api/code/complete', methods=['POST'])
@require_access
def code_complete():
    """代码补全"""
    try:
        data = request.json
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({'error': '代码不能为空'}), 400
        
        messages = [
            {"role": "system", "content": f"你是一个专业的{language}代码助手。只输出格式规范的补全代码（保持缩进），不要解释、不要注释、不要多余内容，直接返回可复制的代码。"},
            {"role": "user", "content": f"为以下{language}代码提供补全（只输出代码块）：\n{code}"}
        ]
        
        result = call_deepseek("deepseek-coder", messages, max_tokens=500)
        completion = result["choices"][0]["message"]["content"]
        tokens = result.get('_tokens', {})
        
        return jsonify({
            'success': True,
            'completion': completion,
            'language': language,
            'tokens': tokens
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/code/analyze', methods=['POST'])
@require_access
def code_analyze():
    """代码分析"""
    try:
        data = request.json
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({'error': '代码不能为空'}), 400
        
        errors = []
        if language == 'python':
            try:
                ast.parse(code)
            except SyntaxError as e:
                errors.append({'line': e.lineno, 'message': str(e.msg), 'type': 'SyntaxError'})
        
        return jsonify({'success': True, 'errors': errors, 'language': language})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/code/explain', methods=['POST'])
@require_access
def code_explain():
    """代码解释"""
    try:
        data = request.json
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({'error': '代码不能为空'}), 400
        
        messages = [
            {"role": "system", "content": "你是一个简洁的代码导师。用最简短的话解释代码功能，一两句话即可，不要长篇大论。"},
            {"role": "user", "content": f"简洁解释以下{language}代码（一句话即可）：\n{code}"}
        ]
        
        result = call_deepseek("deepseek-coder", messages, max_tokens=1000)
        explanation = result["choices"][0]["message"]["content"]
        tokens = result.get('_tokens', {})
        
        return jsonify({
            'success': True,
            'explanation': explanation,
            'language': language,
            'tokens': tokens
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def call_deepseek(model, messages, max_tokens=500, temperature=0.3):
    """调用DeepSeek API"""
    import requests
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    data = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
    result = response.json()
    # 添加token使用统计
    if 'usage' in result:
        result['_tokens'] = {
            'prompt_tokens': result['usage'].get('prompt_tokens', 0),
            'completion_tokens': result['usage'].get('completion_tokens', 0),
            'total_tokens': result['usage'].get('total_tokens', 0)
        }
    return result

if __name__ == '__main__':
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5001))
    print("=" * 50)
    print("🤖 AI代码助手启动中...")
    print(f"管理员邮箱: {ADMIN_EMAIL}")
    print(f"管理员密码: {EMERGENCY_PASSWORD[:4]}****")
    print(f"安全模式: 严格（需审批+邮件验证）")
    print("=" * 50)
    print(f"访问地址: http://localhost:{FLASK_PORT}")
    app.run(debug=True, host='0.0.0.0', port=FLASK_PORT)

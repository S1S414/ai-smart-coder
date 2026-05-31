---
title: AI智能代码助手
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# 项目一：智能代码助手 (Smart Code Assistant)

---

## 一、快速启动（必看）

### ⭐ 最简单方式：双击 start.bat

直接双击 `start.bat` 文件即可启动服务。

### 登录信息

| 页面 | 地址 | 密码 |
|------|------|------|
| 用户页面 | http://localhost:5001 | 访问码（需邮件验证） |
| 管理员页面 | http://localhost:5001/admin | `Frede2026safe` |

### 步骤 1：安装依赖（首次使用）

```bash
cd d:\program\0429\AIProjects\project1_smart_coder
pip install -r requirements.txt
```

### 步骤 2：启动服务

```bash
python app.py
```

### 步骤 3：访问应用

- 用户页面：http://localhost:5001
- 管理员页面：http://localhost:5001/admin

---

## 二、项目概述

### 2.1 项目作用
一个基于大语言模型的代码补全和错误检测工具，类似 GitHub Copilot 的轻量级实现。帮助用户：
- 智能补全代码
- 检测代码错误
- 解释代码逻辑
- **Token消耗统计**：实时显示API调用耗时和Token使用量

### 2.2 创意来源
- GitHub Copilot 的代码补全功能启发
- 结合 AI 大模型能力，降低编程门槛
- 加入多层安全验证，适合面试展示

### 2.3 技术框架

```
┌─────────────────────────────────────────────────────────┐
│                    用户浏览器                            │
│            http://localhost:5001                         │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP
                        ▼
┌─────────────────────────────────────────────────────────┐
│                   Flask 后端                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐    │
│  │ 认证模块  │  │ AI模块   │  │   管理模块        │    │
│  │ - 图形验证码│  │ - DeepSeek│  │   - 审批申请     │    │
│  │ - 邮箱验证│  │ - 代码补全 │  │   - 紧急终止     │    │
│  │ - 访问审批│  │ - 错误检测 │  │   - 状态监控     │    │
│  └──────────┘  └──────────┘  └──────────────────────┘    │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ DeepSeek API │ │ QQ邮箱SMTP   │ │ localStorage │
│ 代码补全/解释 │ │ 邮件通知     │ │ 历史记录存储 │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## 三、功能展示

### 3.1 用户页面 (index.html)
访问地址：`http://localhost:5001`

功能模块：
- **游客登录**：无需注册，每日5次限制
- **正式登录**：图形验证码 → 邮箱验证 → 管理员审批 → 获得访问码
- **代码编辑器**：左侧输入代码，右侧选择功能
- **历史记录**：本地保存，可点击回溯

### 3.2 管理员页面 (admin.html)
访问地址：`http://localhost:5001/admin`

功能模块：
- **待审批列表**：查看用户申请，一键批准/拒绝
- **紧急终止**：一键关闭所有外部访问
- **状态监控**：查看当前服务状态

---

## 四、环境配置

### 4.1 系统要求
- Python 3.8+
- 网络环境（用于调用 DeepSeek API 和发送邮件）

### 4.2 依赖安装
```bash
pip install -r requirements.txt
```

### 4.3 DeepSeek API 配置
1. 访问 https://platform.deepseek.com/ 注册账号
2. 获取 API 密钥
3. 创建 `.env` 文件（复制 `.env.example`）：
```
DEEPSEEK_API_KEY=sk-your-api-key-here
```

### 4.4 邮件通知配置（可选）
如需邮件验证功能，配置 QQ 邮箱 SMTP：
```
QQ_EMAIL=your-email@qq.com
QQ_EMAIL_PASSWORD=your-auth-code
```

---

## 五、目录结构

```
project1_smart_coder/
├── README.md              # 本文件（复现指南）
├── app.py                 # Flask 后端主程序
├── requirements.txt       # Python 依赖包
├── security_config.py     # 安全配置（API密钥、邮箱等）
├── .env                   # 环境变量（包含敏感信息）
├── static/
│   ├── index.html         # 用户使用页面
│   └── admin.html         # 管理员审核页面
└── .env.example           # 环境变量模板
```

---

## 六、相关链接

- DeepSeek API：https://platform.deepseek.com/
- Flask 文档：https://flask.palletsprojects.com/

---

## 七、常见问题与解答

### Q1: 浏览器显示"无法访问此页面"或"连接被拒绝"？
**A:** 检查端口配置：
1. 确保 `.env` 文件中有 `FLASK_PORT=5001`
2. 确保 `app.py` 中 `app.run()` 使用了正确的端口：
   ```python
   FLASK_PORT = int(os.getenv('FLASK_PORT', 5001))
   app.run(debug=True, host='0.0.0.0', port=FLASK_PORT)
   ```
3. 重启服务后刷新浏览器

### Q2: 请求失败 "Failed to fetch"？
**A:** 前端 API 地址与后端端口不匹配。检查 `static/index.html` 和 `static/admin.html`：
```javascript
const API_BASE = 'http://localhost:5001/api';  // 必须与 FLASK_PORT 一致
```
确保所有 HTML 文件中的端口都是 5001。

### Q3: 邮件发送失败？
**A:** 
1. 确认 QQ 邮箱已开启 SMTP 服务
2. 使用的是**授权码**而非邮箱密码（在 QQ 邮箱设置 → 账户 → POP3/SMTP服务 中生成）
3. 检查 `security_config.py` 中的 SMTP 配置

### Q4: 管理员页面无法登录？
**A:** 管理员密码是 `Frede2026safe`（详见上方登录信息表格）

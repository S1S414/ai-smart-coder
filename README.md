---
title: AI智能代码助手
emoji: ''
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# 项目一：智能代码助手 (Smart Code Assistant)

## 项目背景

本工具旨在解决以下痛点：日常编程中频繁查阅文档、排查语法错误、理解陌生代码片段的效率低下问题。面向开发者提供即时可用的 AI 辅助编码能力，同时通过多层安全验证防止 API 滥用。

核心能力：
- **代码补全**：通过 Prompt Engineering 引导 LLM 根据上下文和需求描述生成代码
- **错误检测**：Python 使用 AST 做精确语法解析；其他语言（JS/Java/Go/C++/SQL）通过 LLM 语义分析检测
- **代码解释**：用自然语言解释复杂代码逻辑
- **Token 统计**：实时显示每次 API 调用的耗时与 Token 消耗量

> 定位说明：本工具是**轻量级 Web 代码辅助工具**，与 Copilot 的 IDE 级实时嵌入不同，它侧重"打开浏览器即用"的零安装体验，适合快速排查问题和理解代码片段。

支持语言：Python / JavaScript / Java / Go / C++ / SQL

---

## 快速链接

| 类型 | 链接 | 说明 |
|:---|:---|:---|
| 在线体验 | [s1s414-ai-smart-coder.hf.space](https://s1s414-ai-smart-coder.hf.space) | 用户端，代码补全/检测/解释 |
| 管理端 | [s1s414-ai-smart-coder.hf.space/admin](https://s1s414-ai-smart-coder.hf.space/admin) | 审批申请、紧急终止（密码 `Frede2026safe`） |
| 源码 | [github.com/S1S414/ai-smart-coder](https://github.com/S1S414/ai-smart-coder) | 完整代码仓库 |

> 在线版 SMTP 不可用时自动降级为 Demo 模式，无需邮件即可使用。

---

## 核心架构

### 大语言模型

- **模型**：DeepSeek-Coder（通过 DeepSeek API 调用）
- **调用方式**：OpenAI 兼容接口，Flask 后端统一封装
- **未使用 RAG（检索增强生成）**：本项目为即时对话式代码辅助，无需文档向量检索
- **未使用 Memory 机制**：每次请求独立，无上下文记忆；历史记录仅在前端 `localStorage` 中做展示回溯

### 设计架构

```
用户浏览器 ──HTTP──> Flask 后端 ──API──> DeepSeek-Coder
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
         认证模块       AI模块      管理模块
      - 图形验证码    - 代码补全    - 审批申请
      - 邮箱验证      - 错误检测    - 紧急终止
      - 邮箱降级      - 代码解释    - 状态监控
      (Demo模式)
```

- **后端**：Flask（Python），单进程多路由（`/` 用户端 + `/admin` 管理端）
- **前端**：原生 HTML/CSS/JS，无需构建工具
- **部署**：本地 `python app.py`，在线通过 Docker 自动构建至 HuggingFace Spaces
- **安全**：三层防护 + 请求限流
  - 第一层 **Captcha 图形验证码**（Pillow 生成随机扭曲文本）：防机器批量注册
  - 第二层 **邮箱验证码**（SMTP，5 分钟过期）：验证身份真实性
  - 第三层 **管理员审批 + 访问码**：人工把关，可随时回收权限
  - **频率限制**：同一 IP 每分钟最多 3 次发送验证码请求，防止短信轰炸
  - **紧急终止**：管理端一键设置全局标志位，所有 API 返回 503

---

## 运行指南

### 在线使用（无需安装）

直接打开浏览器访问：
- 用户端：[s1s414-ai-smart-coder.hf.space](https://s1s414-ai-smart-coder.hf.space)
- 管理端：[s1s414-ai-smart-coder.hf.space/admin](https://s1s414-ai-smart-coder.hf.space/admin)（密码 `Frede2026safe`）

### 本地运行

#### 1. 克隆仓库

```bash
git clone https://github.com/S1S414/ai-smart-coder.git
cd ai-smart-coder
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 配置 API Key

复制环境变量模板并填入你的密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 必填：DeepSeek API Key（注册获取：https://platform.deepseek.com/）
DEEPSEEK_API_KEY=sk-your-api-key-here

# 可选：QQ 邮箱 SMTP（不配置则自动使用 Demo 模式）
QQ_EMAIL=your-email@qq.com
QQ_EMAIL_PASSWORD=your-auth-code

# 可选：Flask 端口
FLASK_PORT=5001
```

#### 4. 启动服务

```bash
python app.py
```

#### 5. 访问

- 用户页面：`http://localhost:5001`
- 管理员页面：`http://localhost:5001/admin`（密码 `Frede2026safe`）

---

## 功能展示

### 用户端（`/`）

| 功能 | 说明 |
|:---|:---|
| 游客模式 | 无需登录，每日 5 次免费试用 |
| 正式登录 | 图形验证码 → 邮箱验证 → 管理员审批 → 获得访问码 |
| Demo 模式 | SMTP 不可用时自动降级，验证码直接展示，审批自动通过 |
| 代码编辑器 | 左侧输入代码，右侧选择补全/检测/解释 |
| 历史记录 | 本地 `localStorage` 保存，可点击回溯 |

### 管理端（`/admin`）

| 功能 | 说明 |
|:---|:---|
| 审批列表 | 查看用户申请，一键批准/拒绝 |
| 紧急终止 | 一键关闭所有外部访问 |
| 状态监控 | 查看当前服务运行状态 |

---

## 目录结构

```
project1_smart_coder/
├── app.py                 # Flask 后端主程序
├── Dockerfile             # HF Spaces 容器化配置
├── requirements.txt       # Python 依赖包
├── security_config.py     # 安全配置（API密钥、邮箱等）
├── start.bat              # Windows 一键启动脚本
├── .env.example           # 环境变量模板
├── static/
│   ├── index.html         # 用户端页面
│   └── admin.html         # 管理端页面
└── README.md
```

---

## 构建思路

本项目从零到上线，按以下阶段迭代推进：

```
构思：编程时需要什么？
├── 痛点1：频繁切浏览器查文档 → 要一个"对话式"代码助手
├── 痛点2：bug 排查费时 → 要能帮我读代码、找错误
└── 痛点3：工具不能太笨重 → 要打开浏览器就能用

第一步 | 技术选型（为什么选这些）
├── LLM：DeepSeek-Coder → 便宜、中文友好、代码能力强，OpenAI 兼容接口
├── 后端：Flask → 轻量单文件、路由灵活、适合 Docker 部署
└── 前端：原生 HTML/CSS/JS → 零构建、零依赖，HF Spaces 直接托管

第二步 | 功能迭代（逐步叠加，不是一步到位）
├── v0.1  搭通 Flask + DeepSeek API，实现基础代码补全
├── v0.2  增加错误检测（Python AST + LLM 双方案）
├── v0.3  增加代码解释、Token 统计
├── v0.4  前端 UI：代码编辑器 + 历史记录
└── v0.5  管理端：审批系统 + 紧急终止

第三步 | 安全加固（为什么做三层而不是一层）
├── 问题：API Key 暴露在公网，任何人都能刷 → 需要入口管控
├── 1. Captcha：拦住脚本批量调用
├── 2. 邮箱验证：确认是真人
├── 3. 审批 + 访问码：管理员最终把关、可随时回收
└── 额外：IP 频率限制 + 紧急终止 = 组合拳

第四步 | 部署与降级（遇到问题怎么解）
├── 本地跑通 → 推 GitHub → 部署 HF Spaces（Docker）
├── 发现：海外节点连不上 QQ 邮箱 SMTP
├── 解法：自动降级 Demo 模式（不阻塞用户）
│   ├── 验证码直接页面展示
│   └── 审批自动通过
└── 结果：本地有邮箱走完整流程，在线没有也照用
```

---

## 技术实现

### app.py 逐段拆解

本项目的核心代码在 app.py（约 660 行），分为七个区块：

| 代码段 | 大致行号 | 做什么 | 用到什么 |
|:---|:---|:---|:---|
| 导入与初始化 | 1-31 | 加载 Flask、Pillow、smtplib 等库，创建 Flask 应用实例 | Flask + flask-cors |
| 配置加载 | 33-52 | 从 `.env` 或 `security_config.py` 读取 API Key、邮箱密码等配置 | python-dotenv |
| 数据存储 | 54-59 | 用 Python 字典模拟数据库：验证码、待审批列表、访问码、登录记录 | 纯 Python dict |
| 工具函数 | 65-128 | 写日志、发邮件、生成随机码、获取客户端 IP | smtplib + random |
| 图形验证码 | 130-166 | 用 Pillow 画图：白色背景 + 干扰线 + 随机颜色数字字符 | Pillow |
| 安全 API | 168-558 | 图形验证码接口、邮箱验证码发送、提交访问申请、管理审批/拒绝/紧急终止、恢复服务 | Flask route 装饰器 |
| 功能 API | 560-657 | 代码补全 / 代码分析 / 代码解释，调用 DeepSeek | requests + Python AST |

### 一次请求的完整路径

以"用户点击代码补全"为例，请求在三方之间流转：

```text
浏览器 (index.html)               Flask 后端 (app.py)              DeepSeek API
       │                                  │                              │
       │ ① 用户输入代码，点击"补全"按钮      │                              │
       │                                  │                              │
       │ ② JS 发送 POST /api/code/complete │                              │
       │    Header: X-Access-Code: ABC123  │                              │
       │    Body: {code:"def hello()...",  │                              │
       │          language:"python"}       │                              │
       │ ───────────────────────────────→  │                              │
       │                                  │                              │
       │                       ③ @require_access 装饰器拦截              │
       │                          检查 X-Access-Code 是否有效？          │
       │                          检查访问码是否已过期？                   │
       │                          检查是否处于紧急终止状态？              │
       │                                  │                              │
       │                       ④ 构造 system prompt                      │
       │                          "你是专业的python代码助手..."          │
       │                          + 用户的代码作为 user message          │
       │                                  │                              │
       │                                  │ ⑤ POST /chat/completions     │
       │                                  │    model: deepseek-coder     │
       │                                  │    messages: [...]           │
       │                                  │ ───────────────────────────→ │
       │                                  │                              │
       │                                  │                    ⑥ AI 推理  │
       │                                  │                    生成补全代码 │
       │                                  │ ←─────────────────────────── │
       │                                  │                              │
       │                       ⑦ 提取 content 文本                      │
       │                          提取 usage.token 统计                 │
       │                                  │                              │
       │ ⑧ 浏览器收到 JSON 响应            │                              │
       │    {success: true,               │                              │
       │     completion: "print('Hello')",│                              │
       │     tokens: {prompt:48,          │                              │
       │              completion:12,      │                              │
       │              total:60}}          │                              │
       │ ←───────────────────────────────  │                              │
       │                                  │                              │
       │ ⑨ JS 把补全代码填入编辑器文本框    │                              │
```

### 前端与后端如何通信

两个 HTML 文件（`index.html` 用户端、`admin.html` 管理端）内置 JavaScript，通过 `fetch()` 调用 Flask API：

- **通信格式**：HTTP POST，请求体和返回体都是 JSON
- **身份验证**：用户访问码放在请求头 `X-Access-Code` 中，后端 `@require_access` 装饰器每次统一校验
- **无记忆机制**：每次请求独立，历史记录仅保存在浏览器 `localStorage` 中，后端不存对话上下文
- **Token 统计**：后端调用 DeepSeek 后把返回的 `usage` 字段原样带回前端用于展示

---

## 常见问题

### Q1: 浏览器显示"无法访问此页面"？
**A:** 检查 `FLASK_PORT` 配置是否正确，确保 `app.py` 中端口一致，重启服务后刷新。

### Q2: 请求失败 "Failed to fetch"？
**A:** 前端 `API_BASE` 地址与后端端口不匹配，检查 `index.html` 和 `admin.html` 中端口是否一致。

### Q3: 邮件发送失败？
**A：**
- **本地**：确认 QQ 邮箱已开启 SMTP 服务，使用的是**授权码**而非邮箱密码
- **在线**：HF Spaces 海外服务器无法访问 QQ 邮箱 SMTP，系统会**自动降级为 Demo 模式**——验证码直接显示，审批自动通过

### Q4: 管理员页面无法登录？
**A:** 管理员密码为 `Frede2026safe`。

### Q5: 为什么一套代码有两个页面？
**A:** Flask 通过不同路由实现：`/` 渲染用户端，`/admin` 渲染管理端。同一进程，无需额外部署。

### Q6: 在线版需要配置 SMTP 密码吗？
**A:** 不需要。代码自动检测 SMTP 可用性，不可用时自动降级为 Demo 模式。

### Q7: 用户登录流程是什么？
**A:** 图形验证码 → 邮箱验证码 → 提交申请 → 管理员审批 → 获得访问码 → 进入主界面。（Demo 模式下审批自动通过）

### Q8: 紧急终止是怎么实现的？
**A:** 管理端点击终止后，Flask 后端设置全局标志位，所有 `/api/*` 请求返回 HTTP 503 并拒绝对话请求，服务保持运行但不响应功能调用。重启服务后恢复正常。

### Q9: 这个项目和 GitHub Copilot 有什么区别？
**A:** Copilot 是 IDE 插件，实时感知代码上下文做行内补全。本项目是**轻量级 Web 工具**，优势在于零安装、打开浏览器即用，适合快速排查 bug、理解陌生代码，而不是替代日常编码中的 IDE 补全。

### Q10: 非 Python 语言怎么检测错误？
**A:** Python 使用 AST 做精确语法解析；JavaScript/Java/Go/C++/SQL 通过 Prompt Engineering 引导 LLM 分析代码并返回错误位置和修复建议，属于语义级检测而非语法树匹配。

### Q11: 为什么本地能发邮件、在线版不能？这是设计缺陷吗？
**A:** QQ 邮箱 SMTP 服务器在中国大陆，HuggingFace Spaces 的海外节点无法直连。这不是设计缺陷，代码已通过**自动降级**处理：检测到 SMTP 不可用时切换为 Demo 模式，验证码页面展示 + 审批自动通过。本地部署 QQ 邮箱则走完整邮件流程。

### Q12: Captcha 验证码怎么防爬虫？有没有限流？
**A:** Captcha 使用 Pillow 库动态生成随机扭曲字符 + 干扰线，增加 OCR 识别难度。同时设有限流：同一 IP 每分钟最多 3 次验证码发送，验证码 5 分钟过期且一次性消费。访问码粒度进一步控制长期滥用。

### Q13: 为什么选 Flask + 原生 HTML，而不是 Streamlit？
**A:** 本项目需要自定义安全流程（Captcha 集成、多层审批、紧急终止），Streamlit 的控制粒度不足以实现这些细粒度的交互逻辑。Flask + 原生前端给予完全的控制权，同时更适合 Docker 容器化部署在 HF Spaces。

### Q14: DeepSeek API 调用失败怎么办？
**A:** 后端设有 30 秒超时 + 自动重试机制（最多 2 次），失败后向前端返回明确错误提示而非崩溃。API Key 通过环境变量注入，部署时可在 HF Secrets 中配置，代码与密钥分离。

### Q15: 如何防止用户输入恶意 prompt 注入攻击？
**A:** 用户的代码输入作为 LLM 的 user message 传入，系统 prompt 中明确限定了助手只做代码分析，拒绝执行系统命令、访问文件等非代码任务。DeepSeek 模型本身也带有内容安全过滤。

---

## 相关链接

- GitHub 源码：[github.com/S1S414/ai-smart-coder](https://github.com/S1S414/ai-smart-coder)
- 在线 Demo：[s1s414-ai-smart-coder.hf.space](https://s1s414-ai-smart-coder.hf.space)
- DeepSeek API：[platform.deepseek.com](https://platform.deepseek.com/)
- Flask 文档：[flask.palletsprojects.com](https://flask.palletsprojects.com/)

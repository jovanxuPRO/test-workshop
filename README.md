# Test Workshop Pro

自动化测试工坊 — 模板化测试方案生成、SSE 实时执行、ISTQB 标准 JUnit XML 报告。

## 快速开始

```bash
pip install -r requirements.txt
playwright install chromium
python main.py
# 打开 http://localhost:9000
```

## 功能

### 5 步测试向导
1. 选择模板或自定义方案
2. 配置认证（Bearer / Basic / Custom Header）
3. 添加 API 端点 + 页面 URL + 验证规则
4. 一键生成测试代码
5. 实时 SSE 进度条 + 日志流

### 测试类型

| 类型 | 生成文件 | 覆盖 |
|------|---------|------|
| API | `test_api.py` | GET/POST/PUT/DELETE/HEAD/PATCH 每方法 2-8 个用例 |
| UI | `test_ui.py` | 页面加载、JS 错误、响应式、链接检查、资源加载 |
| Data | `test_data.py` | 对每个规则遍历 API 端点验证 |
| Unit | `test_unit.py` | 可达性、响应时间、SSL、重定向、并发 |

### 内置模板

- **Task Manager** — RESTful CRUD API 全方位测试
- **Baidu** — 13 API + 4 页面 + 10 规则全量
- **JSONPlaceholder** — 完整 REST 测试

### 用例管理中心 (`/tc`)

- 独立 CRUD 管理测试用例库
- 模块/优先级筛选、全文搜索
- 持久化到 `test_cases.json`

## 安全特性

- **代码注入防护**: 所有用户输入经正则净化后注入生成代码
- **SSRF 防护**: 阻止私有 IP、内网地址、云元数据端点
- **XSS 防护**: HTML 输出全量 `html.escape()`
- **凭证安全**: 认证令牌通过环境变量传递，绝不落盘
- **安全响应头**: `X-Content-Type-Options`, `X-Frame-Options`, `XSS-Protection`
- **速率限制**: 20 req/min (gnr), 30 req/min (plan)
- **并发控制**: 最多 3 个测试同时执行
- **原子写入**: JSON 文件临时文件+重命名，防止崩溃损坏

## API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/plan` | POST | 提交测试计划 |
| `/api/stream?id=` | GET | SSE 实时执行流 |
| `/api/gnr` | POST | 同步执行测试 |
| `/api/stop` | POST | 停止执行 |
| `/api/report?dir=` | GET | JUnit XML 报告 |
| `/api/report-list` | GET | 报告库 |
| `/api/report-count` | GET | 最新报告摘要 (JSON) |
| `/api/history` | GET | 执行历史 (HTML) |
| `/api/history-data` | GET | 执行历史 (JSON) |
| `/api/history/{idx}` | DELETE | 删除历史 |
| `/api/tc` | GET/POST | 用例库 CRUD |
| `/api/tc/{cid}` | PUT/DELETE | 用例更新/删除 |

## 项目结构

```
test-workshop/
├── main.py              # FastAPI 后端 (960+ 行)
├── requirements.txt     # 依赖
├── static/
│   ├── index.html       # 主界面 (5 步向导 + 仪表盘)
│   └── tc.html          # 用例管理中心
├── test_cases.json      # 用例数据持久化
├── exec_history.json    # 执行历史 (50 条上限)
└── generated_tests/     # 生成测试代码 (保留 20 个历史)
```

## 生产部署

```bash
# 环境变量
export TW_HOST=0.0.0.0          # 监听地址 (默认 127.0.0.1)
export TW_PORT=9000             # 端口 (默认 9000)
export TW_HEADLESS=true         # Playwright 无头模式
export TW_CERT_FILE=/path/cert.pem   # HTTPS 证书 (可选)
export TW_KEY_FILE=/path/key.pem     # HTTPS 私钥 (可选)

# HTTP 模式（默认）
python main.py

# HTTPS 模式
export TW_CERT_FILE=./cert.pem TW_KEY_FILE=./key.pem
python main.py
```

自签证书快速生成：
```bash
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost"
```

## 审计历史

经 20 个专业 Agent 全面审计（300+ 轮审查），覆盖：
- OWASP Top 10 安全审计
- GDPR/CCPA 隐私合规审查
- 渗透测试（SSRF/XSS/CSRF/注入）
- 代码生成注入分析
- 并发安全与事件循环分析
- 端到端集成测试

详见 [AGENTS.md](../AGENTS.md)

## License

MIT

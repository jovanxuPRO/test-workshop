# Test Workshop Pro

自动化测试工坊 — AI 驱动测试用例生成、7 层安检机式测试矩阵、SSE 实时执行、ISTQB 标准 JUnit XML 报告。

## 快速开始

```bash
# 1. 启动被测目标（企业级电商 Mock，端口 8000）
cd mock_ecommerce
pip install -r ../requirements.txt
python server.py

# 2. 启动测试工坊（端口 9000）
cd ..
python main.py
# 打开 http://localhost:9000
```

可选：`playwright install chromium`（UI 测试需要）。

## 功能

### AI 驱动的用例生成
- 集成 DeepSeek/OpenAI 等 LLM（AI 配置 Tab 管理多 profile）
- 自动分析 PRD 文档，提取实体/业务规则/状态机
- 支持推理模型（deepseek-v4-pro）：非流式调用，等待完整思考+答案后解析
- AI 失败时直接显示错误，不回退模板

### 业务上下文分析
- 📚 一键加载内置 PRD（6 份：电商 3 份 + 百度 3 份）
- 📂 多文件上传 / 粘贴任意 PRD 文本
- AI 分析提取：实体、字段、业务规则（R001-R207）、状态机
- ✏ JSON 编辑弹窗可手动修正分析结果

### 7 层安检机式测试矩阵

| 层 | 内容 |
|----|------|
| L1 | 可达性验证（所有端点 < 500） |
| L2 | 字段契约（实体字段类型/存在性） |
| L3 | 业务规则（金额/库存/唯一性/权限/状态/必填/上限） |
| L4 | 状态机（created→confirmed→paid→shipped→delivered） |
| L5 | 数据完整性（跨 API 一致性校验） |
| L6 | 安全注入（越权/SQL/XSS） |
| L7 | 边界压力（并发/P50/P95 百分位） |

### 四种测试类型

| 类型 | 生成文件 | 覆盖 |
|------|---------|------|
| 🔌 API | `test_api.py` | 每端点 2 用例 + 7 层矩阵 |
| 📱 UI | `test_ui.py` | 加载/JS错误/性能/响应式/链接/资源/三分辨率截图 |
| 📊 Data | `test_data.py` | 业务规则遍历验证 + 跨 API 完整性 |
| 🔧 Unit | `test_unit.py` | 可达性/P50/P95响应时间/SSL/重定向/10路并发 |

### 内置模板

- **E-Commerce 电商系统** — JWT认证 + 18 端点 + 订单状态机 + 退款流程
- **Baidu 百度全量** — 13 API + 4 页面 + 搜索核心/性能/安全三维度
- **Demo API** / **JSONPlaceholder**

### 用例管理中心 (`/tc`) 与 CI/CD (`/ci`)

- 用例 CRUD、模块分组、锁定机制、从用例库导入
- CI 三阶段流水线：AI 生成 → 路径筛选 → 执行验证
- 定时执行 + 一键触发 + 实时日志

### 执行控制

- SSE 实时流 + 3 态控制（⏸ 暂停 / ▶ 继续 / ⏹ 停止）
- 断线重连（后端进程保留）
- 通过率趋势 + 连续通过"可上线"判断

## 企业级 Mock 项目 (mock_ecommerce/)

17 文件全栈电商系统，作为测试靶机：

```
mock_ecommerce/
├── server.py          # FastAPI 入口 + 静态文件
├── auth.py            # JWT 签发/校验 + 三级角色 (admin/operator/viewer)
├── models.py          # Pydantic 校验 + 内存存储 + 状态机
├── routes/            # auth/products/orders/refunds/stats 五模块
├── static/            # 单页应用（登录/仪表盘/商品/订单/退款）
└── docs/              # 6 份 PRD 文档
```

预置账号：`admin/Admin@123` · `operator/Oper@123` · `viewer/View@123`

## 安全特性

- **代码注入防护**: 用户输入正则净化后注入生成代码
- **SSRF 防护**: 阻止私有 IP、内网地址、云元数据端点（进程内 DNS 解析）
- **XSS 防护**: 前端 `he()` 全量转义（含流式用例、执行历史下拉）
- **凭证安全**: 认证令牌仅内存传递，绝不落盘；AI Key AES 加密存储（HMAC 认证标签）
- **安全响应头**: CSP / X-Content-Type-Options / X-Frame-Options / Referrer-Policy
- **速率限制**: 20 req/min (gnr), 30 req/min (plan)
- **并发控制**: 信号量限制同时执行数
- **原子写入**: 临时文件+重命名，防止崩溃损坏

## API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/plan` | POST | 提交测试计划 |
| `/api/stream?id=` | GET | SSE 实时执行流 |
| `/api/gnr` | POST | 同步执行测试 |
| `/api/stop` | POST | 停止执行 |
| `/api/ai-suggest` | POST | AI 用例建议（非流式） |
| `/api/ai-suggest-stream` | POST | AI 用例建议（SSE 流式） |
| `/api/analyze-context` | POST | PRD 业务语义分析 |
| `/api/prd-list` | GET | 列出内置 PRD |
| `/api/prd-load?file=` | GET | 加载 PRD 内容 |
| `/api/ai-key` | POST | 设置/清除 AI Key（加密存储） |
| `/api/report?dir=` | GET | JUnit XML 报告 |
| `/api/report-list` | GET | 报告库 |
| `/api/report-count` | GET | 最新报告摘要 (JSON) |
| `/api/history` / `/api/history-data` | GET | 执行历史 (HTML/JSON) |
| `/api/audit-export` | GET | 合规审计导出 (JSON) |
| `/api/tc` | GET/POST | 用例库 CRUD |
| `/api/tc/{cid}` | PUT/DELETE | 用例更新/删除 |

## CLI 模式

```bash
# CI/CD 模式：从配置运行测试，输出 JUnit XML 后退出
python main.py --run-config ci-test-plan.json --headless

# 仅生成代码不执行（校验语法）
python main.py --run-config ci-test-plan.json --dry-run

# 自定义端口
python main.py --port 9100

# 报告格式
python main.py --run-config ci-test-plan.json --output-format html
```

## 项目结构

```
test-workshop/
├── main.py                  # FastAPI 后端 (~2400 行)
├── requirements.txt         # 依赖
├── Dockerfile               # 容器化
├── ci-test-plan.json        # CI 配置
├── static/
│   ├── index.html           # 主界面（向导+预览+执行+AI配置）
│   ├── tc.html              # 用例管理中心
│   └── ci.html              # CI/CD 控制台
├── mock_ecommerce/          # 企业级电商 Mock 项目
│   ├── server.py / auth.py / models.py
│   ├── routes/              # 5 个路由模块
│   ├── static/              # SPA 前端
│   └── docs/                # 6 份 PRD
├── test_cases.json          # 用例数据持久化
├── exec_history.json        # 执行历史 (50 条上限)
└── generated_tests/         # 生成测试代码 (保留 20 个历史)
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `TW_HOST` | 127.0.0.1 | 监听地址 |
| `TW_PORT` | 9000 | 端口 |
| `TW_SECRET` | 自动生成 | AI Key 加密密钥 |
| `TW_AI_KEY` | 空 | AI API Key（也可 UI 配置） |
| `TW_AI_MODEL` | gpt-4o | 默认模型 |
| `TW_AI_BASE_URL` | api.openai.com | AI API 地址 |
| `TW_HEADLESS` | false | Playwright 无头模式 |
| `TW_TRACE` | false | Playwright trace 调试 |
| `TW_CERT_FILE` / `TW_KEY_FILE` | 空 | HTTPS 证书 |

## 审计历史

经 12 代理 Flash 审计 + 20 角色深度体验审计，覆盖：
- OWASP Top 10 安全审计（SSRF/XSS/注入）
- 越权检测（cancel_order 所有权检查已修复）
- 状态机一致性（退款恢复库存已修复）
- 前端流式渲染、暂停/继续状态机
- 数据完整性（跨 API 校验）

## License

MIT

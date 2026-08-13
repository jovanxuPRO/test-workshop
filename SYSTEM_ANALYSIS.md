# 测试工坊 Pro — 系统分析与规则文档

> 生成时间：2026-08-13 | 版本：基于 main.py v2443 行 + static/ 前端 + mock_ecommerce/ 靶机

---

## 一、系统架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                        浏览器 (localhost:9000)                     │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │ Wizard 向导  │  │ Exec 执行面板 │  │ AI 配置面板   │            │
│  │ (5步输入)    │  │ (暂停/继续)   │  │ (多Profile)   │            │
│  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘            │
│         │   /tc 用例管理   │  /ci CI控制台   │                    │
└─────────┼─────────────────┼────────────────┼────────────────────┘
          │ REST API + SSE  │                │
┌─────────┴─────────────────┴────────────────┴────────────────────┐
│                       main.py (FastAPI)                          │
│                                                                  │
│  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │ AI 生成层 │ │ 7层矩阵层  │ │ 代码生成层 │ │ 执行引擎层        │   │
│  │ 用例筛查   │ │ 业务上下文 │ │ gen_code │ │ SSE + 暂停/继续    │   │
│  └──────────┘ └───────────┘ └──────────┘ └──────────────────┘   │
│  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │ 安全层    │ │ 存储层     │ │ 报告层    │ │ CLI/CI层          │   │
│  │ SSRF/加密 │ │ JSON持久化 │ │ JUnit解析 │ │ argparse/定时     │   │
│  └──────────┘ └───────────┘ └──────────┘ └──────────────────┘   │
└──────────────────────┬───────────────────────────────────────────┘
                       │ HTTP (8000)
┌──────────────────────┴───────────────────────────────────────────┐
│                mock_ecommerce/ (企业级电商靶机)                    │
│  JWT登录 · 三级角色 · 商品CRUD · 订单状态机 · 退款流程 · SPA前端    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 二、功能模块清单

### M1. 测试向导（Wizard）
**位置**: static/index.html `tab-plan`

| 步骤 | 内容 | 数据流 |
|------|------|--------|
| 1. 模板与项目信息 | 3 模板（电商/百度/Demo）+ 项目名 + Base URL + 认证方式 | → localStorage `wiz` |
| 2. API 接口 | 方法(GET/POST) + 路径 + 说明，▶ 快测单端点 | → `apis[]` |
| 3. Web 页面 | 路径 + 名称 + 浏览器 | → `pages[]` |
| 4. 数据规则 | 每行一条规则 | → `rules[]` |
| 5. 业务上下文 | PRD 导入/上传/粘贴 + AI 分析 | → `_ctx` |

**规则 W1**: Base URL 经 `fixUrl()` 自动修正（localhost → 127.0.0.1:8000，补 http:// 前缀，去尾部斜杠）
**规则 W2**: 方法仅 GET/POST
**规则 W3**: 所有输入实时 `save()` 到 localStorage，防丢失

### M2. AI 用例生成（AI Generation）
**位置**: main.py `/api/ai-suggest-stream`（流式SSE）+ `/api/ai-suggest`（同步）

**流程**:
```
用户点击生成 → POST /api/ai-suggest-stream
  → 校验: is_safe_url(base_url)  [规则A1]
  → 校验: AI Key 存在且长度≥20 且前缀 sk-/fk-/ak-  [规则A2]
  → 构造 prompt（API列表 + 业务规则 + "只输出JSON行,method只用GET/POST"）
  → 非流式调用 LLM（timeout=300s，max_tokens≥16000）  [规则A3]
  → 解析 message.content 中所有 {...} JSON 对象  [规则A4]
  → _validate_cases 筛查  [规则A5]
  → SSE 事件流: info → clear → case×N → done
```

**规则 A1（SSRF）**: base_url 拒绝私有IP/内网/云元数据/file:///gopher://；`127.0.0.1:8000` 白名单
**规则 A2（Key格式）**: 长度≥20 且以 sk-/fk-/ak- 开头；乱码 key 直接拒绝，不发起 HTTP 调用
**规则 A3（推理模型）**: deepseek-v4-pro 是推理模型，流式返回 reasoning_content 先于 content；因此改用非流式调用，等待完整响应后解析
**规则 A4（解析容错）**: 花括号深度匹配提取每个 JSON 对象，单个解析失败跳过不影响其余
**规则 A5（用例筛查）**:
- 方法 ∈ {GET, POST}，否则剔除
- 路径必须以 / 或 http 开头
- 优先级 ∈ {P0,P1,P2}，否则归一化 P1
- title 必填且 ≤200 字符
- 去重: 方法+路径+标题 相同只留第一条
- 路径与配置 API 不匹配 → 打 `_path_mismatch` 标记保留
- 全部剔除 → 返回 error

### M3. 业务上下文分析（Context Analysis）
**位置**: main.py `/api/analyze-context` + `_analyze_with_ai` + `_analyze_with_heuristic`

**流程**: PRD 文本 → AI 分析 → `{entities, relations, state_machine, business_rules}` → 前端渲染 + 可编辑

**规则 C1**: 文本上限 50000 字符
**规则 C2**: 有 AI Key → AI 分析（温度0.2，max_tokens 6000）；无 Key → 启发式正则提取
**规则 C3（启发式）**: 从 `## 标题`/`/api/xxx` 提取实体；从 `R###:` 编号提取规则；从状态流转章节提取状态机
**规则 C4**: 分析结果可 JSON 编辑（弹窗），编辑后 `save()` 持久化
**规则 C5**: 重新分析时智能合并（新结果稀疏时保留旧实体/状态机）

### M4. 7 层安检机测试矩阵（Layered Matrix）
**位置**: main.py `_layered_tests`

| 层 | 生成规则 | 触发条件 |
|----|---------|---------|
| L1 可达性 | 每端点一条 `status_code < 500` | 有上下文即生成 |
| L2 字段契约 | 实体字段全存在 `all(k in d[0] for k in [...])` | 实体有 fields 列表 |
| L3 业务规则 | 关键词匹配: 金额/库存/唯一/权限/状态/必填/上限/通用 | 规则含关键词 |
| L4 状态机 | 实体 create→verify 序列测试 | 上下文有 state_machine |
| L5 数据完整性 | 订单金额=Σ(单价×数量) 跨API校验 | ≥2 个 API |
| L6 安全注入 | 剥认证头请求，断言 401/403 | 每端点 |
| L7 边界压力 | ThreadPoolExecutor 10 并发，全部 <500 | 每端点 |

**规则 L3-1（金额/库存）**: 负数拒绝，断言 400/422
**规则 L3-2（唯一性）**: 重复值 POST，断言 200/201/400/409
**规则 L3-3（权限）**: 断言 200/401/403
**规则 L3-4（状态流转）**: DELETE 到不存在 id，断言 400/404
**规则 L3-5（必填）**: 空字段 POST，断言 400/422
**规则 L3-6（上限）**: 超大金额，断言 400/422

### M5. 测试代码生成（Code Gen）
**位置**: main.py `gen_code` + `_exact_test`

**流程**: plan → conftest.py + test_api.py + test_ui.py + test_data.py + test_unit.py

**规则 G1**: 路径参数 `{xxx}` 统一替换为 `1`（`re.sub(r'\{[^}]+\}', '1', p)`）
**规则 G2**: 方法白名单，非法方法降级 GET
**规则 G3（authValue 净化）**: 正则 `[^\w\-=+/,.:;@#$%^&*()!]` 过滤后经环境变量传递，绝不写入生成文件
**规则 G4（_exact_test 关键词匹配）**:
- 安全类优先: SQL注入 → `<500`；XSS → `400+ 或 "<script>" not in text`
- 错误类: 缺少→400/422/401；不存在→404/400；未认证→401/403；无效→400/422；重复→400/409
- 正常类: 创建→200/201；更新→200/201/204；删除→200/204；查询→200；详情→200/404；登录→200/201
**规则 G5（GET 方法）**: GET 不带 json body（httpx Client.get 不支持 json 参数）
**规则 G6**: 保留最近 20 个生成目录，自动清理

### M6. 执行引擎（Execution Engine）
**位置**: main.py `/api/plan` + `/api/stream` + `_run_stream` + `_attach_existing` + `/api/stop`

**状态机**:
```
[新建] → POST /api/plan → PLANS[pid]
  ↓ GET /api/stream
[运行中] ←────┐ resume: GET /api/stream
  ↓ 客户端断开  │ (进程继续跑，输出进持久队列)
[已暂停] ──────┘
  ↓ __END__（pytest 自然结束）
[完成] → save_hist_entry + save_auto_tcs + update_tc_status
  ↓ POST /api/stop（任意时刻）
[已停止] → 杀进程 + 清理全部状态
```

**规则 E1**: `RUN_PROCS[pid]` 进程表、`RUN_QUEUES[pid]` 持久输出队列、`RUN_TALLIES[pid]` 跨重连计数器
**规则 E2**: 暂停 = 断开 SSE，不杀进程；继续 = 重连同一队列续读（断线期间输出不丢）
**规则 E3**: 停止 = 唯一杀进程入口，清理 RUN_PROCS/RUN_QUEUES/RUN_TALLIES/PLANS
**规则 E4**: 10 分钟超时上限
**规则 E5**: pytest 参数 `-v --tb=line --color=no --junitxml=results.xml`
**规则 E6**: 计数解析: `PASSED/Failed/ERROR` + `::` 判定单条用例
**规则 E7**: 完成时保存历史（50条上限）+ 自动保存用例库 + 更新用例状态

### M7. 报告层（Report）
**位置**: `/api/report` + `/api/report-count` + `/api/report-list` + `/api/history` + `/api/audit-export`

**规则 R1**: 报告统计 `passed = total - failed - errors - skipped`（skipped 必须扣除）
**规则 R2**: 通过率 = passed/total，防除零
**规则 R3**: 历史含趋势（最近10次）+ 连续通过 streak + 可上线判断（streak≥3）
**规则 R4**: audit-export 导出执行历史+用例库 JSON 供合规审计

### M8. 安全层（Security）
**规则 S1（SSRF）**: `is_safe_url` 进程内 DNS 解析，拒绝私有/回环/保留/多播 IP，拒绝 169.254.169.254 云元数据
**规则 S2（AI Key 加密）**: PBKDF2-HMAC-SHA256 派生密钥（10万轮），HMAC 认证标签防篡改，密钥存 `.tw_secret` 随机生成
**规则 S3（XSS）**: 前端 `he()` 转义所有用户输入（预览行/历史下拉/Data规则/Unit行）
**规则 S4（CSP）**: 安全响应头 X-Content-Type-Options/X-Frame-Options/Referrer-Policy/CSP
**规则 S5（速率限制）**: gnr 20/min, plan 30/min
**规则 S6（并发）**: 信号量限制同时执行
**规则 S7（原子写入）**: 临时文件+重命名
**规则 S8（authValue）**: 仅内存传递，localStorage 不存

### M9. 存储层（Storage）
- `test_cases.json` — 用例库
- `exec_history.json` — 执行历史（50条）
- `.ai_key.enc` — AI Key 加密存储
- `.tw_secret` — 加密密钥
- `generated_tests/` — 测试代码（20个保留）

### M10. 企业级靶机（mock_ecommerce）
**规则 M1**: JWT 登录（PBKDF2 哈希验证，盐:hash 格式）
**规则 M2**: 三级角色 admin/operator/viewer
**规则 M3**: 订单状态机 created→confirmed→paid→shipped→delivered（+cancelled）
**规则 M4**: 创建订单扣库存；取消订单退库存；退款批准退库存（仅 paid/shipped）
**规则 M5**: cancel_order 所有权检查（非 owner 非 admin 403）
**规则 M6**: 退款金额 0<amount≤订单总额

---

## 三、模块间关系与数据流

```
                ┌────────────────────────────────────┐
                │          用户输入层                 │
                │  URL + APIs + Pages + Rules + PRD  │
                └──────────┬─────────────────────────┘
                           │
              ┌────────────▼────────────┐
              │   M3 业务上下文分析      │──→ _ctx {entities, rules, state_machine}
              └────────────┬────────────┘
                           │ 注入
              ┌────────────▼────────────┐
              │   M2 AI 用例生成        │──→ cases[] (经 M2 筛查规则A5)
              └────────────┬────────────┘
                           │ exact 模式
              ┌────────────▼────────────┐
              │   M4 7层矩阵 _layered   │──→ extra cases (L1-L7)
              └────────────┬────────────┘
                           │ 合并
              ┌────────────▼────────────┐
              │   M5 gen_code           │──→ 4个测试文件 + conftest
              └────────────┬────────────┘
                           │ subprocess pytest
              ┌────────────▼────────────┐
              │   M6 执行引擎           │──→ SSE 实时流 (暂停/继续/停止)
              └────────────┬────────────┘
                           │ results.xml
              ┌────────────▼────────────┐
              │   M7 报告层             │──→ 仪表盘 + 趋势 + 可上线判断
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │   M9 存储层             │──→ 历史/用例库持久化
              └─────────────────────────┘

横切关注点: M8 安全层贯穿所有模块
```

**关键依赖**:
- M2 依赖 M3 的 `_ctx`（上下文注入 prompt）
- M4 依赖 M3 的 entities/rules/state_machine
- M5 依赖 M2 的 cases（exact 模式）+ M4 的 layered cases
- M6 依赖 M5 的测试代码
- M7 依赖 M6 的 results.xml + tally 计数器

---

## 四、关键规则冲突与优先级

| 冲突场景 | 规则 | 裁决 |
|---------|------|------|
| AI 用例 vs 模板用例 | A2 用户要 AI-only | AI 失败直接 error，不回退 |
| 暂停 vs 超时 | E2 vs E4 | 暂停不杀进程；超时（运行态10min）杀 |
| 方法限制 vs 模板 | W2(仅GET/POST) vs 模板含PUT/DELETE | 模板是演示数据不强制；生成时筛查剔除 |
| 推理模型流式 vs 用户体验 | A3 | 非流式等完整回答（300s），不做假流式 |
| 路径不匹配 | A5 | 打标记保留，不剔除（AI 可能更了解业务） |

---

## 五、已知待办

1. **UI 行计数**：`pgs.length*7` 应为 `*6`（每页 6 个 UI 测试）
2. **API 分区头**：无条数显示
3. **fallback 渲染路径**：缺 API/Data 分区头
4. **非流式响应**：`reasoning_content` 未读取（推理模型若把答案放该字段会失败）
5. **JSON 解析**：花括号深度计数在字符串内花括号场景会失效（建议 json.JSONDecoder().raw_decode）
6. **mock_server.py**：与 mock_ecommerce 重复，未删除
7. **_gen_hashes.py / tc_manager.html**：死文件待清理

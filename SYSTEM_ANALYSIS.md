# 测试工坊 Pro — 精准系统分析

> 生成：2026-08-13 | main.py 2501 行 / index.html 1297 行 / mock_ecommerce 17 文件

---

## 一、端点全景（25 个，含精确行号）

### 1.1 执行类

| # | 端点 | 方法 | 行 | 限流 | 行为 |
|---|------|------|----|----|------|
| 1 | `/api/plan` | POST | 987 | 30/min | 校验 body ≤50000 字符 → `PLANS[pid]=body` → 返回 8位pid |
| 2 | `/api/stream?id=` | GET | 1035 | 无 | plan 不存在→error；进程在跑→`_attach_existing` 重连；否则 `gen_code`→`_run_stream` |
| 3 | `/api/gnr` | POST | 944 | 20/min | **同步执行**：gen_code→pytest(300s超时)→XML解析→存历史→返回JSON |
| 4 | `/api/stop?sid=` | POST | 1007 | 无 | 杀进程+清 RUN_PROCS/RUN_QUEUES/RUN_TALLIES/PLANS；sid空则全清 |

### 1.2 AI 类

| # | 端点 | 方法 | 行 | 行为 |
|---|------|------|----|------|
| 5 | `/api/ai-suggest` | POST | 1600 | **同步 JSON 返回**（非流式），`_call_llm`+`_validate_cases` |
| 6 | `/api/ai-suggest-stream` | POST | 1684 | **SSE 流式**：info→clear→case×N→done |
| 7 | `/api/analyze-context` | POST | 1791 | PRD 文本→AI/启发式→entities/relations/state_machine/business_rules |
| 8 | `/api/ai-key` | POST | 1523 | key<8字符拒绝；空值清除+删文件；有效则 AES 加密落盘 `.ai_key.enc` |
| 9 | `/api/ai-key-status` | GET | 1506 | 返回 configured/valid/hint/source |

### 1.3 PRD 类

| # | 端点 | 方法 | 行 | 行为 |
|---|------|------|----|------|
| 10 | `/api/prd-list` | GET | 1821 | 扫描 mock_ecommerce/docs/*.md 返回文件名列表 |
| 11 | `/api/prd-load?file=` | GET | 1834 | 防穿越检查 `..`/`/`→读文件内容 |

### 1.4 报告类

| # | 端点 | 方法 | 行 | 行为 |
|---|------|------|----|------|
| 12 | `/api/report-count` | GET | 1205 | 最新 XML 摘要，**passed = t-f-e-s**（已修skipped） |
| 13 | `/api/report?dir=` | GET | 1267 | HTML 报告页 `_build_report` |
| 14 | `/api/report-list` | GET | 1234 | 所有报告目录列表 |

### 1.5 历史类

| # | 端点 | 方法 | 行 | 行为 |
|---|------|------|----|------|
| 15 | `/api/history` | GET | 881 | HTML 表格 |
| 16 | `/api/history-data` | GET | 845 | JSON + trend(10次) + streak + ready(streak≥3) |
| 17 | `/api/history/{idx}` | DELETE | 930 | 删除单条 |
| 18 | `/api/audit-export` | GET | 864 | 合规导出：执行历史+用例库 JSON |

### 1.6 用例库类

| # | 端点 | 方法 | 行 | 行为 |
|---|------|------|----|------|
| 19 | `/api/tc` | GET | 1469 | 全量返回 |
| 20 | `/api/tc` | POST | 1473 | 字段截断[:100]→append→save |
| 21 | `/api/tc/{cid}` | PUT | 2256 | **无类型校验**（已知问题） |
| 22 | `/api/tc/{cid}` | DELETE | 2269 | 删除 |
| 23 | `/api/save-tc` | POST | 1496 | 计划→批量存用例库（save_auto_tcs） |

### 1.7 其他

| # | 端点 | 方法 | 行 | 行为 |
|---|------|------|----|------|
| 24 | `/ci` | GET | 2368 | CI 控制台页面 |
| 25 | `/api/ci-trigger` | POST | 2377 | GitHub Actions 触发 |
| 26 | `/api/ci-status` | GET | 2394 | 最近5次 workflow runs |
| 27 | `/` | GET | 2412 | 主页面 |

---

## 二、函数清单（30 个，含行号）

### 2.1 安全与基础设施

| 函数 | 行 | 职责 |
|------|----|------|
| `SecurityHeadersMiddleware` | 34 | CSP/X-Frame/XSS-Protection/Referrer 响应头 |
| `_encrypt_key` | 73 | AES 流加密：随机IV+HMAC-SHA256 流+认证标签 |
| `_decrypt_key` | 89 | 先验认证标签（compare_digest）再解密，失败抛 ValueError |
| `_check_rate` | 127 | 滑动窗口：过期剔除→≥max_req拒绝→append→>5000键清理 |
| `startup_check` | 143 | 依赖检查 httpx/pytest + pytest --version |
| `_cleanup_procs` | 161 | 关停时 terminate+wait(5s) 所有进程 |
| `is_safe_url` | 179 | SSRF：file/ftp/gopher拒绝；localhost/.local/.internal拒绝；进程内DNS解析；私有/回环/链路本地/保留/多播拒绝；169.254.169.254拒绝；127.0.0.1:8000白名单 |
| `safe` | 209 | 标识符净化：保留\w+CJK，防..穿越 |
| `safe_path` | 217 | 路径净化：允许/{}?=&，补前导/ |

### 2.2 测试生成

| 函数 | 行 | 职责 |
|------|----|------|
| `_exact_test` | 231 | 标题关键词→(test名,语句,断言) 三元组，15 个关键词规则 |
| `_layered_tests` | 314 | L1-L7 矩阵用例生成 |
| `gen_code` | 420 | plan→5个测试文件+conftest |
| `_validate_cases` | 1639 | AI 用例筛查（6项规则） |
| `_call_llm` | 1969 | 非流式 LLM 调用+三层JSON解析容错 |
| `_pattern_suggest` | 2054 | 模板兜底用例（已被AI-only策略闲置） |
| `_analyze_with_ai` | 1847 | PRD→结构化上下文（AI） |
| `_analyze_with_heuristic` | 1891 | PRD→结构化上下文（正则启发式） |

### 2.3 执行引擎

| 函数 | 行 | 职责 |
|------|----|------|
| `_run_stream` | 1124 | 新进程+SSE流，断开不杀进程（暂停语义） |
| `_attach_existing` | 1068 | 重连持久队列续读 |
| `save_plan` | 987 | plan存储 |

### 2.4 存储与报告

| 函数 | 行 | 职责 |
|------|----|------|
| `load_hist`/`save_hist_entry` | 817/837 | 历史读写（50条上限） |
| `_atomic_write` | 830 | 临时文件+os.replace |
| `load_tc`/`save_tc` | 1452/1465 | 用例库读写 |
| `save_auto_tcs` | 2276 | 执行后自动存用例库（title去重，1000→截500） |
| `update_tc_status` | 2332 | 按XML结果更新用例状态 |
| `_build_report` | 1276 | HTML报告 |
| `report_count` | 1205 | 摘要统计 |

---

## 三、`_exact_test` 关键词规则全表（15 条）

| 顺序 | 关键词（title.lower() 子串匹配） | 生成 | 断言 |
|-----|-------------------------------|------|------|
| 1 | sql/sqli/注入/injection | GET?q='OR'1'='1 | `<500` |
| 2 | xss/脚本/script/cross | ?q=<script>alert(1) | `>=400 或 "<script>" not in text` |
| 3 | 缺少/必填/缺失/空/empty | POST 空体 | `400/422/401` |
| 4 | 未认证/未授权/无权限/unauth/token/forbidden | 空 Authorization 头 | `401/403` |
| 5 | 不存在/404/not found/找不到 | 裸请求 | `404/400` |
| 6 | 无效/非法/invalid/格式/bad | 非法邮箱 payload | `400/422` |
| 7 | 重复/dup/冲突/already | 重复字段 payload | `400/409` |
| 8 | 过短/short/超长/long/过长/溢出 | 1000字符 name | `400/422 或 <500` |
| 9 | 创建/create/新增/add/注册 | 实体字段 payload | `200/201` |
| 10 | 更新/update/修改/edit/replace | 更新 payload | `200/201/204` |
| 11 | 删除/delete/remove | 裸请求 | `200/204` |
| 12 | 详情/detail/单个/id/查看/获取 | 裸请求 | `200/404` |
| 13 | 分页/page/limit/列表/list/查询/query | GET?page=1&limit=10 | `200` |
| 14 | 登录/login/auth | admin/Admin@123 | `200/201` |
| 15 | 健康/health/状态/status/ping | 裸请求 | `200` |
| 兜底 | 无匹配 | POST 带 {"test":"value"} / 裸请求 | `<500` |

**规则**：
- 安全类(1-2)与错误类(3-8)优先于正常类(9-15)
- 实体字段 f0-f3 从上下文提取，兜底 username/email/role/password
- GET/HEAD/OPTIONS 不带 json body；DELETE 也不带（更新除外）
- 方法仅 GET/POST（VALID_METHODS 限制）

---

## 四、7 层矩阵精确规则（_layered_tests）

| 层 | 触发条件 | 精确生成逻辑 | 断言 |
|----|---------|-------------|------|
| L1 | 有 ctx 即生成 | 每 API 一条 `可达性-{path_id}` | `<500` |
| L2 | 实体 fields 非空 且 GET | `契约校验-{ename}({n}字段)` | walrus: `isinstance((d:=...), list) and len(d)>0 and all(k in d[0] for k in [fields])` |
| L3 | 规则关键词匹配 | 见下表 6 类 | 见下表 |
| L4 | state_machine 非空 | 序列测试（create_ep→list_ep） | `<500`（弱，待增强） |
| L5 | ≥2 API | 订单金额=Σ(quantity×unit_price) | 差值<0.02 |
| L6 | 每 API | 剥认证头裸客户端 | **必须 401/403** |
| L7 | 每 API | ThreadPoolExecutor(10) | 全部 `<500` |

### L3 规则关键词 → payload/断言

| 关键词 | payload | 断言 |
|--------|---------|------|
| 金额/amount/price/价格/库存/stock/>=0/非负/不能为负/必须>0 | {"amount":-1,"stock":-5} | 400/422 |
| 唯一/unique/重复/已存在 | {f0:"dup-test-001"} | 200/201/400/409 |
| 管理员/admin/权限/普通用户/无权/只能看/越权 | 无 | 200/401/403 |
| 不可取消/only created/不能取消/不允许/之后不可 | DELETE /999999 | 400/404 |
| 必填/required/不能为空/not null/缺少 | {"name":""} | 400/422 |
| 超过/不能超过/exceed/上限/最多 | {"amount":99999999} | 400/422 |
| 必须/must/shall/应/自动/auto | 无 | <500 |

---

## 五、执行引擎状态机（精确）

```
状态: [新建] [运行中] [已暂停] [完成] [已停止]

[新建] —POST /api/plan(30/min,≤50KB)→ PLANS[pid]=plan
[新建] —GET /api/stream→ gen_code → _run_stream:
        Popen(pytest -v --tb=line --color=no --junitxml=results.xml)
        RUN_PROCS[pid]=proc; RUN_QUEUES[pid]=Queue(); RUN_TALLIES[pid]=[0,0,0,0]
        读线程: proc.stdout.readline → q.put(line) → 终止后 q.put("__END__")
[运行中] —客户端断开(request.is_disconnected())→ break（不杀进程）
[已暂停] —GET /api/stream→ RUN_PROCS[pid] 存活 → _attach_existing:
        复用 RUN_QUEUES[pid] 续读（断线期间输出不丢）
        复用 RUN_TALLIES[pid] 计数不重复
[运行中/已暂停] —POST /api/stop→ proc.terminate()+kill → 清4个dict
[运行中/已暂停] —q.get("__END__")→ save_hist_entry+save_auto_tcs+update_tc_status
        → 清4个dict → SSE done(total,passed,failed,errors,rate)
[运行中] —10分钟无输出→ kill+error
```

**关键差异**：
- 流式(stream): `--tb=line`，实时 SSE，支持暂停
- 同步(gnr): `--tb=short`，capture_output，300s 硬超时，返回 JSON

**计数器规则**：`"PASSED" in st and "::" in st` 判通过（含进度行格式）；`[N%]` 正则提取百分比

---

## 六、AI 生成流程（精确失败模式）

```
POST /api/ai-suggest-stream
├─ is_safe_url(base_url) 失败 → error "AI Base URL 被拒绝"
├─ Key 校验失败(空/短/前缀) → error "未配置AI Key"
├─ LLM 非流式调用 (timeout=300, max_tokens=max(配置,16000))
│   ├─ HTTP≠200 → error "AI API {code}"
│   ├─ content 解析出 0 个 JSON → error "AI 未产出有效用例(返回N字符: 片段)"
│   ├─ _validate_cases 全剔除 → error "AI 用例全部未通过筛查"
│   └─ 通过 → clear → case×N → done (含"筛查剔除N条"信息)
└─ 任何异常 → error "AI异常({type})"
```

**筛查规则（_validate_cases）**：
1. 方法 ∈ {GET,POST}
2. 路径 / 或 http 开头
3. 优先级归一化 P0/P1/P2
4. title 必填≤200
5. 方法+路径+标题去重
6. 路径不匹配配置 → `_path_mismatch` 标记（不剔除）

---

## 七、数据模式

### 7.1 plan（提交计划）
```json
{
  "name": str, "url": str, "apis": [{"m":"GET|POST","p":"/api/x","n":"说明"}],
  "pages": [{"u":"/","na":"名称"}], "rules": [str],
  "types": ["api","ui","data","unit"], "exact": bool,
  "auth": "none|bearer|basic|header", "authValue": str(仅内存),
  "context": {"entities":[], "business_rules":[], "state_machine":[]},
  "_dir": str(内部: 生成目录)
}
```

### 7.2 用例（test_cases.json）
```json
{"id":"001","module":"电商系统","title":"...","priority":"P1",
 "method":"GET","path":"/api/x","expected":"...","steps":"...",
 "status":"待执行|通过|失败","created":"YYYY-MM-DD HH:MM"}
```

### 7.3 历史条目（exec_history.json）
```json
{"name":str,"url":str,"total":int,"passed":int,"failed":int,"errors":int,
 "rate":float,"time":"YYYY-MM-DD HH:MM:SS","dir":str}
```

---

## 八、前端函数全景（52 个）

### 8.1 向导模块
`toggleAuth`(348) `tab`(352) `initTpls`(362) `apply`(367) `addApi`(383) `quickTest`(392) `addPg`(406) `save`(416) `restore`(422) `fixUrl`(438) `validateURL`(446)

### 8.2 执行模块
`_runWithConfirm`(458) `generate`(468) `_streamSSE`(526) `_setRunButtons`(573) `pauseExec`(581) `resumeExec`(589) `stopExec`(601) `loadHist`(612) `delExec`(639) `execHist`(641) `_runGenerate`(907)

### 8.3 预览模块
`previewCases`(718) `toggleAllLocks`(837) `togglePreviewAll`(851) `toggleLock`(855) `execPreviewed`(870) `savePreviewed`(928) `saveToTC`(944) `loadTCs`(956) `renderTCList`(965) `importSelectedTCs`(979)

### 8.4 上下文模块
`initPRDList`(1008) `loadPRDFile`(1019) `uploadPRD`(1031) `loadAllPRDs`(1048) `renderContext`(1066) `editContext`(1118) `updateContext`(1125) `analyzeContext`(1131)

### 8.5 AI 配置模块
`loadAIProfiles`(1173) `saveAIProfiles`(1194) `renderAIList`(1195) `newAIConfig`(1216) `selectAIProfile`(1221) `deleteAIConfig`(1242) `toggleAIKeyVisibility`(1250) `onAIProviderChange`(1255) `saveAIConfig`(1260)

### 8.6 工具
`he`(285) HTML转义

---

## 九、数据流依赖图

```
fixUrl ──→ plan.url ──→ gen_code ──→ conftest.B
_ctx ──┬──→ _call_llm prompt（业务规则注入）
       ├──→ _layered_tests（L2实体字段/L3规则/L4状态机）
       └──→ _exact_test（实体字段名 f0-f3）
AI cases ──→ _validate_cases ──→ exact模式 plan.apis
layered cases ──→ gen_code 追加（L1-L7）
gen_code ──→ test_api/ui/data/unit.py + conftest(auth_token fixture)
pytest ──→ results.xml ──┬──→ report_count/report
                         ├──→ update_tc_status
                         └──→ save_hist_entry
authValue ──→ auth_env(TW_AUTH_HEADER) ──→ conftest 环境变量（不落盘）
```

---

## 十、已知缺陷清单（精确行号）

| # | 严重 | 位置 | 问题 |
|---|------|------|------|
| 1 | HIGH | main.py:968 | gnr 的 `p = t - f - e` **未减 skipped**（report_count 已修，gnr 漏修） |
| 2 | HIGH | main.py:1697-1708 | JSON 花括号深度计数在字符串值含 `{}` 时失效 |
| 3 | MED | main.py:1689 | 非流式响应只读 message.content，未读 reasoning_content |
| 4 | MED | main.py:2256 | PUT /api/tc/{cid} 无类型校验 |
| 5 | LOW | index.html:782 | UI 计数 `pgs.length*7` 应为 `*6` |
| 6 | LOW | index.html:769 | API 分区头无条数 |
| 7 | LOW | index.html:823-830 | fallback 渲染缺 API/Data 分区头 |
| 8 | LOW | main.py:154 | startup_check subprocess 无 timeout |
| 9 | LOW | 死文件 | mock_server.py / _gen_hashes.py / tc_manager.html |
| 10 | LOW | main.py:301 | 登录用例硬编码 admin/Admin@123（对非电商系统会误判） |
| 11 | INFO | main.py:1722 | 暂停态无超时：进程跑完自然结束，但若挂起无人重连则残留（stop 可清） |

# 测试工坊 Pro — 完整系统档案

> 最后更新：2026-08-13 23:20 | main.py / static/index.html / mock_ecommerce/
> 本文档整合：架构全景、27 端点、30 函数、15 关键词规则、7 层矩阵、状态机、数据模式、缺陷清单（含修复状态）

---

## 一、架构全景

```
浏览器(localhost:9000)
├── Wizard 向导(5步) · Exec 执行面板 · AI 配置面板 · /tc 用例 · /ci CI控制台
│
main.py (FastAPI, ~2500行)
├── AI生成层    _call_llm · _validate_cases · ai-suggest(-stream)
├── 7层矩阵层   _layered_tests (L1-L7)
├── 代码生成层  gen_code · _exact_test (15关键词规则)
├── 执行引擎层  _run_stream · _attach_existing (暂停/继续/停止)
├── 上下文层    analyze-context · _analyze_with_ai · _analyze_with_heuristic
├── 安全层      is_safe_url · _encrypt_key · SecurityHeadersMiddleware · _check_rate
├── 存储层      load_hist · save_hist_entry · load_tc · save_tc · _atomic_write
├── 报告层      report · report-count · report-list · audit-export
└── CLI/CI层    argparse(--run-config/--port/--output-format) · ci-trigger

mock_ecommerce/ (端口8000, 靶机)
├── JWT登录(PBKDF2验证) · 三级角色 · 商品CRUD · 订单状态机 · 退款流程 · SPA前端
└── docs/ 6份PRD (电商3 + 百度3)
```

---

## 二、端点全表（27 个）

| # | 端点 | 方法 | 限流 | 行为 |
|---|------|------|------|------|
| 1 | `/api/plan` | POST | 30/min | body≤50KB → PLANS[pid] → 返回8位pid |
| 2 | `/api/stream?id=` | GET | 无 | plan不存在→error；进程存活→_attach_existing重连；否则gen_code→_run_stream |
| 3 | `/api/gnr` | POST | 20/min | 同步执行：gen_code→pytest(300s)→XML→历史→JSON返回 |
| 4 | `/api/stop?sid=` | POST | 无 | 杀进程+清RUN_PROCS/RUN_QUEUES/RUN_TALLIES/PLANS；sid空全清 |
| 5 | `/api/ai-suggest` | POST | 无 | 同步JSON：_call_llm+_validate_cases |
| 6 | `/api/ai-suggest-stream` | POST | 无 | SSE流：info→clear→case×N→done |
| 7 | `/api/analyze-context` | POST | 无 | PRD文本→AI/启发式→entities/relations/state_machine/business_rules |
| 8 | `/api/ai-key` | POST | 无 | key<8拒；空清除+删文件；有效AES加密落盘 |
| 9 | `/api/ai-key-status` | GET | 无 | configured/valid/hint/source |
| 10 | `/api/prd-list` | GET | 无 | 扫描mock_ecommerce/docs/*.md |
| 11 | `/api/prd-load?file=` | GET | 无 | 防穿越(..//)→读文件 |
| 12 | `/api/report-count` | GET | 无 | 最新XML摘要 passed=t-f-e-s ✅已修 |
| 13 | `/api/report?dir=` | GET | 无 | HTML报告 |
| 14 | `/api/report-list` | GET | 无 | 报告目录列表 |
| 15 | `/api/history` | GET | 无 | HTML表格 |
| 16 | `/api/history-data` | GET | 无 | JSON+trend(10次)+streak+ready(≥3) |
| 17 | `/api/history/{idx}` | DELETE | 无 | 删单条 |
| 18 | `/api/audit-export` | GET | 无 | 合规导出JSON |
| 19 | `/api/tc` | GET | 无 | 全量 |
| 20 | `/api/tc` | POST | 无 | 截断[:100]→append |
| 21 | `/api/tc/{cid}` | PUT | 无 | ✅已修：priority枚举+method枚举+截断500 |
| 22 | `/api/tc/{cid}` | DELETE | 无 | 删除 |
| 23 | `/api/save-tc` | POST | 无 | 计划→批量存用例库 |
| 24 | `/ci` | GET | 无 | CI控制台页 |
| 25 | `/api/ci-trigger` | POST | 无 | GitHub Actions触发 |
| 26 | `/api/ci-status` | GET | 无 | 最近5次workflow |
| 27 | `/` | GET | 无 | 主页面 |

---

## 三、函数清单（30 个）

| 函数 | 行 | 职责 |
|------|----|------|
| SecurityHeadersMiddleware | 34 | 安全响应头 |
| _encrypt_key | 73 | AES流加密+HMAC标签 |
| _decrypt_key | 89 | 验标签→解密 |
| _check_rate | 127 | 滑动窗口限流 |
| startup_check | 143 | 依赖检查 ✅已加15s超时 |
| _cleanup_procs | 161 | 关停清理 |
| is_safe_url | 179 | SSRF防护 |
| safe | 209 | 标识符净化 |
| safe_path | 217 | 路径净化 |
| _exact_test | 231 | 标题→测试三元组(15规则) |
| _layered_tests | 314 | L1-L7矩阵 |
| gen_code | 420 | plan→5测试文件 |
| load_hist / save_hist_entry | 817/837 | 历史读写 |
| _atomic_write | 830 | 临时文件+replace |
| _check_rate调用点 | — | gnr:20/min, plan:30/min |
| list_history_json | 846 | 历史JSON+趋势 |
| audit_export | 865 | 合规导出 |
| del_history | 931 | 删历史 |
| gnr | 945 | 同步执行 ✅已修skipped |
| save_plan | 988 | plan存储 |
| stop_exec | 1008 | 停止执行 |
| stream | 1036 | SSE流入口 |
| _attach_existing | 1068 | 重连续读 ✅已修历史保存 |
| _run_stream | 1124 | 新进程SSE ✅暂停不杀进程 |
| report_count | 1206 | 摘要 ✅已修skipped |
| report_list | 1235 | 报告列表 |
| _build_report | 1276 | HTML报告 |
| load_tc / save_tc | 1452/1465 | 用例库读写 |
| add_tc | 1474 | 添加用例 |
| save_plan_to_tc | 1497 | 批量存用例 |
| ai_key_status | 1507 | Key状态 |
| set_ai_key | 1524 | 设置/清除Key |
| ai_suggest | 1601 | 同步AI建议 |
| _validate_cases | 1639 | 用例筛查 |
| ai_suggest_stream | 1685 | 流式AI建议 |
| analyze_context | 1792 | 上下文分析 |
| list_prds / load_prd | 1822/1835 | PRD读写 |
| _analyze_with_ai | 1847 | AI上下文分析 |
| _analyze_with_heuristic | 1891 | 启发式分析 |
| _call_llm | 1969 | LLM调用 ✅已修raw_decode+reasoning |
| _pattern_suggest | 2054 | 模板兜底(已闲置) |
| upd_tc | 2257 | ✅已修校验 |
| del_tc | 2270 | 删用例 |
| save_auto_tcs | 2276 | 自动存用例库 |
| update_tc_status | 2332 | 状态更新 |
| ci_page / ci_trigger / ci_status | 2369/2378/2395 | CI功能 |
| index | 2413 | 主页 |

---

## 四、`_exact_test` 15 条关键词规则

**顺序：安全(1-2) > 错误(3-8) > 正常(9-15) > 兜底**

| # | 关键词 | 生成语句 | 断言 |
|---|--------|---------|------|
| 1 | sql/sqli/注入/injection | GET?q='OR'1'='1 | <500 ✅已修恒真式 |
| 2 | xss/脚本/script/cross | ?q=<script>alert(1) | ≥400 或 "<script>" not in text |
| 3 | 缺少/必填/缺失/空/empty | POST空体 | 400/422/401 |
| 4 | 未认证/未授权/无权限/unauth/token/forbidden | 空Authorization头 | 401/403 |
| 5 | 不存在/404/not found/找不到 | 裸请求 | 404/400 |
| 6 | 无效/非法/invalid/格式/bad | 非法email | 400/422 |
| 7 | 重复/dup/冲突/already | 重复字段 | 400/409 |
| 8 | 过短/short/超长/long/过长/溢出 | 1000字符 | 400/422 或 <500 |
| 9 | 创建/create/新增/add/注册 | 实体字段payload | 200/201 |
| 10 | 更新/update/修改/edit/replace | 更新payload | 200/201/204 |
| 11 | 删除/delete/remove | 裸请求 | 200/204 |
| 12 | 详情/detail/单个/id/查看/获取 | 裸请求 | 200/404 |
| 13 | 分页/page/limit/列表/list/查询/query | GET?page=1&limit=10 | 200 |
| 14 | 登录/login/auth | ✅env驱动: TW_LOGIN_USER/PASS | 200/201 |
| 15 | 健康/health/状态/status/ping | 裸请求 | 200 |
| 兜底 | 无匹配 | POST{"test":"value"}或裸 | <500 |

**约束**：实体字段f0-f3取自上下文(兜底username/email/role/password)；GET/HEAD/OPTIONS/DELETE不带json body；方法仅GET/POST。

---

## 五、7 层矩阵

| 层 | 触发 | 断言 |
|----|------|------|
| L1 可达性 | 有ctx | <500 |
| L2 字段契约 | 实体fields+GET | walrus: all(k in d[0] for k in [fields]) ✅已修真检查 |
| L3 业务规则 | 关键词7类 | 见下表 |
| L4 状态机 | state_machine非空 | 序列(create→verify) <500 |
| L5 数据完整性 | ≥2API | 订单金额差<0.02 |
| L6 安全注入 | 每端点 | 剥认证头→必须401/403 ✅已修 |
| L7 边界并发 | 每端点 | ThreadPoolExecutor(10)全<500 ✅已修真并发 |

### L3 规则映射

| 关键词 | payload | 断言 |
|--------|---------|------|
| 金额/price/stock/>=0/非负/不能为负/必须>0 | {"amount":-1,"stock":-5} | 400/422 |
| 唯一/unique/重复/已存在 | {f0:"dup-test-001"} | 200/201/400/409 |
| admin/权限/无权/越权 | 无 | 200/401/403 |
| 不可取消/不允许/之后不可 | DELETE/999999 | 400/404 |
| 必填/required/not null | {"name":""} | 400/422 |
| 超过/上限/最多 | {"amount":99999999} | 400/422 |
| 必须/must/自动 | 无 | <500 |

---

## 六、执行引擎状态机

```
[新建] --POST /api/plan(30/min,≤50KB)--> PLANS[pid]
[新建] --GET /api/stream--> gen_code --> _run_stream:
    Popen(pytest -v --tb=line --junitxml)
    RUN_PROCS[pid] / RUN_QUEUES[pid] / RUN_TALLIES[pid]=[0,0,0,0]
    读线程: readline→q.put → 结束→q.put("__END__")
[运行中] --客户端断开--> break（✅不杀进程）
[已暂停] --GET /api/stream--> _attach_existing:
    复用RUN_QUEUES续读 + RUN_TALLIES续计数 ✅已修
[任意] --POST /api/stop--> terminate+kill + 清4 dict
[任意] --q.get("__END__")--> save_hist_entry+save_auto_tcs+update_tc_status
    → 清4 dict → SSE done(total,passed,failed,errors,rate)
[运行中] --10min超时--> kill+error
```

**计数器**：`"PASSED" in st and "::" in st`；`[N%]`正则取进度。
**流式vs同步**：stream用--tb=line实时SSE可暂停；gnr用--tb=short capture_output 300s硬超时。

---

## 七、AI 生成失败模式（6 种）

1. base_url 不安全 → `AI Base URL 被拒绝`
2. Key 空/短/前缀错 → `未配置AI Key`
3. HTTP≠200 → `AI API {code}`
4. content 解析0个JSON → `AI 未产出有效用例(返回N字符:片段)`
5. 筛查全剔除 → `AI 用例全部未通过筛查`
6. 异常 → `AI异常({type})`

**筛查规则(_validate_cases)**：
- 方法 ∈ {GET,POST}
- 路径 / 或 http 开头
- priority 归一化 P0/P1/P2
- title 必填≤200
- 方法+路径+标题去重
- 路径不匹配→`_path_mismatch`标记不剔除

**推理模型策略**：deepseek-v4-pro 流式返回 reasoning_content 先于 content，改用非流式(300s)等完整回答；content 空时兜底读 reasoning_content ✅已修；解析用 JSONDecoder.raw_decode ✅已修。

---

## 八、数据模式

```json
// plan
{"name":str, "url":str, "apis":[{"m":"GET|POST","p":"/api/x","n":"说明"}],
 "pages":[{"u":"/","na":"名称"}], "rules":[str],
 "types":["api","ui","data","unit"], "exact":bool,
 "auth":"none|bearer|basic|header", "authValue":str(仅内存),
 "context":{"entities":[],"business_rules":[],"state_machine":[]},
 "_dir":str(内部)}

// test_case
{"id":"001","module":"","title":"","priority":"P1","method":"GET","path":"","expected":"","steps":"","status":"待执行","created":""}

// history_entry
{"name":"","url":"","total":0,"passed":0,"failed":0,"errors":0,"rate":0,"time":"","dir":""}
```

---

## 九、前端函数（52 个）

**向导**：toggleAuth(348) tab(352) initTpls(362) apply(367) addApi(383) quickTest(392) addPg(406) save(416) restore(422) fixUrl(438) validateURL(446)
**执行**：_runWithConfirm(458) generate(468) _streamSSE(526) _setRunButtons(573) pauseExec(581) resumeExec(589) stopExec(601) loadHist(612) delExec(639) execHist(641) _runGenerate(907)
**预览**：previewCases(718) toggleAllLocks(837) togglePreviewAll(851) toggleLock(855) execPreviewed(870) savePreviewed(928) saveToTC(944) loadTCs(956) renderTCList(965) importSelectedTCs(979)
**上下文**：initPRDList(1008) loadPRDFile(1019) uploadPRD(1031) loadAllPRDs(1048) renderContext(1066) editContext(1118) updateContext(1125) analyzeContext(1131)
**AI配置**：loadAIProfiles(1173) saveAIProfiles(1194) renderAIList(1195) newAIConfig(1216) selectAIProfile(1221) deleteAIConfig(1242) toggleAIKeyVisibility(1250) onAIProviderChange(1255) saveAIConfig(1260)
**工具**：he(285)

---

## 十、安全规则

| # | 规则 |
|---|------|
| S1 | SSRF：is_safe_url 进程内DNS，拒私有/回环/链路本地/保留/多播/169.254.169.254；127.0.0.1:8000白名单 |
| S2 | AI Key：PBKDF2-SHA256(10万轮)+HMAC标签；密钥.tw_secret随机生成 |
| S3 | XSS：he()全量转义（预览/历史/Data/Unit/fallback ✅全修） |
| S4 | 响应头：CSP/X-Content-Type-Options/X-Frame-Options/Referrer-Policy |
| S5 | 限流：gnr 20/min，plan 30/min |
| S6 | 并发：信号量 |
| S7 | 原子写入：临时文件+replace |
| S8 | authValue：仅内存，localStorage不存 |

---

## 十一、缺陷清单（含修复状态）

| # | 严重 | 位置 | 问题 | 状态 |
|---|------|------|------|------|
| 1 | HIGH | main.py:968 | gnr passed未减skipped | ✅已修 |
| 2 | HIGH | JSON解析 | 花括号深度计数失效 | ✅raw_decode |
| 3 | MED | 非流式响应 | 未读reasoning_content | ✅已修 |
| 4 | MED | PUT /api/tc | 无类型校验 | ✅已修 |
| 5 | LOW | UI计数 | *7应为*6 | ✅已修 |
| 6 | LOW | API分区头 | 无条数 | ✅已修 |
| 7 | LOW | fallback渲染 | 缺Data分区+未转义 | ✅已修 |
| 8 | LOW | startup_check | 无超时 | ✅15s |
| 9 | LOW | 死文件 | mock_server.py/tc_manager.html | ✅已删 |
| 10 | LOW | 登录凭证 | 硬编码 | ✅env驱动 |
| 11 | INFO | 暂停态 | 无超时（进程自然结束） | ⏸设计如此 |
| 12 | NEW | 运行时数据 | exec_history/test_cases入库 | ✅已untrack |

---

## 十三、按钮功能全表（含行号与处理器）

### 13.1 index.html 向导页

| 按钮 | 行 | 处理器 | 行为 |
|------|----|--------|------|
| 新建方案/执行/AI配置 | 44/45/50 | `tab(t)` | 切换三个面板，高亮当前 |
| + 添加接口 | 87 | `addApi()` | 新增 API 行（GET/POST 下拉+路径+说明+▶快测+删除） |
| 从用例库导入 | 88 | `loadTCs()` | 打开 tc-modal 弹窗 |
| 弹窗关闭 × | 96 | 内联 | 隐藏 tc-modal |
| 导入所选用例 | 100 | `importSelectedTCs()` | 勾选用例写入向导 API 表 |
| + 添加页面 | 110 | `addPg()` | 新增页面行（路径+名称+浏览器） |
| 📚 全部加载 | 127 | `loadAllPRDs()` | 拉取全部 PRD→textarea→自动 analyzeContext |
| AI 分析业务语义 | 129 | `analyzeContext()` | POST /api/analyze-context→渲染结果 |
| 取消 | 130 | `_cancelAnalyze()` | AbortController 中止分析 |
| 清除 | 131 | 内联 | 清空 textarea+_ctx+重渲染 |
| ✏ 编辑 | 138 | `editContext()` | window.open JSON 编辑弹窗 |
| 生成用例预览 | 157 | `previewCases()` | SSE 流式拉取 AI 用例+分区渲染 |
| 重新生成 | 166 | `previewCases()` | 重跑预览 |
| 执行选中 | 167 | `execPreviewed()` | 勾选用例→exact 模式执行 |
| 保存到用例库 | 168 | `savePreviewed()` | 预览用例→POST /api/save-tc |
| 🔒 表头 | 175 | `toggleAllLocks()` | 全锁定/全解锁 |
| 直接执行全部 | 193 | `_runWithConfirm()` | 生产URL警告确认→generate() |
| 新建配置 | 205 | `newAIConfig()` | AI profile 新建 |
| 保存配置 | 215 | `saveAIConfig()` | profile→localStorage ai_profiles |
| 删除配置 | 216 | `deleteAIConfig()` | 移除当前 profile |
| 显隐 Key | 240 | `toggleAIKeyVisibility()` | password input 切换 |
| 执行(历史) | 264 | `execHist()` | 历史方案→执行 |
| 模板按钮 | 364 | `apply(k,this)` | 模板→填充表单+_ctx+save |
| ▶ 快测 | 388 | `quickTest(this)` | 单端点快速执行 |
| × 删行 | 389/411 | 内联 | 删除行+save() |
| 停止/暂停按钮区 | 487/578/585/594/605 | pauseExec/resumeExec/stopExec | 三态控制 |
| 删除历史 | 635 | `delExec(i)` | DELETE /api/history/{idx} |
| 执行面板控制 | 668 | pauseExec/stopExec | dash 面板三态 |
| 保存并关闭(编辑弹窗) | 1135 | updateContext | JSON→_ctx→save |

### 13.2 index.html 预览区（动态生成）

| 按钮 | 处理器 | 行为 |
|------|--------|------|
| 全选框 | `togglePreviewAll()` | 勾选全部用例 |
| 🔓/🔒 每行锁 | `toggleLock(el,key)` | 单用例锁定（重生成保留） |

### 13.3 ci.html CI 控制台

| 按钮 | 行 | 处理器 | 行为 |
|------|----|--------|------|
| ▶ 执行 CI | 87 | `startCI()` | 三阶段：AI生成→路径筛选→执行，SSE 日志 |
| ⏹ 停止 | 88 | `stopCI()` | POST /api/stop+关SSE |
| 触发远程 CI | 113 | `triggerGitHubCI()` | POST /api/ci-trigger |
| 查看最近状态 | 114 | `checkGitHubCI()` | GET /api/ci-status 渲染5次runs |

### 13.4 tc.html 用例管理

| 按钮 | 行 | 处理器 | 行为 |
|------|----|--------|------|
| 执行选中 | 50 | `execSelected()` | 勾选用例执行 |
| 新增用例 | 51 | `openAdd()` | 打开表单 |
| 取消 | 86 | 内联 | 关闭表单 |
| 保存 | 87 | `saveTC()` | POST /api/tc |
| 模块筛选 | 133 | `filterModule(m)` | 按模块过滤 |
| 编辑 | 155 | `openEdit(id)` | 载入表单 |
| 删除 | 156 | `delTC(id)` | DELETE /api/tc/{cid} |

---

## 十四、数据流

```
fixUrl → plan.url → gen_code → conftest.B
_ctx ──┬→ _call_llm prompt(规则注入)
       ├→ _layered_tests(L2实体/L3规则/L4状态机)
       └→ _exact_test(实体字段f0-f3)
AI cases → _validate_cases → exact模式plan.apis
layered cases → gen_code追加(L1-L7)
gen_code → test_api/ui/data/unit.py + conftest(auth_token fixture)
pytest → results.xml ──┬→ report-count/report
                        ├→ update_tc_status
                        └→ save_hist_entry
authValue → auth_env(TW_AUTH_HEADER) → conftest环境变量(不落盘)
```

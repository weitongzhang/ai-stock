# FTShare-market-data 测试文档

## 目录结构

```
FTShare-market-data/
├── SKILL.md              # 主技能文档
├── run.py                # 统一调度入口
├── test_runner.py        # 测试运行器（本文档配套）
├── test_logs/            # 测试日志输出目录（自动创建）
│   ├── <subskill>_<timestamp>.json    # 每个接口的返回 JSON
│   └── summary_<timestamp>.txt        # 汇总报告
└── sub-skills/           # 各子 skill 实现
```

---

## 快速开始

### 运行全部测试

```bash
python3 test_runner.py
```

输出示例：

```
======================================================================
FTShare-market-data 子 skill 集成测试
用例总数: 47  跳过: 2  执行: 45
日志目录: /path/to/test_logs
======================================================================

[  1/47] PASS  get-nth-trade-date - 前5个交易日  (351ms)
         日志：test_logs/get-nth-trade-date_20260324_115213.json  (0.1 KB)
[  2/47] PASS  stock-list-all-stocks - 全量股票列表  (486ms)
         日志：test_logs/stock-list-all-stocks_20260324_115213.json  (245.3 KB)
...

======================================================================
结果汇总：PASS=45  FAIL=0  SKIP=2
总耗时：23.4s
汇总日志：test_logs/summary_20260324_115213.txt
======================================================================
```

---

## 使用方法

### 1. 按关键词过滤测试

只运行匹配关键词的用例（支持多个关键词，取并集）：

```bash
# 只跑股票相关
python3 test_runner.py stock

# 只跑 ETF
python3 test_runner.py etf

# 只跑宏观经济
python3 test_runner.py economic

# 多个关键词
python3 test_runner.py stock etf fund

# 精确匹配某个 subskill
python3 test_runner.py get-nth-trade-date
```

支持的过滤关键词：

| 关键词 | 匹配范围 |
|--------|---------|
| `stock` | 股票行情、财务、持仓 |
| `etf` | ETF 全部 |
| `index` | 指数 |
| `fund` | 基金 |
| `cb` | 可转债 |
| `economic` | 宏观经济（中国+美国） |
| `block` | 大宗交易 |
| `margin` | 两融 |
| `pledge` | 股权质押 |
| `news` | 新闻语义搜索 |
| `holder` | 股东信息 |
| `performance` | 业绩快报/预告 |

### 2. 清空历史日志后运行

```bash
python3 test_runner.py --clean
```

会删除 `test_logs/` 下所有 `.json` 和 `summary_*.txt` 文件，然后重新运行全部测试。

### 3. 组合使用

```bash
# 清空日志 + 只跑股票类
python3 test_runner.py --clean stock

# 清空日志 + 跑多个类别
python3 test_runner.py --clean stock etf fund
```

---

## 日志文件说明

### JSON 日志文件

每个成功的接口调用会生成独立的 JSON 文件：

```
test_logs/stock-security-info_20260324_115213.json
```

命名规则：`<subskill名>_<运行时间戳>.json`

内容为接口返回的完整 JSON 响应（已格式化，indent=2）。

### 汇总日志文件

每次运行生成一个汇总报告：

```
test_logs/summary_20260324_115213.txt
```

内容包含：
- 运行时间戳
- 用例总数、通过数、失败数、跳过数
- 总耗时
- 失败用例列表（如有）
- 全部用例明细（状态、耗时、日志文件名）

示例：

```
FTShare-market-data 测试汇总
运行时间: 20260324_115213
用例总数: 47  跳过: 2  执行: 45
PASS=45  FAIL=0
总耗时: 23.4s

全部用例明细：
  [  1] PASS  get-nth-trade-date - 前5个交易日  (351ms)
        日志：get-nth-trade-date_20260324_115213.json
  [  2] PASS  stock-list-all-stocks - 全量股票列表  (486ms)
        日志：stock-list-all-stocks_20260324_115213.json
  ...
```

---

## 测试用例覆盖范围

当前共 **47 个测试用例**，覆盖以下模块：

### 股票类（20 个）
- 股票列表、行情查询、K 线、分时
- 十大股东、十大流通股东、股东人数、增减持
- 利润表、资产负债表、现金流量表（单股全期 + 全市场特定期）
- 业绩快报、业绩预告（单股全期 + 全市场特定期）
- IPO 列表

### ETF 类（8 个）
- ETF 详情、列表、K 线、分时
- 成份股、盘前数据、PCF 列表、PCF 下载

### 指数类（4 个）
- 指数详情、列表、K 线、分时

### 基金类（5 个）
- 基金基础信息、累计收益、净值历史、概览、支持标的

### 可转债类（2 个）
- 可转债列表、基础信息

### 大宗交易 / 两融 / 质押（4 个）
- 大宗交易、融资融券明细、质押总揽、质押明细

### 新闻类（2 个）
- 语义搜索新闻

### 宏观经济（21 个）
- 中国 15 个指标（CPI、PPI、PMI、GDP、LPR、M2、社融、零售、进出口、工业、固投、财政、税收、外储、准备金率）
- 美国 6 个指标（ISM、非农、CPI、失业率、联邦基金利率等）

### 工具类（1 个）
- 获取前 N 个交易日

---

## 跳过的用例

以下用例默认跳过（标记 `skip=True`），原因说明：

| 用例 | 原因 |
|------|------|
| `etf-pre-single` | 盘前数据接口只在交易日盘前时段有效，非交易时段返回系统错误 |
| `etf-pcf-download` | 需要先调 `etf-pcfs` 拿到真实 filename 才能下载，不适合固定参数测试 |

如需测试这些接口，可手动调用：

```bash
# 交易日盘前时段测试
python3 run.py etf-pre-single --symbol 510300.XSHG

# 先查 PCF 列表再下载
python3 run.py etf-pcfs --date 20260324
python3 run.py etf-pcf-download --filename <从上面获取的真实文件名> --output test.xml
```

---

## 校验规则

每个测试用例会进行以下校验：

1. **退出码校验**：进程退出码必须为 0
2. **JSON 合法性校验**：stdout 必须为合法 JSON
3. **字段存在性校验**：检查响应中是否包含预期字段（`key_checks`）
4. **自定义业务校验**：如检查列表非空、字典结构等（`custom_validator`）

---

## CI 集成

脚本退出码：
- 全部通过退出 `0`
- 有失败用例退出 `1`

可直接接入 CI 流水线：

```bash
# GitHub Actions / GitLab CI 示例
python3 test_runner.py && echo "✅ 测试通过" || exit 1
```

---

## 常见问题

### Q1：日志文件太多怎么办？

使用 `--clean` 参数清空历史日志：

```bash
python3 test_runner.py --clean
```

### Q2：如何只看某个接口的返回 JSON？

```bash
# 运行测试
python3 test_runner.py stock-security-info

# 查看日志
cat test_logs/stock-security-info_<timestamp>.json
```

或者直接用 `run.py`：

```bash
python3 run.py stock-security-info --symbol 600519.SH | jq .
```

### Q3：某个接口超时怎么办？

默认超时 30 秒，如需调整，修改 `test_runner.py` 中的 `REQUEST_TIMEOUT_SEC` 常量。

### Q4：如何添加新的测试用例？

编辑 `test_runner.py` 中的 `_build_test_cases()` 函数，按现有格式添加 `TestCase` 对象。

---

## 维护建议

1. **每次发布前运行全量测试**，确保所有接口正常工作。
2. **定期清理日志目录**，避免占用过多磁盘空间。
3. **新增 subskill 时同步添加测试用例**，保持测试覆盖率。
4. **关注 SKIP 用例**，在合适的时段（如交易日盘前）手动验证。

---

## 附录：完整用例列表

运行以下命令查看所有用例名称：

```bash
python3 -c "
import sys
sys.path.insert(0, '.')
from test_runner import _build_test_cases
for i, c in enumerate(_build_test_cases(), 1):
    status = 'SKIP' if c.skip else 'RUN '
    print(f'{i:>3}. [{status}] {c.name}')
"
```

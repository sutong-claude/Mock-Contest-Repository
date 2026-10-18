# Coderlands 平台与采集路径初步勘查

> 来源：用户 2026-10-07 上传的《Coderlands_平台与采集路径初步勘查.md》；本文件整理为仓库长期版。
>
> 当前目标不是继续猜站点后端，而是保留已经验证过的页面事实和采集规格。

## 结论摘要

1. 前端高把握是 Vue SPA，使用 Vue Router、Axios；可见 Element UI 风格组件，同时混有 Layui/jQuery 和阿里云播放器。
2. 这些前端指纹不足以证明它基于 Hydro、HUSTOJ、QDUOJ、UOJ 等任一开源 OJ。
3. 更稳妥的判断：代码部落是教学/竞赛业务高度耦合的平台，后台可能自研或深度改造，但目前没有可靠源码/版本指纹。
4. 采集应从正常登录会话中真实页面行为出发，不猜 ID、不绕权限、不猜 API。
5. 此前已人工看过这场比赛的 4 道题、2 页规则 PDF、54 行榜单、本人 4 个提交详情，并抽查榜首 net 与另一位选手 tree。

## 已观察到的页面/资源

站点导航包含：
- 在线 IDE；
- 月赛；
- 笔记；
- 班级；
- 题库；
- 题单；
- 竞赛；
- 训练中心；
- 排行榜；
- AI 工具；
- 部落商城。

已观察资源包括：
- `jslib/vue.js`
- `jslib/axios.min.js`
- `jslib/vue-router.min.js`
- `layui/jquery-3.4.1.min.js`
- `/web/static/js/manifest.*.js`
- `/web/static/js/vendor.*.js`
- `/web/static/js/app.*.js`
- 阿里云 `aliplayer`

结论：只能确认 UI 技术栈，不能据此归因判题后端。

## 可靠导航方式

直接拼 hash 路由并不稳定。

实际复查时，可靠入口是：

```text
站内“竞赛”
→ 按完整比赛名搜索
→ 进入比赛
→ 已结束提示
→ 查看答题 / 查看成绩
```

因此未来 adapter 应以“站内正常导航”做入口，而不是硬拼隐藏路由。

## 榜单 DOM 原型

成绩弹窗中可识别：
- 数据行：含 ZJ- 考号的 `tr`
- 名次：`.col-rank`
- 考号：`.col-name .user-name`
- 总分：`.total-score`
- 每题：`.score-cell`
- 本人行：`tr.is-me`

榜单当时显示 54 行，但其中很多账号尚未开始，所以它是页面快照，不能直接拿 0 分账号计算“最终参赛者均分/中位数”。

## 提交详情 DOM 原型

点击分数后会出现 `.oi-sub-detail-dialog`。

重要现象：

> 弹窗刚出现时会先显示占位状态；稍后才异步加载真实分数与测试点。

所以采集器必须等待测试点行加载完成，不能固定睡极短时间后立即读 DOM。

表格还有横向滚动；目标分数格不可见时要先滚入视口，再点击。失败应记录“未采集”，不能误报成 0。

## 首版采集器模块

1. `find_contest(name)`
2. `read_contest()`
3. `read_problems()`
4. `read_ranklist()`
5. `read_submission(row, problem_index)`

统一输出：
- `contest.json`
- `problems.jsonl`
- `ranklist.jsonl`
- `submissions.jsonl`
- `capture_manifest.json`

## 当前网络层边界

本轮浏览工具能读 DOM、点击真实 UI、看控制台，但没有 Network/CDP 请求事件能力，也没有取得可复用 API URL/参数/JSON。

因此当前不能写：
> “API 已经探明”。

准确状态是：

> **已验证 DOM 规格 + 自动化架构；尚未完成真实 API 适配。**

以后如果能在正常登录浏览器里记录真实请求，再把稳定只读 API 抽出来；在此之前，DOM adapter 是最诚实的第一版。

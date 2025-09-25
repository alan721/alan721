# 网络热点话题收集工具

一个开箱即用的小软件，可以自动从百度实时热点榜单抓取热门话题，根据热度指数进行排序，并支持桌面界面或命令行两种方式查看结果。

## 功能特点

- 📊 自动抓取百度实时热搜榜。
- 🔢 将热度指数统一转换为数值，便于排序与后续分析。
- 🖥️ 自带桌面应用，一键刷新即可查看当前热点，并支持双击打开原文链接。
- 🔁 支持通过命令行参数控制返回条目数量及输出格式。
- 🧱 提供基础组件，方便后续扩展到其他热点来源。

## 快速开始

1. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

2. 启动桌面程序：

   ```bash
   python -m trending_topics.app
   ```

   程序会自动抓取最新的百度实时热点，列表展示排行、热度与来源，选中后可在下方查看简介，双击任意行即可打开原始链接。

3. 运行命令行工具（可选）：

   ```bash
   python -m trending_topics.cli --limit 20 --format table
   ```

   或以 JSON 格式输出：

   ```bash
   python -m trending_topics.cli --limit 10 --format json
   ```

## 模块说明

- `trending_topics.collectors.BaiduHotSearchCollector`：负责从百度实时热点页面解析话题数据。
- `trending_topics.ranking.rank_topics`：根据热度值对话题进行排序。
- `trending_topics.app`：基于 Tkinter 的图形界面，适合希望“一键获取热点”的用户。
- `trending_topics.cli`：简洁的 CLI 界面，可按需调整返回数量和输出格式。

## 测试

执行以下命令运行单元测试：

```bash
pytest
```

## 下一步可以做什么？

- 增加更多热点源（例如微博热搜、知乎热榜等），并将结果合并展示。
- 将结果写入数据库或推送到消息通知渠道，实现自动化的热点监控流程。
- 将 CLI 扩展为 Web 服务，为团队提供可视化的热点追踪面板。

# 🦞 微信公众号文章抓取工具 (wechat-article-fetcher)

> 绕过微信反爬机制，提取文章标题、作者和正文内容

## ✨ 特性

- ✅ **绕过反爬**：伪装浏览器 User-Agent，绕过微信验证码
- ✅ **智能提取**：自动识别标题、作者、正文段落
- ✅ **内容过滤**：去除无关内容（导航、广告、重复段落）
- ✅ **批量处理**：支持单篇/批量抓取
- ✅ **多格式输出**：支持纯文本、JSON、Markdown

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install beautifulsoup4 requests
```

### 2. 单篇抓取

```bash
# 基础用法（输出到终端）
python3 scripts/fetch_article.py "https://mp.weixin.qq.com/s/uLmsKoeNSrAPXDRi5r4pRA"

# 保存为 Markdown 文件
python3 scripts/fetch_article.py "URL" --output /tmp/article.md

# JSON 格式输出（适合程序调用）
python3 scripts/fetch_article.py "URL" --json
```

### 3. 批量抓取

```bash
# 从文件读取 URL 列表
python3 scripts/batch_fetch.py --urls-file urls.txt --output-dir /tmp/articles/

# 命令行指定多个 URL
python3 scripts/batch_fetch.py \
  --url "https://mp.weixin.qq.com/s/xxx" \
  --url "https://mp.weixin.qq.com/s/yyy" \
  --output-dir /tmp/articles/
```

## 📖 使用示例

### 示例 1：快速查看文章内容

```bash
$ python3 scripts/fetch_article.py "https://mp.weixin.qq.com/s/xxx"
🦞 正在抓取：https://mp.weixin.qq.com/s/xxx
✅ 下载完成，HTML 大小：3,028,645 字节
✅ 提取成功
标题：《龙虾使用指北》
作者：真格基金
段落数：165

============================================================
标题：《龙虾使用指北》
作者：真格基金
============================================================

欢迎来到《龙虾使用指北》。我们收录了深圳场 OpenClaw 活动里最具有代表性的 7 个案例...
```

### 示例 2：保存完整文章

```bash
$ python3 scripts/fetch_article.py "URL" --output ~/articles/article.md
🦞 正在抓取：https://mp.weixin.qq.com/s/xxx
✅ 下载完成，HTML 大小：3,028,645 字节
✅ 提取成功
标题：《龙虾使用指北》
作者：真格基金
段落数：165
✅ 已保存到：/Users/zhulin/articles/article.md
```

### 示例 3：程序化调用（JSON 输出）

```bash
$ python3 scripts/fetch_article.py "URL" --json
{
  "title": "《龙虾使用指北》",
  "author": "真格基金",
  "paragraphs": 165,
  "success": true,
  "content_preview": "欢迎来到《龙虾使用指北》。我们收录了深圳场 OpenClaw 活动里..."
}
```

### 示例 4：批量处理 50 篇文章

```bash
# 准备 urls.txt 文件（每行一个 URL）
cat urls.txt
https://mp.weixin.qq.com/s/xxx
https://mp.weixin.qq.com/s/yyy
https://mp.weixin.qq.com/s/zzz

# 执行批量抓取（每 2 秒请求一次，避免被封）
python3 scripts/batch_fetch.py --urls-file urls.txt --output-dir /tmp/articles/ --delay 2

# 查看结果
ls /tmp/articles/
20260415_173000_龙虾使用指北.md
20260415_173002_另一篇文章.md
...
batch_report.json  # 汇总报告
```

## 🔧 技术原理

### 为什么能绕过微信反爬？

微信文章有反爬机制：
- ❌ 直接 `curl` → 返回验证码页面
- ❌ 普通 HTTP 请求 → 可能被拦截或返回空内容
- ✅ **伪装浏览器 User-Agent** → 能拿到完整内容

### 核心代码

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
}
response = requests.get(url, headers=headers, timeout=15)
```

### 内容提取流程

1. **下载 HTML**：伪装浏览器，15 秒超时
2. **解析 HTML**：BeautifulSoup 提取 `<p>`, `<span>`, `<section>` 标签
3. **过滤内容**：去除"请在微信中打开"、"滑动看下一个"等无关内容
4. **去重处理**：保留段落顺序，去除重复段落
5. **输出结果**：Markdown/JSON/纯文本

## 📁 文件结构

```
wechat-article-fetcher/
├── README.md              # 使用说明（本文件）
├── SKILL.md               # Skill 定义（OpenClaw 集成）
└── scripts/
    ├── fetch_article.py   # 单篇抓取脚本
    └── batch_fetch.py     # 批量抓取脚本
```

## ⚠️ 限制与注意事项

### 已知限制

- 部分需要登录的文章无法访问（如付费文章、会员专享）
- 极少数文章可能仍有反爬保护
- 不支持视频/音频内容提取（仅提取文字）
- 图片会以文字形式保留描述，不下载图片文件

### 使用建议

1. **批量抓取时设置延迟**：`--delay 2` 或更长，避免请求过快被封
2. **大文章用 --output**：终端输出会截断，保存文件更完整
3. **检查提取结果**：极少数文章可能提取失败，手动验证

### 错误处理

```bash
# 常见错误 1：网络问题
❌ 错误：下载失败：HTTPSConnectionPool...
解决：检查网络连接，重试

# 常见错误 2：URL 无效
❌ 错误：下载失败：404 Client Error
解决：确认 URL 正确，文章未被删除

# 常见错误 3：提取失败
⚠️ 警告：未能提取到正文内容
解决：文章结构特殊，手动查看 HTML
```

## 🦞 OpenClaw 集成

如果你使用 OpenClaw，将此 Skill 添加到你的技能库：

```bash
# 克隆或复制此技能目录到
~/.openclaw/skills/wechat-article-fetcher/

# 或在 SOUL.md / TOOLS.md 中添加使用方法
```

在 OpenClaw 中调用：
```bash
python3 ~/clawd/skills/wechat-article-fetcher/scripts/fetch_article.py "URL"
```

## 📝 更新日志

- **2026-04-15**：初始版本
  - ✅ 单篇抓取功能
  - ✅ 批量抓取功能
  - ✅ Markdown/JSON 输出
  - ✅ 智能内容过滤

## 🤝 贡献

欢迎提交 Issue 和 PR！

**已知待优化**：
- [ ] 支持图片下载
- [ ] 支持视频/音频提取
- [ ] 支持付费文章（需登录态）
- [ ] 异步并发抓取（提升批量速度）

## 📄 许可证

MIT License

---

*Made with 🦞 by 老 A 的贾维斯*

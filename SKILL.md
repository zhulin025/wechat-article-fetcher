# wechat-article-fetcher Skill

微信公众号文章抓取技能，绕过微信反爬机制，提取文章标题、作者和正文内容。

## 触发场景

当用户需要：
- 阅读/总结微信公众号文章内容
- 提取微信文章的标题、作者、正文
- 批量处理多个微信文章链接

## 核心原理

微信有反爬机制：
- ❌ 直接 `curl` → 返回验证码页面
- ❌ 普通 HTTP 请求 → 可能被拦截
- ✅ **伪装浏览器 User-Agent + 解析 HTML** → 能拿到完整内容

## 使用方法

### 方式 1：直接调用脚本

```bash
python3 ~/clawd/skills/wechat-article-fetcher/scripts/fetch_article.py "微信文章 URL"
```

**输出示例**：
```json
{
  "title": "《龙虾使用指北》",
  "author": "真格基金",
  "content": "正文内容...",
  "paragraphs": 165,
  "success": true
}
```

### 方式 2：带输出文件

```bash
python3 ~/clawd/skills/wechat-article-fetcher/scripts/fetch_article.py \
  "https://mp.weixin.qq.com/s/xxx" \
  --output /tmp/article.md
```

### 方式 3：批量处理

```bash
python3 ~/clawd/skills/wechat-article-fetcher/scripts/batch_fetch.py \
  --urls-file urls.txt \
  --output-dir /tmp/articles/
```

## 依赖

```bash
pip install beautifulsoup4 requests
```

## 技术实现

1. **伪装浏览器**：设置 User-Agent 为真实浏览器
2. **超时控制**：15 秒超时（文章可能较大）
3. **HTML 解析**：BeautifulSoup 提取 `<p>`, `<span>`, `<section>` 标签
4. **内容过滤**：去除无关内容（"请在微信中打开"、"滑动看下一个"等）
5. **去重处理**：保留段落顺序，去除重复内容

## 限制

- 部分需要登录的文章无法访问
- 极少数文章可能仍有反爬保护
- 不支持视频/音频内容提取

## 相关文件

- `scripts/fetch_article.py` - 单篇文章抓取
- `scripts/batch_fetch.py` - 批量抓取
- `README.md` - 详细使用说明

#!/usr/bin/env python3
"""
微信公众号文章抓取工具
绕过微信反爬机制，提取文章标题、作者和正文内容

用法:
    python3 fetch_article.py "微信文章 URL"
    python3 fetch_article.py "URL" --output /tmp/article.md
"""

import argparse
import json
import re
import sys
from html import unescape
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ 缺少依赖，请安装：pip install beautifulsoup4 requests")
    sys.exit(1)


def fetch_html(url: str, timeout: int = 15) -> str:
    """
    下载微信文章 HTML，伪装浏览器绕过反爬
    
    Args:
        url: 微信文章 URL
        timeout: 超时时间（秒）
    
    Returns:
        HTML 内容字符串
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        response.encoding = response.apparent_encoding  # 自动检测编码
        return response.text
    except requests.exceptions.RequestException as e:
        raise Exception(f"下载失败：{e}")


def extract_content(html: str) -> dict:
    """
    从 HTML 中提取文章标题、作者和正文
    
    Args:
        html: 微信文章 HTML
    
    Returns:
        包含 title, author, content, paragraphs 的字典
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # 提取标题 - 尝试多种方式
    title = ""
    for tag in ['h1', 'h2', 'title']:
        for elem in soup.find_all(tag):
            text = elem.get_text(strip=True)
            if 5 < len(text) < 200:
                title = text
                break
        if title:
            break
    
    # 如果还没找到，找包含关键词的标题
    if not title:
        for elem in soup.find_all(['h1', 'h2', 'h3']):
            text = elem.get_text(strip=True)
            if any(kw in text for kw in ['龙虾', '指北', 'OpenClaw', 'AI']):
                title = text
                break
    
    # 提取作者
    author = ""
    author_elem = soup.find(class_='rich_media_meta_nickname')
    if author_elem:
        author = author_elem.get_text(strip=True)
    
    # 提取所有段落文本
    paragraphs = []
    for p in soup.find_all(['p', 'span', 'section']):
        text = p.get_text(strip=True)
        # 过滤掉太短的、重复的、无关的内容
        if (len(text) > 15 and 
            len(text) < 500 and 
            '请在微信中打开' not in text and
            '滑动看下一个' not in text and
            '轻触阅读原文' not in text and
            '关注公众号' not in text and
            '活动里最具有代表性的' not in text):  # 过滤导航重复内容
            paragraphs.append(text)
    
    # 去重（保留顺序）
    seen = set()
    unique_paragraphs = []
    for p in paragraphs:
        if p not in seen:
            seen.add(p)
            unique_paragraphs.append(p)
    
    # 组合正文
    content = "\n\n".join(unique_paragraphs)
    
    return {
        "title": title if title else "未找到标题",
        "author": author if author else "未知",
        "content": content,
        "paragraphs": len(unique_paragraphs),
        "success": len(unique_paragraphs) > 0
    }


def save_markdown(data: dict, output_path: str):
    """保存为 Markdown 格式"""
    md_content = f"# {data['title']}\n\n"
    md_content += f"**作者**: {data['author']}\n\n"
    md_content += f"**段落数**: {data['paragraphs']}\n\n"
    md_content += "---\n\n"
    md_content += data['content']
    
    Path(output_path).write_text(md_content, encoding='utf-8')
    print(f"✅ 已保存到：{output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='微信公众号文章抓取工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python3 fetch_article.py "https://mp.weixin.qq.com/s/xxx"
    python3 fetch_article.py "URL" --output /tmp/article.md
    python3 fetch_article.py "URL" --json  # 输出 JSON 格式
        """
    )
    parser.add_argument('url', help='微信文章 URL')
    parser.add_argument('--output', '-o', help='输出文件路径（Markdown 格式）')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    
    args = parser.parse_args()
    
    print(f"🦞 正在抓取：{args.url}")
    
    try:
        # 下载 HTML
        html = fetch_html(args.url)
        print(f"✅ 下载完成，HTML 大小：{len(html):,} 字节")
        
        # 提取内容
        data = extract_content(html)
        
        if not data['success']:
            print("⚠️ 警告：未能提取到正文内容")
            print(f"标题：{data['title']}")
            print(f"作者：{data['author']}")
        else:
            print(f"✅ 提取成功")
            print(f"标题：{data['title']}")
            print(f"作者：{data['author']}")
            print(f"段落数：{data['paragraphs']}")
        
        # 输出
        if args.json:
            # JSON 输出时不包含完整内容（可能太长）
            output = {
                "title": data['title'],
                "author": data['author'],
                "paragraphs": data['paragraphs'],
                "success": data['success'],
                "content_preview": data['content'][:500] + "..." if len(data['content']) > 500 else data['content']
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
        elif args.output:
            save_markdown(data, args.output)
        else:
            # 默认输出纯文本
            print(f"\n{'='*60}")
            print(f"标题：{data['title']}")
            print(f"作者：{data['author']}")
            print(f"{'='*60}\n")
            print(data['content'][:2000])  # 只显示前 2000 字符
            if len(data['content']) > 2000:
                print(f"\n...（还有 {len(data['content']) - 2000} 字符，使用 --output 保存完整内容）")
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
微信公众号文章批量抓取工具

用法:
    python3 batch_fetch.py --urls-file urls.txt --output-dir /tmp/articles/
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

try:
    from fetch_article import fetch_html, extract_content, save_markdown
except ImportError:
    print("❌ 请确保在同一目录下运行此脚本")
    sys.exit(1)


def load_urls(file_path: str) -> list:
    """从文件加载 URL 列表"""
    urls = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and line.startswith('http'):
                urls.append(line)
    return urls


def batch_fetch(urls: list, output_dir: str, delay: int = 2):
    """
    批量抓取文章
    
    Args:
        urls: URL 列表
        output_dir: 输出目录
        delay: 请求间隔（秒）
    """
    import time
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    results = []
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] 正在抓取：{url}")
        
        try:
            html = fetch_html(url)
            data = extract_content(html)
            
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_title = data['title'][:30].replace('/', '_').replace('\\', '_')
            filename = f"{timestamp}_{safe_title}.md"
            filepath = output_path / filename
            
            save_markdown(data, str(filepath))
            
            results.append({
                "url": url,
                "title": data['title'],
                "success": data['success'],
                "file": str(filepath)
            })
            
            # 延迟，避免请求过快
            if i < len(urls):
                time.sleep(delay)
                
        except Exception as e:
            print(f"❌ 失败：{e}")
            results.append({
                "url": url,
                "title": "N/A",
                "success": False,
                "error": str(e)
            })
    
    # 生成汇总报告
    report_path = output_path / "batch_report.json"
    import json
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ 批量抓取完成")
    print(f"成功：{sum(1 for r in results if r['success'])}/{len(results)}")
    print(f"报告：{report_path}")
    print(f"{'='*60}")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='微信公众号文章批量抓取工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python3 batch_fetch.py --urls-file urls.txt --output-dir /tmp/articles/
    python3 batch_fetch.py --url "URL1" --url "URL2" --output-dir /tmp/
        """
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--urls-file', help='包含 URL 列表的文件路径（每行一个 URL）')
    group.add_argument('--url', action='append', help='单个 URL（可多次指定）')
    
    parser.add_argument('--output-dir', '-o', required=True, help='输出目录')
    parser.add_argument('--delay', type=int, default=2, help='请求间隔（秒），默认 2 秒')
    
    args = parser.parse_args()
    
    # 加载 URL
    if args.urls_file:
        urls = load_urls(args.urls_file)
        print(f"📋 从 {args.urls_file} 加载了 {len(urls)} 个 URL")
    elif args.url:
        urls = args.url
        print(f"📋 命令行指定了 {len(urls)} 个 URL")
    else:
        print("❌ 请指定 --urls-file 或 --url")
        sys.exit(1)
    
    if not urls:
        print("❌ 没有有效的 URL")
        sys.exit(1)
    
    # 批量抓取
    batch_fetch(urls, args.output_dir, args.delay)


if __name__ == '__main__':
    main()

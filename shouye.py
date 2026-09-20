#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
常用网站导航页生成器
数据源用字典格式，修改 SITES 后运行脚本即可生成 index.html
"""

from datetime import datetime
from pathlib import Path
import json

# ==================== 数据源（字典格式，按需修改） ====================
SITES = {
    "常用工具": [
        {"name": "Google", "url": "https://www.google.com", "desc": "搜索引擎"},
        {"name": "GitHub", "url": "https://github.com", "desc": "代码托管"},
        {"name": "ChatGPT", "url": "https://chat.openai.com", "desc": "AI 对话"},
        {"name": "Claude", "url": "https://claude.ai", "desc": "AI 助手"},
        {"name": "Grok", "url": "https://x.com/i/grok", "desc": "xAI"},
    ],
    "开发相关": [
        {"name": "Stack Overflow", "url": "https://stackoverflow.com", "desc": "编程问答"},
        {"name": "MDN", "url": "https://developer.mozilla.org", "desc": "Web 文档"},
        {"name": "Python 官方", "url": "https://docs.python.org/zh-cn/3/", "desc": "Python 文档"},
        {"name": "LeetCode", "url": "https://leetcode.cn", "desc": "算法练习"},
    ],
    "资讯阅读": [
        {"name": "少数派", "url": "https://sspai.com", "desc": "科技生活"},
        {"name": "V2EX", "url": "https://www.v2ex.com", "desc": "创意工作者社区"},
        {"name": "Hacker News", "url": "https://news.ycombinator.com", "desc": "科技新闻"},
        {"name": "知乎", "url": "https://www.zhihu.com", "desc": "问答社区"},
    ],
    "娱乐影音": [
        {"name": "Bilibili", "url": "https://www.bilibili.com", "desc": "视频网站"},
        {"name": "YouTube", "url": "https://www.youtube.com", "desc": "视频"},
        {"name": "网易云音乐", "url": "https://music.163.com", "desc": "音乐"},
    ],
}

# 页面标题和副标题
PAGE_TITLE = "我的常用导航"
PAGE_SUBTITLE = "个人快速入口 · 每天自动更新"

# ==================== HTML 模板 ====================
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{subtitle}">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🔗</text></svg>">
  <style>
    :root {{
      --bg: #0f1115;
      --card: #1a1d24;
      --text: #e6e8ec;
      --muted: #9aa0a6;
      --accent: #5b8def;
      --border: #2a2e38;
      --hover: #252930;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      min-height: 100vh;
      padding: 24px 16px 48px;
    }}
    .container {{ max-width: 1100px; margin: 0 auto; }}
    header {{
      text-align: center;
      margin-bottom: 36px;
    }}
    h1 {{
      font-size: 1.8rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      margin-bottom: 6px;
    }}
    .subtitle {{
      color: var(--muted);
      font-size: 0.95rem;
    }}
    .search-box {{
      margin: 24px auto 0;
      max-width: 420px;
    }}
    .search-box input {{
      width: 100%;
      padding: 12px 16px;
      border-radius: 12px;
      border: 1px solid var(--border);
      background: var(--card);
      color: var(--text);
      font-size: 1rem;
      outline: none;
      transition: border-color 0.2s;
    }}
    .search-box input:focus {{
      border-color: var(--accent);
    }}
    .search-box input::placeholder {{ color: var(--muted); }}
    section {{
      margin-bottom: 32px;
    }}
    .category-title {{
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.06em;
      margin-bottom: 12px;
      padding-left: 4px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
      gap: 12px;
    }}
    .card {{
      display: flex;
      align-items: center;
      gap: 14px;
      padding: 14px 16px;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 14px;
      text-decoration: none;
      color: inherit;
      transition: background 0.15s, border-color 0.15s, transform 0.15s;
    }}
    .card:hover {{
      background: var(--hover);
      border-color: #3a4050;
      transform: translateY(-1px);
    }}
    .favicon {{
      width: 32px;
      height: 32px;
      border-radius: 8px;
      background: #2a2e38;
      flex-shrink: 0;
      object-fit: contain;
    }}
    .card-info {{
      min-width: 0;
      flex: 1;
    }}
    .card-name {{
      font-weight: 600;
      font-size: 0.95rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .card-desc {{
      font-size: 0.8rem;
      color: var(--muted);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      margin-top: 2px;
    }}
    footer {{
      text-align: center;
      margin-top: 48px;
      color: var(--muted);
      font-size: 0.8rem;
    }}
    footer a {{ color: var(--accent); text-decoration: none; }}
    .hidden {{ display: none !important; }}
    @media (max-width: 600px) {{
      h1 {{ font-size: 1.5rem; }}
      .grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>{title}</h1>
      <p class="subtitle">{subtitle}</p>
      <div class="search-box">
        <input type="search" id="search" placeholder="搜索网站..." autocomplete="off">
      </div>
    </header>

    <main id="main">
{content}
    </main>

    <footer>
      最后更新：{update_time} · 由本地脚本自动生成 ·
      <a href="https://github.com" target="_blank" rel="noopener">GitHub Pages</a>
    </footer>
  </div>

  <script>
    const searchInput = document.getElementById('search');
    const cards = document.querySelectorAll('.card');
    const sections = document.querySelectorAll('section');

    searchInput.addEventListener('input', () => {{
      const q = searchInput.value.trim().toLowerCase();
      cards.forEach(card => {{
        const name = card.dataset.name || '';
        const desc = card.dataset.desc || '';
        const match = !q || name.includes(q) || desc.includes(q);
        card.classList.toggle('hidden', !match);
      }});
      sections.forEach(sec => {{
        const visible = sec.querySelectorAll('.card:not(.hidden)').length > 0;
        sec.classList.toggle('hidden', !visible);
      }});
    }});

    // 键盘快捷键：按 / 聚焦搜索框
    document.addEventListener('keydown', e => {{
      if (e.key === '/' && document.activeElement.tagName !== 'INPUT') {{
        e.preventDefault();
        searchInput.focus();
      }}
    }});
  </script>
</body>
</html>
"""

def get_favicon_url(url: str) -> str:
    """使用 Google 的 favicon 服务（稳定、跨域友好）"""
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        return f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
    except Exception:
        return "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🌐</text></svg>"

def generate_html() -> str:
    content_parts = []
    for category, sites in SITES.items():
        cards = []
        for site in sites:
            favicon = get_favicon_url(site["url"])
            cards.append(f"""
        <a class="card" href="{site['url']}" target="_blank" rel="noopener"
           data-name="{site['name'].lower()}" data-desc="{site.get('desc', '').lower()}">
          <img class="favicon" src="{favicon}" alt="" loading="lazy"
               onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🌐</text></svg>'">
          <div class="card-info">
            <div class="card-name">{site['name']}</div>
            <div class="card-desc">{site.get('desc', '')}</div>
          </div>
        </a>""")
        content_parts.append(f"""
      <section>
        <div class="category-title">{category}</div>
        <div class="grid">
{''.join(cards)}
        </div>
      </section>""")

    update_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    return HTML_TEMPLATE.format(
        title=PAGE_TITLE,
        subtitle=PAGE_SUBTITLE,
        content="".join(content_parts),
        update_time=update_time,
    )

def main():
    html = generate_html()
    output = Path(__file__).parent / "index.html"
    output.write_text(html, encoding="utf-8")
    print(f"✅ 已生成: {output}")
    print(f"   共 {sum(len(v) for v in SITES.values())} 个链接，{len(SITES)} 个分类")

if __name__ == "__main__":
    main()
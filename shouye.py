# -*- coding: utf-8 -*-
"""
常用网站导航页自动更新系统（常驻循环版）
- 脚本位置：H:\stock_data_project\telegram_bot\generate_index.py
- 目标仓库：H:\stock_data_project\bookmarks\index.html
- 更新时间：每天 22:00 左右
"""

import os
import time
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from colorama import init, Fore, Style

init(autoreset=True)

# ====================== 1. 配置区域 ======================
# 路径配置（根据你的实际目录）
SCRIPT_DIR = Path(r"H:\stock_data_project\telegram_bot")
REPO_DIR = Path(r"H:\stock_data_project\bookmarks")          # Git 仓库根目录
INDEX_FILE = REPO_DIR / "index.html"                         # 要更新的文件
PROGRESS_FILE = SCRIPT_DIR / "nav_progress.json"             # 进度记录放在脚本目录

# 页面信息
PAGE_TITLE = "我的常用导航"
PAGE_SUBTITLE = "个人快速入口 · 每天自动更新"

# 运行控制
POLLING_INTERVAL = 60 * 30          # 每 30 分钟检查一次（更精准卡 22 点）
COOLDOWN_SECONDS = 3600 * 20        # 两次更新至少间隔 20 小时（保证一天只更新一次）
DRY_RUN_ONLY = False                # True = 只生成不推送 Git
AUTO_PUSH = True                    # 是否自动 git commit + push

# 每天 22 点更新（时间窗口 22:00 ~ 23:00）
PUSH_START_HOUR = 22
PUSH_END_HOUR   = 23

# ====================== 2. 数据源（按需修改） ======================
SITES: Dict[str, List[Dict[str, str]]] = {
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

# ====================== 3. HTML 模板 ======================
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
    header {{ text-align: center; margin-bottom: 36px; }}
    h1 {{ font-size: 1.8rem; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 6px; }}
    .subtitle {{ color: var(--muted); font-size: 0.95rem; }}
    .search-box {{ margin: 24px auto 0; max-width: 420px; }}
    .search-box input {{
      width: 100%; padding: 12px 16px; border-radius: 12px;
      border: 1px solid var(--border); background: var(--card);
      color: var(--text); font-size: 1rem; outline: none;
    }}
    .search-box input:focus {{ border-color: var(--accent); }}
    .search-box input::placeholder {{ color: var(--muted); }}
    section {{ margin-bottom: 32px; }}
    .category-title {{
      font-size: 0.85rem; font-weight: 600; color: var(--muted);
      text-transform: uppercase; letter-spacing: 0.06em;
      margin-bottom: 12px; padding-left: 4px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
      gap: 12px;
    }}
    .card {{
      display: flex; align-items: center; gap: 14px;
      padding: 14px 16px; background: var(--card);
      border: 1px solid var(--border); border-radius: 14px;
      text-decoration: none; color: inherit;
      transition: background 0.15s, border-color 0.15s, transform 0.15s;
    }}
    .card:hover {{ background: var(--hover); border-color: #3a4050; transform: translateY(-1px); }}
    .favicon {{ width: 32px; height: 32px; border-radius: 8px; background: #2a2e38; flex-shrink: 0; object-fit: contain; }}
    .card-info {{ min-width: 0; flex: 1; }}
    .card-name {{ font-weight: 600; font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .card-desc {{ font-size: 0.8rem; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 2px; }}
    footer {{ text-align: center; margin-top: 48px; color: var(--muted); font-size: 0.8rem; }}
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

# ====================== 4. 工具函数 ======================
def load_json(path: Path, default=None):
    if not path.exists():
        return default if default is not None else {}
    try:
        import json
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(Fore.RED + f"[错误] 读取 {path} 失败: {e}")
        return default if default is not None else {}


def save_json(path: Path, data: Any):
    try:
        import json
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(Fore.RED + f"[错误] 保存 {path} 失败: {e}")


def get_favicon_url(url: str) -> str:
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


def git_push() -> bool:
    """在目标仓库目录执行 git 操作（自动 pull --rebase 后再 push）"""
    if DRY_RUN_ONLY:
        print(Fore.MAGENTA + "⚠️ DRY_RUN 模式：跳过 git push")
        return True

    try:
        # 1. 先拉取远程最新代码（推荐 rebase，保持历史干净）
        print(Fore.CYAN + "🔄 正在拉取远程最新代码...")
        pull_result = subprocess.run(
            ["git", "pull", "--rebase", "origin", "main"],
            cwd=REPO_DIR,
            capture_output=True, text=True
        )
        if pull_result.returncode != 0:
            # 如果 rebase 失败，尝试普通 pull
            print(Fore.YELLOW + "⚠️ rebase 失败，尝试普通 pull...")
            pull_result = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=REPO_DIR,
                capture_output=True, text=True
            )
            if pull_result.returncode != 0:
                print(Fore.RED + f"❌ git pull 失败:\n{pull_result.stderr}")
                return False

        # 2. 检查 index.html 是否有改动
        result = subprocess.run(
            ["git", "status", "--porcelain", "index.html"],
            cwd=REPO_DIR,
            capture_output=True, text=True, check=True
        )
        if not result.stdout.strip():
            print(Fore.BLUE + "ℹ️  index.html 没有变化，跳过推送")
            return True

        # 3. 只提交 index.html（避免把其他无关文件一起提交）
        subprocess.run(["git", "add", "index.html"], cwd=REPO_DIR, check=True)
        commit_msg = f"chore: 自动更新导航页 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=REPO_DIR, check=True)

        # 4. 推送
        push_result = subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=REPO_DIR,
            capture_output=True, text=True
        )
        if push_result.returncode != 0:
            print(Fore.RED + f"❌ git push 失败:\n{push_result.stderr}")
            return False

        print(Fore.GREEN + "✅ 已自动推送到 GitHub")
        return True

    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"❌ Git 操作失败: {e}")
        return False
    except FileNotFoundError:
        print(Fore.RED + "❌ 未找到 git 命令，请确认已安装 Git 并加入 PATH")
        return False


# ====================== 5. 核心类 ======================
class NavUpdater:
    def __init__(self):
        self.progress = load_json(PROGRESS_FILE, {})
        self.last_update_ts = self.progress.get("last_update_ts", 0)
        total_links = sum(len(v) for v in SITES.values())
        print(Fore.GREEN + f"📚 数据源加载完成：共 {len(SITES)} 个分类，{total_links} 个链接")
        print(Fore.GREEN + f"📁 目标文件：{INDEX_FILE}")

    def should_update_now(self) -> bool:
        now = datetime.now()
        now_ts = time.time()

        # 1. 时间窗口检查（22:00 ~ 23:00）
        if not (PUSH_START_HOUR <= now.hour < PUSH_END_HOUR):
            print(Fore.BLUE + f"🌙 当前时间 {now.strftime('%H:%M')} 不在更新窗口 "
                              f"({PUSH_START_HOUR}:00 - {PUSH_END_HOUR}:00)，跳过")
            return False

        # 2. 冷却检查
        if now_ts - self.last_update_ts < COOLDOWN_SECONDS:
            remaining = int((COOLDOWN_SECONDS - (now_ts - self.last_update_ts)) // 60)
            print(Fore.BLUE + f"🧊 冷却中，距离下次可更新还有约 {remaining} 分钟")
            return False

        return True

    def run_once(self):
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始检查是否需要更新导航页...")

        if not self.should_update_now():
            return

        # 生成 HTML 到目标路径
        html = generate_html()
        INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
        INDEX_FILE.write_text(html, encoding="utf-8")
        print(Fore.GREEN + f"✅ 已生成: {INDEX_FILE}")

        # 推送
        success = True
        if AUTO_PUSH:
            success = git_push()
        else:
            print(Fore.YELLOW + "ℹ️  AUTO_PUSH = False，仅本地生成，未推送")

        if success:
            self.last_update_ts = time.time()
            self.progress["last_update_ts"] = self.last_update_ts
            self.progress["last_update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_json(PROGRESS_FILE, self.progress)
            print(Fore.GREEN + f"✅ 更新完成并记录时间")


# ====================== 6. 主程序（常驻循环） ======================
def main():
    print("=" * 70)
    print(Fore.CYAN + "🚀 常用导航页自动更新系统 已启动")
    print(f"脚本目录: {SCRIPT_DIR}")
    print(f"目标仓库: {REPO_DIR}")
    print(f"检查间隔: {POLLING_INTERVAL // 60} 分钟 | 更新冷却: {COOLDOWN_SECONDS // 3600} 小时")
    print(f"更新时间窗口: 每天 {PUSH_START_HOUR}:00 - {PUSH_END_HOUR}:00")
    print(f"自动推送 Git: {'开启' if AUTO_PUSH else '关闭'}")
    if DRY_RUN_ONLY:
        print(Fore.MAGENTA + "⚠️ 当前处于 DRY_RUN 模式，不会真实推送 Git")
    print("=" * 70)

    # 简单检查路径是否存在
    if not REPO_DIR.exists():
        print(Fore.RED + f"❌ 目标仓库目录不存在: {REPO_DIR}")
        print(Fore.YELLOW + "请确认路径是否正确")
        sys.exit(1)

    updater = NavUpdater()

    while True:
        try:
            updater.run_once()
        except KeyboardInterrupt:
            print("\n👋 服务已安全退出")
            break
        except Exception as e:
            print(Fore.RED + f"\n⚠️ 运行时异常: {e}")
            time.sleep(60)
            continue

        print(Fore.BLUE + f"下次检查将在 {POLLING_INTERVAL // 60} 分钟后...")
        time.sleep(POLLING_INTERVAL)


if __name__ == "__main__":
    main()
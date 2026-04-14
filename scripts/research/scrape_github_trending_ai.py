import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
KEYWORDS = ["ai", "agent", "llm", "大模型", "大语言模型", "gpt", "llama", "generative ai", "rag", "multi-agent"]
TRENDING_URL = "https://github.com/trending?since=daily"

def fetch_trending() -> List[Dict]:
    resp = requests.get(TRENDING_URL, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    projects = []
    for repo in soup.select("article.Box-row"):
        # 提取项目名称和url
        name_elem = repo.select_one("h2 a")
        if not name_elem:
            continue
        full_name = name_elem.get("href").lstrip("/")
        repo_url = f"https://github.com/{full_name}"
        # 提取描述
        desc_elem = repo.select_one("p.col-9")
        desc = desc_elem.get_text(strip=True) if desc_elem else ""
        # 过滤关键词
        text_to_check = (full_name + " " + desc).lower()
        if not any(k.lower() in text_to_check for k in KEYWORDS):
            continue
        # 提取总star数
        stars_elem = repo.select_one("a[href*='/stargazers']")
        total_stars = stars_elem.get_text(strip=True).replace(",", "") if stars_elem else "0"
        # 提取24小时新增star
        star_gain_elem = repo.select_one("span.d-inline-block.float-sm-right")
        star_gain = "0"
        if star_gain_elem:
            gain_text = star_gain_elem.get_text(strip=True)
            match = re.search(r"(\d+,?\d*) stars today", gain_text)
            if match:
                star_gain = match.group(1).replace(",", "")
        projects.append({
            "name": full_name,
            "url": repo_url,
            "total_stars": int(total_stars),
            "daily_star_gain": int(star_gain),
            "description": desc
        })
    # 按日增star排序
    projects.sort(key=lambda x: x["daily_star_gain"], reverse=True)
    return projects

def save_to_md(projects: List[Dict], output_path: str):
    md_content = "# 最近24小时GitHub Trending AI/Agent/大模型相关热门项目\n\n"
    md_content += "| 项目名称 | 仓库地址 | 总Star数 | 24小时新增Star | 核心功能描述 |\n"
    md_content += "| --- | --- | --- | --- | --- |\n"
    for p in projects:
        md_content += f"| {p['name']} | {p['url']} | {p['total_stars']:,} | {p['daily_star_gain']:,} | {p['description']} |\n"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"结果已保存到 {output_path}")

if __name__ == "__main__":
    projects = fetch_trending()
    output_file = "/Users/dxd/code/RealCoolSnow/hermes-agent/output/research/github_trending_ai_24h.md"
    save_to_md(projects, output_file)
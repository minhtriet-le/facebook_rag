import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import time
import psycopg2
from credential import config

# Đọc danh sách root URLs từ file
with open("roots.txt") as f:
    ROOT_URLS = [line.strip().rstrip("/") + "/" for line in f if line.strip()]

visited = set()

DB_NAME = config['DB_NAME']
DB_USER = config['DB_USER']
DB_PASSWORD = config['DB_PASSWORD']
DB_HOST = config['DB_HOST']
DB_PORT = config['DB_PORT']

# DB connect
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# Tạo bảng
cur.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE,
    root_url TEXT,
    title TEXT
);
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    document_id INT REFERENCES documents(id),
    chunk TEXT
);
""")
conn.commit()

def auto_chunk(text, max_chunk_size=2000, overlap=200):
    """Tự động chia nhỏ text nếu quá dài."""
    if len(text) <= max_chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks

def extract_section_text(soup):
    """Lấy text từ section có class hoặc id được chỉ định"""
    target_classes = [
        "_9ntw _9ntz _9nu2",
        "_9ntw _9nty _9nu2",
        "_9ntw _9nu2",
        "_9ntw _as3o _9nu2",
        "_9ntw _9ntz _9nt-",
        "_9ntw _9ntx _9nu2"
    ]

    texts = []

    # Theo class
    for cls in target_classes:
        for sec in soup.find_all("section", class_=cls):
            txt = sec.get_text(separator=" ", strip=True)
            if txt:
                texts.append(txt)

    # Theo id
    sec = soup.find("section", id="policy-details")
    if sec:
        txt = sec.get_text(separator=" ", strip=True)
        if txt:
            texts.append(txt)

    return " ".join(texts)

EXCLUDE_PREFIXES = [
    "https://transparency.meta.com/vi-vn/oversight/oversight-board-cases/"
]

def is_excluded(url):
    """Kiểm tra xem url có nằm trong danh sách exclude không"""
    return any(url.startswith(prefix) for prefix in EXCLUDE_PREFIXES)

def crawl(url, root_url, sleep_time=0.01):
    if url in visited or is_excluded(url):
        return
    visited.add(url)
    print(f"🔎 Đang crawl: {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"⚠️ Lỗi khi tải {url}: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string.strip() if soup.title else None

    text = extract_section_text(soup)
    if not text.strip():
        print(f"⚠️ Không tìm thấy text hợp lệ trong {url}")
        return

    # Insert document
    cur.execute(
        "INSERT INTO documents (url, root_url, title) VALUES (%s,%s,%s) ON CONFLICT (url) DO NOTHING RETURNING id",
        (url, root_url, title)
    )
    doc_id = cur.fetchone()
    if doc_id:
        doc_id = doc_id[0]
    else:
        cur.execute("SELECT id FROM documents WHERE url=%s", (url,))
        doc_id = cur.fetchone()[0]

    # Chunk text và insert
    chunks = auto_chunk(text)
    for chunk in chunks:
        cur.execute(
            "INSERT INTO chunks (document_id, chunk) VALUES (%s,%s)",
            (doc_id, chunk)
        )
    conn.commit()

    # Crawl link con trong cùng root_url
    for a_tag in soup.find_all("a", href=True):
        link = urljoin(url, a_tag["href"])
        if link.startswith(root_url) and not is_excluded(link):
            crawl(link, root_url, sleep_time)

    time.sleep(sleep_time)

if __name__ == "__main__":
    for root_url in ROOT_URLS:
        crawl(root_url, root_url)

    conn.close()

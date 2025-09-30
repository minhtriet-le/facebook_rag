import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import time
import psycopg2
from credential import config

# Read list of root URLs from file
with open("roots.txt") as f:
    ROOT_URLS = [line.strip().rstrip("/") + "/" for line in f if line.strip()]

visited = set()

# --- Database Connection ---
DB_NAME = config.DB_NAME
DB_USER = config.DB_USER
DB_PASS = config.DB_PASS
DB_HOST = config.DB_HOST
DB_PORT = config.DB_PORT

# DB connect
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# Create tables
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
    """Automatically split text into smaller chunks if it's too long."""
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
    """Extract text from sections with specified class or id"""
    target_classes = [
        "_9ntw _9ntz _9nu2",
        "_9ntw _9nty _9nu2",
        "_9ntw _9nu2",
        "_9ntw _as3o _9nu2",
        "_9ntw _9ntz _9nt-",
        "_9ntw _9ntx _9nu2"
    ]

    texts = []

    # By class
    for cls in target_classes:
        for sec in soup.find_all("section", class_=cls):
            txt = sec.get_text(separator=" ", strip=True)
            if txt:
                texts.append(txt)

    # By id
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
    """Check if url is in the exclude list"""
    return any(url.startswith(prefix) for prefix in EXCLUDE_PREFIXES)

def crawl(url, root_url, sleep_time=0.01):
    if url in visited or is_excluded(url):
        return
    visited.add(url)
    print(f"🔎 Crawling: {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"⚠️ Error loading {url}: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string.strip() if soup.title else None

    text = extract_section_text(soup)
    if not text.strip():
        print(f"⚠️ No valid text found in {url}")
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

    # Chunk text and insert
    chunks = auto_chunk(text)
    for chunk in chunks:
        cur.execute(
            "INSERT INTO chunks (document_id, chunk) VALUES (%s,%s)",
            (doc_id, chunk)
        )
    conn.commit()

    # Crawl child links within the same root_url
    for a_tag in soup.find_all("a", href=True):
        link = urljoin(url, a_tag["href"])
        if link.startswith(root_url) and not is_excluded(link):
            crawl(link, root_url, sleep_time)

    time.sleep(sleep_time)

if __name__ == "__main__":
    for root_url in ROOT_URLS:
        crawl(root_url, root_url)

    conn.close()

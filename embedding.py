import psycopg2
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from credential import config

# --- Kết nối DB (Giữ nguyên) ---
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

# ----------------- CREATE EMBEDDING COLUMN -----------------
cur.execute("""
ALTER TABLE chunks
ADD COLUMN IF NOT EXISTS embedding vector(1024);
""")
conn.commit()

# ----------------- LOAD BGE-M3 MODEL -----------------
print("🚀 Loading BGE-M3 model ...")
model = SentenceTransformer("BAAI/bge-m3")

# ----------------- GET CHUNKS TO EMBED -----------------
cur.execute("SELECT id, chunk FROM chunks WHERE embedding IS NULL;")
rows = cur.fetchall()
print(f"⚡ {len(rows)} chunks cần embed")

# ----------------- EMBEDDING & SAVE -----------------
for chunk_id, text in tqdm(rows):
    embedding = model.encode(text)
    emb_list = embedding.tolist()
    cur.execute(
        "UPDATE chunks SET embedding = %s WHERE id = %s",
        (emb_list, chunk_id)
    )

conn.commit()
conn.close()
print("✅ Hoàn tất embedding vào pgvector")

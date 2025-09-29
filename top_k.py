import psycopg2
from sentence_transformers import SentenceTransformer
from credential import config

# --- Config ---
TOP_K = 5
query = "Nội dung bóc lột trẻ em"

# --- Kết nối DB ---
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

# --- Load model BGE-M3 để encode query ---
model = SentenceTransformer("BAAI/bge-m3")
query_emb = model.encode(query).tolist()

# --- Truy vấn các chunk gần nhất (cosine similarity) ---
cur.execute("""
SELECT id, chunk, embedding <-> %s::vector AS distance
FROM chunks
ORDER BY distance
LIMIT %s;
""", (query_emb, TOP_K))

results = cur.fetchall()
for r in results:
    print(f"ID: {r[0]}, Distance: {r[2]}\nChunk: {r[1][:300]}...\n")

conn.close()

import psycopg2
from sentence_transformers import SentenceTransformer
from google import genai 
from google.genai import types # Added to use configuration
from google.genai.errors import APIError # Added for error handling

from credential import config
import os # Added for better API Key management

# --- Config ---
TOP_K = 5
query = "Đăng tải nội dung bóc lột trẻ em có đúng với chính sách Facebook?"

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

# ----------------- Load embedding model -----------------
# Note: If you want to use Gemini embeddings, you'll need to replace this part.
# But to maintain the current Retrieval Augmented Generation (RAG) logic, we keep it as is.
model = SentenceTransformer("BAAI/bge-m3")
query_emb = model.encode(query).tolist()

# ----------------- Retrieval -----------------
cur.execute("""
SELECT id, chunk, embedding <-> %s::vector AS distance
FROM chunks
ORDER BY distance
LIMIT %s;
""", (query_emb, TOP_K))

results = cur.fetchall()
context = "\n".join([r[1] for r in results])
conn.close()

# ----------------- Gemini API (Main changes section) -----------------

# try:
#     client = genai.Client()
# except Exception as e:
#     print(f"Error initializing Gemini Client: {e}")
#     print("Please ensure the GEMINI_API_KEY environment variable is set.")
#     exit()

# Generation configuration
generation_config = types.GenerateContentConfig(
    temperature=0.2
)

prompt = f"""
Bạn là trợ lý AI. Dựa trên thông tin dưới đây về những tiêu chuẩn và chính sách của Facebook, trả lời câu hỏi bằng tiếng Việt trong vòng 200 từ. Nếu không tìm thấy thông tin liên quan, hãy trả lời 'Không tìm thấy thông tin liên quan'.

Thông tin: {context}

Câu hỏi: {query}
"""
print("📝 Prompt:", prompt)

# try:
#     # Call Gemini API
#     # Use appropriate Gemini model, for example gemini-2.5-flash
#     resp = client.models.generate_content(
#         model="gemini-2.5-flash", # Powerful model, replacing gpt-4.1-mini
#         contents=[prompt],
#         config=generation_config,
#     )

#     answer = resp.text
#     print("💡 Trả lời:", answer)

# except APIError as e:
#     print(f"Error calling Gemini API: {e}")
# except Exception as e:
#     print(f"An unknown error occurred: {e}")
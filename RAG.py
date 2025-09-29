import psycopg2
from sentence_transformers import SentenceTransformer
# Thay thế: import OpenAI
from google import genai 
from google.genai import types # Thêm để sử dụng cấu hình
from google.genai.errors import APIError # Thêm để xử lý lỗi

from credential import config
import os # Thêm để quản lý API Key tốt hơn

# --- Config ---
TOP_K = 5
query = "Đăng tải nội dung bóc lột trẻ em có đúng với chính sách Facebook?"

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

# ----------------- Load embedding model (Giữ nguyên) -----------------
# Lưu ý: Nếu bạn muốn dùng embedding của Gemini, bạn sẽ cần thay thế phần này.
# Nhưng để giữ nguyên logic Retrieval Augment Generation (RAG) hiện tại, ta giữ nguyên.
model = SentenceTransformer("BAAI/bge-m3")
query_emb = model.encode(query).tolist()

# ----------------- Retrieval (Giữ nguyên) -----------------
cur.execute("""
SELECT id, chunk, embedding <-> %s::vector AS distance
FROM chunks
ORDER BY distance
LIMIT %s;
""", (query_emb, TOP_K))

results = cur.fetchall()
context = "\n".join([r[1] for r in results])
conn.close()

# ----------------- Gemini API (Phần thay đổi chính) -----------------

# try:
#     client = genai.Client()
# except Exception as e:
#     print(f"Lỗi khởi tạo Gemini Client: {e}")
#     print("Vui lòng đảm bảo biến môi trường GEMINI_API_KEY đã được thiết lập.")
#     exit()

# Cấu hình Generation
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
#     # Gọi Gemini API
#     # Sử dụng mô hình Gemini phù hợp, ví dụ gemini-2.5-flash
#     resp = client.models.generate_content(
#         model="gemini-2.5-flash", # Mô hình mạnh mẽ, thay thế gpt-4.1-mini
#         contents=[prompt],
#         config=generation_config,
#     )

#     answer = resp.text
#     print("💡 Trả lời:", answer)

# except APIError as e:
#     print(f"Lỗi gọi Gemini API: {e}")
# except Exception as e:
#     print(f"Đã xảy ra lỗi không xác định: {e}")
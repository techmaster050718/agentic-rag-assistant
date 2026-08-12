import requests
import subprocess

# Get failed IDs
result = subprocess.run(
    ["docker", "exec", "rag-postgres", "psql", "-U", "rag_user", "-d", "rag_db", "-t", "-c", "SELECT id FROM documents WHERE status != 'ingested';"],
    capture_output=True, text=True
)
ids = [i.strip() for i in result.stdout.split('\n') if i.strip()]

for doc_id in ids:
    res = requests.delete(f"http://localhost:8000/api/v1/documents/{doc_id}")
    print(f"Deleted {doc_id}: {res.status_code}")

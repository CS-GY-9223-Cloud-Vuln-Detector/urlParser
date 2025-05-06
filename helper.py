from supabase import create_client, Client
import uuid
import os
from datetime import datetime
from dotenv import load_dotenv
import hashlib
import logging

logger = logging.getLogger(__name__)

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def add_project(project_id: str, repo_url: str, project_owner: str):
    created_at = datetime.now().isoformat()
    name = repo_url.split("/")[-1].split(".")[0].strip()

    if repo_url.endswith(".git"):
        repo_url = repo_url[:-4]

    data = {
        "id": project_id,
        "name": name,
        "repo_url": repo_url,
        "project_owner": project_owner,
        "created_at": created_at,
    }

    try:
        response = supabase.table("projects").insert(data).execute()
        print("Project inserted:", response)
    except Exception as e:
        print("Failed to insert project:", e)


def add_file(project_id: str, file_name: str, md5_hash, loc, storage_path, file_path, file_url):
    id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()

    data = {
        "id": id,
        "file_name": file_name,
        "project_id": project_id,
        "created_at": created_at,
        "file_type": "python",
        "md5": md5_hash,
        "loc": loc,
        "storage_path": storage_path,
        "file_path": file_path,
        "file_url": file_url,
    }

    try:
        response = supabase.table("files").insert(data).execute()
        print("File inserted:", response)
        return id
    except Exception as e:
        print("Failed to insert file:", e)

def calculate_md5(file_path):
    """Calculate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def count_lines(file_path):
    """Count lines in a file"""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except Exception as e:
        logger.error(f"Error counting lines in {file_path}: {str(e)}")
        return 0

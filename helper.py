from supabase import create_client, Client
import uuid
import os
from datetime import datetime
from dotenv import load_dotenv

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


def add_file(project_id: str, file_name: str):
    id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()

    data = {
        "id": id,
        "file_name": file_name,
        "project_id": project_id,
        "created_at": created_at,
    }

    try:
        response = supabase.table("files").insert(data).execute()
        print("File inserted:", response)
        return id
    except Exception as e:
        print("Failed to insert file:", e)

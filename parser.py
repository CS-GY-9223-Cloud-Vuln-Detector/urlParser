import os
import shutil
import tempfile
from git import Repo
from supabase import create_client, Client
import stat
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = "cloud-files"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

class GitHubParser:
    def __init__(self, repo_url):
        self.repo_url = repo_url
        self.clone_dir = tempfile.mkdtemp()

    def clone_repo(self):
        print(f"Cloning {self.repo_url} into {self.clone_dir}")
        repo = Repo.clone_from(self.repo_url, self.clone_dir)
        repo.close()
        print("Repo cloned.")

    def find_python_files(self):
        py_files = []
        for root, _, files in os.walk(self.clone_dir):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    py_files.append(full_path)
        return py_files

    def upload_files(self, file_paths):
        uploaded = []
        for file_path in file_paths:
            relative_path = os.path.relpath(file_path, self.clone_dir)
            relative_path = relative_path.replace("\\", "/")

            with open(file_path, 'rb') as f:
                file_data = f.read()

                print(f"Uploading {relative_path} to Supabase...")

                try:
                    supabase.storage.from_(BUCKET_NAME).upload(
                        path=relative_path,
                        file=file_data,
                        file_options={"content-type": "text/x-python"}
                    )
                    uploaded.append(relative_path)
                except Exception as e:
                    print(f"Failed to upload {relative_path}: {e}")
        return uploaded

    def clean_up(self):
        shutil.rmtree(self.clone_dir, onerror=remove_readonly)
        print("Temporary files cleaned up.")

    def process(self):
        try:
            self.clone_repo()
            py_files = self.find_python_files()
            uploaded_files = self.upload_files(py_files)
            return uploaded_files
        finally:
            self.clean_up()

if __name__ == "__main__":
    repo_url = input("Enter GitHub repo URL: ").strip()
    parser = GitHubParser(repo_url)
    uploaded_files = parser.process()
    print("\\nUploaded Files:")
    for f in uploaded_files:
        print(f)
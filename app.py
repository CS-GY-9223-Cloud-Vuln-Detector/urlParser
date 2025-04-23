from flask import Flask, request, jsonify
from flask_cors import CORS
from parser import GitHubParser

app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})


@app.route("/parse", methods=["POST"])
def parse_repo():
    data = request.get_json()
    repo_url = data.get("repo_url")

    if not repo_url:
        return jsonify({"error": "Missing repo_url"}), 400

    try:
        parser = GitHubParser(repo_url)
        uploaded_files, file_ids, project_id = parser.process()

        return jsonify(
            {
                "status": "success",
                "project_id": project_id,
                "files_uploaded": uploaded_files,
                "file_ids": file_ids,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=6060)

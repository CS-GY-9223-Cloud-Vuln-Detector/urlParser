from flask import Flask, request, jsonify, g
from flask_cors import CORS
from parser import GitHubParser
from functools import wraps
from helper import supabase

app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        # Check for bearer token in Authorization header
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]

        if not token:
            return jsonify({"error": "Authentication Token is missing!"}), 401

        try:
            # Verify token with Supabase (adapting logic from core/security.py [cite: 1])
            user_response = supabase.auth.get_user(token)

            if not user_response or not user_response.user:
                return jsonify({"error": "Invalid or expired token"}), 401

            user_id = user_response.user.id

            # Fetch the user profile from your 'user_profiles' table
            profile_response = (
                supabase.table("users").select("*").eq("id", user_id).execute()
            )

            if not profile_response.data:
                # This case might happen if user exists in auth but not profiles table
                return jsonify({"error": "User profile not found"}), 404

            # Store the fetched profile in Flask's 'g' object for access in the route
            g.current_user_profile = profile_response.data[0]

        except Exception as e:
            print(f"Authentication error: {str(e)}")  # Log error
            # Check for specific Supabase/JWT errors if possible, otherwise return general error
            if "invalid JWT" in str(e).lower() or "token is invalid" in str(e).lower():
                return jsonify({"error": "Invalid or expired token"}), 401
            return jsonify({"error": "Could not validate credentials"}), 401

        # Proceed to the decorated route function
        return f(*args, **kwargs)

    return decorated_function

@app.route("/parse", methods=["POST"])
@token_required
def parse_repo():
    data = request.get_json()
    repo_url = data.get("repo_url")
    user_id = g.current_user_profile["id"]

    if not repo_url:
        return jsonify({"error": "Missing repo_url"}), 400

    try:
        parser = GitHubParser(repo_url, user_id)
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

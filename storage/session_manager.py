# storage/session_manager.py

user_sessions = {}

def start_session(user_id):
    user_sessions[user_id] = {
        "items": [],
        "branch": None,
        "step": "collecting_items"
    }

def reset_session(user_id):
    if user_id in user_sessions:
        del user_sessions[user_id]

def get_session(user_id):
    return user_sessions.get(user_id)

def set_items(user_id, items):
    user_sessions[user_id]["items"].extend(items)
    user_sessions[user_id]["step"] = "collecting_branch"

def set_branch(user_id, branch):
    user_sessions[user_id]["branch"] = branch
    user_sessions[user_id]["step"] = "complete"

import os
import requests
import json

from datetime import datetime

API_URL = os.getenv("API_URL", "http://localhost:8000")
API_URL_UPDATE = f"{API_URL}/api/update"

MOODLE_TIMELINE_PATH = "./services/moodle_timeline.json"

if __name__ == "__main__":
    with open(MOODLE_TIMELINE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for idx, item in enumerate(data):
        content_dict = item.get("content", {})

        data = {
            "source": "moodle",
            "timestamp": datetime.now().isoformat(),
            "content": f"an event titled {content_dict.get('title', '[no title]')} "
                        f"at date {content_dict.get('date', '[no date]')} "
                        f"for course {content_dict.get('course_name', '[no course]')}"
        }

        response = requests.post(API_URL_UPDATE, json=data)
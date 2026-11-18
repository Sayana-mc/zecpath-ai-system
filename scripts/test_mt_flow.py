import requests

AUTH = ("recruiter-d41-52", "Password123!LongEnough")
BASE = "http://127.0.0.1:8000"

res = requests.post(
    f"{BASE}/api/v1/machine-tests/assignments",
    auth=AUTH,
    json={
        "candidate_id": "cand_arun_kumar",
        "opening_id": "job_python_lead",
        "task_type": "coding",
        "task_id": "py_lru_cache_01",
        "title": "Implement Thread-Safe LRU Cache with TTL",
        "description": "Design an LRU Cache data structure supporting get(key) and put(key, value, ttl) operations with O(1) average time complexity.",
        "time_limit_minutes": 45
    }
)
print("Create assignment status:", res.status_code)
created = res.json()
print("Created assignment:", created)
assignment_id = created.get("assignment_id")

code_content = '''class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        val = self.cache.pop(key)
        self.cache[key] = val
        return val

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.pop(key)
        elif len(self.cache) >= self.capacity:
            oldest = next(iter(self.cache))
            del self.cache[oldest]
        self.cache[key] = value
'''

sub_res = requests.post(
    f"{BASE}/api/v1/machine-tests/assignments/{assignment_id}/submit",
    auth=AUTH,
    json={
        "code_content": code_content,
        "language": "python",
        "time_spent_minutes": 28.0
    }
)
print("Submit status:", sub_res.status_code)
print("Submit response:", sub_res.json())

list_subs = requests.get(
    f"{BASE}/api/v1/machine-tests/assignments/{assignment_id}/submissions",
    auth=AUTH
)
print("List submissions status:", list_subs.status_code)
print("List submissions count:", len(list_subs.json()))

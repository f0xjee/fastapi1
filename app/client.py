import requests

data = requests.post(
    "http://127.0.0.1:8000/api/v1/todo", json={"title": "todo_1", "important": True}
)

print(data.status_code)
print(data.json())


data = requests.get("http://127.0.0.1:8000/api/v1/advertisement/1")
print(data.status_code)
print(data.json())
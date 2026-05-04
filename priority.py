import requests
from datetime import datetime, timezone

ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJ0YW52aS4yNjM5OUBnZ25pbmRpYS5kcm9uYWNoYXJ5YS5pbmZvIiwiZXhwIjoxNzc3ODc4MTI3LCJpYXQiOjE3Nzc4NzcyMjcsImlzcyI6IkFmZm9yZCBNZWRpY2FsIFRlY2hub2xvZ2llcyBQcml2YXRlIExpbWl0ZWQiLCJqdGkiOiJmZTRkM2FmZC0yOTg1LTQ5N2EtOGU0OS0xNjAxYWU4ZjM3ZWIiLCJsb2NhbGUiOiJlbi1JTiIsIm5hbWUiOiJ0bnZpIGpvc2hpIiwic3ViIjoiMjA2NDM4Y2YtZWU1Ni00Mzk4LWFlNzEtYjQ1OGMwZGE4ODBmIn0sImVtYWlsIjoidGFudmkuMjYzOTlAZ2duaW5kaWEuZHJvbmFjaGFyeWEuaW5mbyIsIm5hbWUiOiJ0bnZpIGpvc2hpIiwicm9sbE5vIjoiMjYzOTkiLCJhY2Nlc3NDb2RlIjoidWtzZFdUIiwiY2xpZW50SUQiOiIyMDY0MzhjZi1lZTU2LTQzOTgtYWU3MS1iNDU4YzBkYTg4MGYiLCJjbGllbnRTZWNyZXQiOiJCSk1Ld1JEa0podmNTUVNEIn0.bFdiCgp81f0A03g0w8W_kSRRXbAobhUX5YWfmTR8fFY" 

API_URL = "http://20.207.122.201/evaluation-service/notifications" 

def calculate_priority(item):
    weights = {'placement': 300, 'result': 200, 'event': 100}
    
    category = item.get('type', 'event').lower()
    ts_str = item.get('created_at', datetime.now(timezone.utc).isoformat())
    
    try:
        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except:
        ts = datetime.now(timezone.utc)

    hours_old = (datetime.now(timezone.utc) - ts).total_seconds() / 3600
    score = weights.get(category, 50) - (hours_old * 10)
    
    return score

def get_priority_inbox(n=10):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(API_URL, headers=headers)
        
        if response.status_code != 200:
            print(f"Server returned error {response.status_code}: {response.text}")
            return

        data = response.json()
        print(f"DEBUG: Data received from API: {data}") 
        print(f"DEBUG: Data type: {type(data)}")

        if len(data) > 0:
            print(f"DEBUG: First item keys are: {data[0].keys()}") # This tells us the real names!
        
        scored_notifications = []
        for item in data:
            category = item.get('notificationType', item.get('type', 'event')).lower()
            content = item.get('message', item.get('content', 'No content available'))
            
            score = calculate_priority(item) 
            scored_notifications.append({
                'score': score,
                'type': category,
                'content': content
            })
        if isinstance(data, str):
            print(f"API returned a message instead of data: {data}")
            return
        
        if isinstance(data, dict):
            data = data.get('notifications', data.get('data', [data]))

        scored_notifications = []
        for item in data:
            if isinstance(item, dict): 
                score = calculate_priority(item)
                scored_notifications.append({
                    'score': score,
                    'type': item.get('type', 'N/A'),
                    'content': item.get('content', 'No content')
                })

        top_list = sorted(scored_notifications, key=lambda x: x['score'], reverse=True)[:n]

        
        print(f"\n--- TOP {n} PRIORITY NOTIFICATIONS ---")
        for i, note in enumerate(top_list, 1):
            print(f"{i}. [{note['type'].upper()}] (Score: {note['score']:.2f}) - {note['content']}")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    get_priority_inbox(10)
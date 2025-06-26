import requests
import pandas as pd
import os
response = requests.get("https://api.github.com")
data = response.json()
print("GitHub API Status_check_Change")
print(pd.DataFrame([data]))
api_key=os.getenv("API_KEY")
print(f"My API is {api_key})

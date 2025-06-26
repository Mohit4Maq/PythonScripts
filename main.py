import requests
import pandas as pd
response = requests.get("https://api.github.com")
data = response.json()
print("GitHub API Status_check_Change")
print(pd.DataFrame([data]))

import requests
import pandas as pd
response = requests.get("https://api.github.com")
data = response.json()
print("GitHub API Status")
print(pd.DataFrame([data]))

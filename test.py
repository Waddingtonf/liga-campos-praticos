import requests
import re

url = "https://docs.google.com/spreadsheets/d/1SFRlXmO_xmcD1HGnMN4LmALch2tkKGNlGFoOHtu5VYM/edit?usp=sharing"
resp = requests.get(url)

matches = re.findall(r'docs-sheet-tab-caption.*?>(.*?)<', resp.text)
cleaned = []
for m in matches:
    name = " ".join(m.split())
    if name and name not in cleaned:
        cleaned.append(name)
        
print("CLEANED TABS:", cleaned)

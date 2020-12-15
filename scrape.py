import json
import requests
from bs4 import Beautifulsoup

response = requests.get("https://www.mtgtop8.com/format?f=LE&meta=16&cp=1")
soup = BeautifulSoup(response.content, "html.parser")

entries = []
for entry in soup.find_all(class_ = "hover_tr"):
    column = entry.find_all("td")
    if t[4].find("img")["src"] == "/graph/bigstar.png":
        tourny_size = 4
    else:
        tourny_size = len(column[4].find_all("img"))
    deck = {
            "id" : column[0].find_all("input")[1]["value"],
            "url" : column[1].find("a")["href"],
            "archtype" : column[1].text.strip(),
            "player" : column[2].text.strip(),
            "event" : column[3].text.strip(),
            "size" : tourny_size,
            "place" : column[5].text.strip(),
            "date" : column[6].text.strip()

            }
    entries.append(deck)

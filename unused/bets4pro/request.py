import json

import requests
from bs4 import BeautifulSoup

url = "https://bets4.org/"

payload = ""
headers = {
    "cookie": "lang=en; _ym_uid=1698496197361582594; _ym_d=1698496197; _gcl_au=1.1.2103616613.1698496197; _ga=GA1.1.1692695333.1698496197; _fbp=fb.1.1698496197487.1957987306; overwatch=true; hs=true; soccer=true; dota2=true; PHPSESSID=co0tp0rn0o2sn41if7va91dr24; _ym_isad=2; cf_clearance=bBd_ujiRye4KITmr23U27_ki08M77MmDuz9IuNu7leE-1704307437-0-2-c1af11bd.ae1faf2b.e28cf9c4-0.2.1704307437; cs_go=true; basketball=false; hockey=true; lol=true; sc=true; valorant=true; other=true; _ga_S9E0G3W1VY=GS1.1.1704307434.5.1.1704308876.0.0.0",
    "authority": "bets4.net",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "referer": "https://bets4.net/express-bets/",
    "sec-ch-ua": "^\^Not_A",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "^\^Windows^^",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

response = requests.request("GET", url, data=payload, headers=headers)

html_str = response.text

html_str = html_str.replace('style="display: none;"', "")

soup = BeautifulSoup(html_str, 'html.parser')
blocks = soup.find_all(class_='main-content__item_bottom')

for block in blocks:
    link = block.find_parent()
    match_id = link["href"].split("/")[1].split("-")[1]

    team_1 = block.find(class_="team_1").get_text(separator="_^_", strip=True).split("_^_")[0]
    team_2 = block.find(class_="team_2").get_text(separator="_^_", strip=True).split("_^_")[0]

    bets = requests.get(f"https://bets4.org/widget/cofs_api.php?tournament_id={match_id}").text
    bets = json.loads(bets)

    bets = bets["response"]["cofs"]

    print(team_1, " - ", team_2)
    for bet in bets:
        print(1 + bet["team_1_cof"], " - ", 1 + bet["team_2_cof"], f" ({bet['type']})")

    print("________________________________________\n")

import requests

url = 'https://bets4.net/engine/function/bet.php'

headers = {
    'authority': 'bets4.net',
    'accept': '*/*',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'cookie': 'PHPSESSID=7g7oodbchfvculnq3dborah6a4; _ym_uid=1710485980694729689; _ym_d=1710485980; _gcl_au=1.1.163594364.1710485980; _ga=GA1.1.1086513639.1710485980; _fbp=fb.1.1710485979816.101480955; _ym_isad=2; lang=en; cf_clearance=xknjbO9bA3Q2Nynl_J0ezTj.ThsuIrfbakSThACkXuk-1710605360-1.0.1.1-SZ9PF9orLEzcPkQu0BjOc3SzNom3Dst4pD.amNqsU19TRC8DY0frxim.52ABb2_48NZNQTw5idIXTT0LJ7N61g; cof_change_agree=true; cof_change_agree_any=false; _ga_S9E0G3W1VY=GS1.1.1710605359.10.1.1710606314.0.0.0',
    'origin': 'https://bets4.net',
    'referer': 'https://bets4.net/tournament-343883/sentinels-karmine-corp/',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

data = {
  'user_betcoin': '0',
  'tournament': '343883',
  'type': 'live_game2',
  'bet_item': 'Array',
  'team_live_game2': 'team_1',
  'team_1_cof_live_game2': '0.935',
  'team_2_cof_live_game2': '0.821',
  'team_1_rate_live_game2': '48',
  'team_2_rate_live_game2': '52',
  'cof_change_agree': 'agree',
  'button_name': 'place-bet',
}

response = requests.post(url, headers=headers, data=data)

print(response.text)

import re

from fuzzywuzzy import fuzz

from config import WORD_BLACK_LIST, THRESHOLD


def update_team_name(team: str):
    team = team.strip().lower()

    for word in WORD_BLACK_LIST:
        team = team.replace(word, "")

    return team.strip()


def remove_id_key(d):
    ids = []

    ids.append(d.pop("id"))
    ids.extend(d.pop("sub_matches", []))

    ids = [str(i) for i in ids]

    d["fan_ids"] = ",".join(ids)
    return d


def are_teams_similar(team1, team2):
    similarity_score = fuzz.ratio(team1, team2)
    return similarity_score >= THRESHOLD


def is_reversed(d2by_team_1, d2by_team_2, fan_team_1, fan_team_2):
    same = fuzz.ratio(d2by_team_1, fan_team_1) + fuzz.ratio(d2by_team_2, fan_team_2)
    not_same = fuzz.ratio(d2by_team_1, fan_team_2) + fuzz.ratio(d2by_team_2, fan_team_1)

    if same > not_same:
        return False
    else:
        return True


def create_fan_sport_url(match_type, sport_id, league_id, league_name, match_id, team_1, team_2):
    if sport_id == 40:
        sport = "esports"
    elif sport_id == 3:
        sport = "basketball"
    elif sport_id == 1:
        sport = "football"
    else:
        return

    league_input = str(league_id) + " " + league_name
    league = re.sub(r'[^a-zA-Z0-9]+', '-', league_input).lower()

    match_input = str(match_id) + " " + team_1 + " " + team_2
    match = re.sub(r'[^a-zA-Z0-9]+', '-', match_input).lower()

    match_type = "line" if match_type == "LineFeed" else "live"

    return f"https://fan-sport.com/{match_type}/{sport}/{league}/{match}"


def calculate_odds_from_bets(team_am_1, team_am_2):
    team_1_am = team_am_1 + 1
    team_2_am = team_am_2 + 1

    team_1_cf = 1 + (team_2_am / team_1_am * 0.93)
    team_2_cf = 1 + (team_1_am / team_2_am * 0.93)

    return round(team_1_cf, 2), round(team_2_cf, 2)


def calculate_bets(fan_cf_1, fan_cf_2, d2by_cf_1, d2by_cf_2, d2by_am_1, d2by_am_2):
    if d2by_cf_1 > fan_cf_1:
        amount_bet = (115 * fan_cf_1 * d2by_am_1 + 115 * fan_cf_1 - 100 * d2by_am_1 - 193 - 93 * d2by_am_2) / (100 - 115 * fan_cf_1)
        side = 1
    elif d2by_cf_2 > fan_cf_2:
        amount_bet = (115 * fan_cf_2 * d2by_am_2 + 115 * fan_cf_2 - 100 * d2by_am_2 - 193 - 93 * d2by_am_1) / (100 - 115 * fan_cf_2)
        side = 2
    else:
        return None, None

    return amount_bet, side


def get_team_name(bet_name, reverse):
    if not reverse:
        if "1" in bet_name:
            return "1"
        elif "2" in bet_name:
            return "2"
        else:
            return bet_name
    else:
        if "1" in bet_name:
            return "2"
        elif "2" in bet_name:
            return "1"
        else:
            return bet_name


def add_bet_to_cfs(data, bet_id, bet_name, coef, url):
    b_data = data.get(bet_id, None)
    if not b_data:
        data[bet_id] = {
            "id": bet_id,
            "fan_bets": {f"{bet_name}": coef},
            "fan_url": url,
        }
    else:
        data[bet_id]["fan_bets"].update({f"{bet_name}": coef})

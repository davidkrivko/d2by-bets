import re

from fuzzywuzzy import fuzz

from config import WORD_BLACK_LIST, THRESHOLD


def update_team_name(team):
    team = team.strip().lower()

    pattern = r"\b(?:" + "|".join(map(re.escape, WORD_BLACK_LIST)) + r")\b"

    result_string = re.sub(pattern, "", team, flags=re.IGNORECASE)

    return result_string.strip()


def remove_id_key(d):
    d.pop("id", None)
    d.pop("sub_matches", None)
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

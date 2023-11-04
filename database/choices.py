MATCH_TYPE = [
    "MATCH_WINNER",
    "HANDICAP",
    "OVER_UNDER",
]


BETS_ORDER_D2BY = {
    "MATCH_WINNER": {"$numberDecimal": "0"},
    "OVER_UNDER_MATCH": 2,  # "values" это значение от которого больше меньше выставляется
    "HANDICAP_MAP_1": 3,  # "values" это значение от которого больше меньше выставляется
    "HANDICAP_MAP_2": 4,  # "values" это значение от которого больше меньше выставляется

}

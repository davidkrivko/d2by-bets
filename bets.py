# from betsModel import betsModel
# from betsModelGroup import betsModelGroup
#
#
# def extract_bet_details(response):
#     bet_details = []
#
#     for bet in response['E']:
#         bet_model = betsModel.get(str(bet['T']), "")
#         bet_group = betsModelGroup.get(bet_model["IdG"], "")
#
#         bet_details.append({
#             'betGroupName': bet_group.get('N', None),
#             'betModelName': bet_model.get('N', None),
#             'coefficient': bet.get('C', None)
#         })
#
#     return bet_details
#
#
# api_response = {
#     "E": [
#             {
#                 "C": 1.67,
#                 "G": 1,
#                 "T": 1
#             },
#             {
#                 "C": 2.262,
#                 "G": 1,
#                 "T": 3
#             },
#             {
#                 "C": 3.18,
#                 "G": 2,
#                 "P": -4.5,
#                 "T": 7
#             },
#             {
#                 "C": 2.51,
#                 "G": 2,
#                 "P": -3.5,
#                 "T": 7
#             },
#             {
#                 "C": 1.99,
#                 "CE": 1,
#                 "G": 2,
#                 "P": -2.5,
#                 "T": 7
#             },
#             {
#                 "C": 1.45,
#                 "G": 2,
#                 "P": 2.5,
#                 "T": 7
#             },
#             {
#                 "C": 1.31,
#                 "G": 2,
#                 "P": 3.5,
#                 "T": 7
#             },
#             {
#                 "C": 1.36,
#                 "G": 2,
#                 "P": 4.5,
#                 "T": 8
#             },
#             {
#                 "C": 1.54,
#                 "G": 2,
#                 "P": 3.5,
#                 "T": 8
#             },
#             {
#                 "C": 1.83,
#                 "CE": 1,
#                 "G": 2,
#                 "P": 2.5,
#                 "T": 8
#             },
#             {
#                 "C": 2.79,
#                 "G": 2,
#                 "P": -2.5,
#                 "T": 8
#             },
#             {
#                 "C": 3.54,
#                 "G": 2,
#                 "P": -3.5,
#                 "T": 8
#             },
#             {
#                 "C": 1.33,
#                 "G": 17,
#                 "P": 19.5,
#                 "T": 9
#             },
#             {
#                 "C": 1.53,
#                 "G": 17,
#                 "P": 20.5,
#                 "T": 9
#             },
#             {
#                 "C": 1.86,
#                 "CE": 1,
#                 "G": 17,
#                 "P": 21.5,
#                 "T": 9
#             },
#             {
#                 "C": 2.42,
#                 "G": 17,
#                 "P": 22.5,
#                 "T": 9
#             },
#             {
#                 "C": 3.52,
#                 "G": 17,
#                 "P": 23.5,
#                 "T": 9
#             },
#             {
#                 "C": 3.38,
#                 "G": 17,
#                 "P": 19.5,
#                 "T": 10
#             },
#             {
#                 "C": 2.52,
#                 "G": 17,
#                 "P": 20.5,
#                 "T": 10
#             },
#             {
#                 "C": 1.95,
#                 "CE": 1,
#                 "G": 17,
#                 "P": 21.5,
#                 "T": 10
#             },
#             {
#                 "C": 1.58,
#                 "G": 17,
#                 "P": 22.5,
#                 "T": 10
#             },
#             {
#                 "C": 1.31,
#                 "G": 17,
#                 "P": 23.5,
#                 "T": 10
#             },
#             {
#                 "C": 1.53,
#                 "CE": 1,
#                 "G": 15,
#                 "P": 12.5,
#                 "T": 11
#             },
#             {
#                 "C": 2.53,
#                 "CE": 1,
#                 "G": 15,
#                 "P": 12.5,
#                 "T": 12
#             },
#             {
#                 "C": 1.93,
#                 "CE": 1,
#                 "G": 62,
#                 "P": 11.5,
#                 "T": 13
#             },
#             {
#                 "C": 1.88,
#                 "CE": 1,
#                 "G": 62,
#                 "P": 11.5,
#                 "T": 14
#             },
#             {
#                 "C": 6.33,
#                 "G": 90,
#                 "T": 759
#             },
#             {
#                 "C": 1.12,
#                 "G": 90,
#                 "T": 761
#             },
#             {
#                 "C": 7.5,
#                 "G": 864,
#                 "P": 2,
#                 "T": 2832
#             },
#             {
#                 "C": 7.75,
#                 "G": 864,
#                 "P": 3,
#                 "T": 2832
#             },
#             {
#                 "C": 9,
#                 "G": 864,
#                 "P": 4,
#                 "T": 2832
#             },
#             {
#                 "C": 10.9,
#                 "G": 864,
#                 "P": 5,
#                 "T": 2832
#             },
#             {
#                 "C": 12,
#                 "G": 864,
#                 "P": 6,
#                 "T": 2832
#             },
#             {
#                 "C": 13.2,
#                 "G": 864,
#                 "P": 7,
#                 "T": 2832
#             },
#             {
#                 "C": 15.5,
#                 "G": 864,
#                 "P": 8,
#                 "T": 2832
#             },
#             {
#                 "C": 19,
#                 "G": 864,
#                 "P": 9,
#                 "T": 2832
#             },
#             {
#                 "C": 27,
#                 "G": 864,
#                 "P": 10,
#                 "T": 2832
#             },
#             {
#                 "C": 35,
#                 "G": 864,
#                 "P": 11,
#                 "T": 2832
#             },
#             {
#                 "C": 70,
#                 "G": 864,
#                 "P": 12,
#                 "T": 2832
#             },
#             {
#                 "C": 9.35,
#                 "G": 864,
#                 "P": 2,
#                 "T": 2833
#             },
#             {
#                 "C": 9.95,
#                 "G": 864,
#                 "P": 3,
#                 "T": 2833
#             },
#             {
#                 "C": 11.7,
#                 "G": 864,
#                 "P": 4,
#                 "T": 2833
#             },
#             {
#                 "C": 14.2,
#                 "G": 864,
#                 "P": 5,
#                 "T": 2833
#             },
#             {
#                 "C": 15.5,
#                 "G": 864,
#                 "P": 6,
#                 "T": 2833
#             },
#             {
#                 "C": 17.5,
#                 "G": 864,
#                 "P": 7,
#                 "T": 2833
#             },
#             {
#                 "C": 21,
#                 "G": 864,
#                 "P": 8,
#                 "T": 2833
#             },
#             {
#                 "C": 26,
#                 "G": 864,
#                 "P": 9,
#                 "T": 2833
#             },
#             {
#                 "C": 38,
#                 "G": 864,
#                 "P": 10,
#                 "T": 2833
#             },
#             {
#                 "C": 49,
#                 "G": 864,
#                 "P": 11,
#                 "T": 2833
#             },
#             {
#                 "C": 1.75,
#                 "G": 2717,
#                 "T": 3508
#             },
#             {
#                 "C": 2.06,
#                 "G": 2717,
#                 "T": 3509
#             }
#     ]
# }
#
# bets_detail = extract_bet_details(api_response)
#
# for bet in bets_detail:
#     print(bet)
import datetime
import re
from collections import defaultdict

from betsModel import betsModel


# mats = {
#     92: {
#         "teams": ("fc porto", "milan"),
#         "start_time": datetime.datetime(2023, 11, 2, 10, 0)
#     },
#     176: {
#         "teams": ("freedom", "big brain"),
#         "start_time": datetime.datetime(2023, 11, 5, 19, 0)
#     },
#     139: {
#         "teams": ("9ine", "1win"),
#         "start_time": datetime.datetime(2023, 11, 4, 18, 0)
#     },
#     43: {
#         "teams": ("everton", "burnley"),
#         "start_time": datetime.datetime(2023, 11, 3, 16, 0)
#     },
#     40: {
#         "teams": ("miami heat", "brooklyn nets"),
#         "start_time": datetime.datetime(2023, 11, 4, 20, 0)
#     },
# }
#
#
# sec_mats = [
#     {
#         "CI": 123,
#         "O1": "fc porto",
#         "O2": "ac milan",
#         "S": datetime.datetime(2023, 11, 2, 10, 10).timestamp()
#     },
#     {
#         "CI": 675,
#         "O1": "9ine",
#         "O2": "1win",
#         "S": datetime.datetime(2023, 11, 2, 10, 10).timestamp()
#     },
#     {
#         "CI": 340,
#         "O1": "9ine",
#         "O2": "win",
#         "S": datetime.datetime(2023, 11, 4, 17, 50).timestamp(),
#     },
#     {
#         "CI": 100,
#         "O1": "freedom",
#         "O2": "win",
#         "S": datetime.datetime(2023, 11, 5, 19, 2).timestamp(),
#     }
# ]
#
#
# def compare(matches, mats, sport_id):
#     return [
#                 {
#                     "id": match["CI"],
#                     "team_1": match["O1"].lower(),
#                     "team_2": match["O2"].lower(),
#                     "start_time": datetime.datetime.fromtimestamp(match["S"]),
#                     "d2by_id": mat_id,
#                     "sub_matches": [sub["CI"] for sub in match["SG"]] if sport_id == 40 else []
#                 }
#                 for mat_id, mat in mats.items()
#                 for match in matches
#                 if (
#                         (match["O1"].lower() in mat["teams"] or match["O2"].lower() in mat["teams"])
#                         and (
#                                 (mat["start_time"] - datetime.timedelta(minutes=10))
#                                 <= datetime.datetime.fromtimestamp(match["S"])
#                                 <= (mat["start_time"] + datetime.timedelta(minutes=10))
#                         )
#                 )
#             ]
#
#
# res = compare(sec_mats, mats, 3)
# print(res)


def group_by_g_then_t(data):
    grouped_data = defaultdict(lambda: defaultdict(list))
    for item in data:
        g_value = item["G"]
        t_value = item["T"]
        grouped_data[g_value][t_value].append(item)
    return grouped_data


data = [
            {
                "C": 1.25,
                "G": 1,
                "T": 1
            },
            {
                "C": 3.735,
                "G": 1,
                "T": 3
            },
            {
                "C": 2.4,
                "G": 2436,
                "P": 2.5,
                "T": 2824
            },
            {
                "C": 1.53,
                "G": 2436,
                "P": 2.5,
                "T": 2825
            },
            {
                "C": 1.81,
                "G": 2438,
                "P": -1.5,
                "T": 2826
            },
            {
                "C": 1.08,
                "G": 2438,
                "P": 1.5,
                "T": 2826
            },
            {
                "C": 7.47,
                "G": 2438,
                "P": -1.5,
                "T": 2827
            },
            {
                "C": 1.93,
                "G": 2438,
                "P": 1.5,
                "T": 2827
            },
            {
                "C": 7.1,
                "G": 136,
                "P": 0.002,
                "T": 3044
            },
            {
                "C": 5.86,
                "G": 136,
                "P": 1.002,
                "T": 3044
            },
            {
                "C": 1.81,
                "G": 136,
                "P": 2,
                "T": 3044
            },
            {
                "C": 3.41,
                "G": 136,
                "P": 2.001,
                "T": 3044
            },
            {
                "C": 1.07,
                "G": 6993,
                "T": 5606
            },
            {
                "C": 7.15,
                "G": 6993,
                "T": 5607
            },
            {
                "C": 1.9,
                "G": 6995,
                "T": 5608
            },
            {
                "C": 1.81,
                "G": 6995,
                "T": 5609
            }
        ]

grouped_dict = group_by_g_then_t(data)



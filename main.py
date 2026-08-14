import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import requests
from bs4 import BeautifulSoup
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI(title="멀티 플랫폼 야구 선수 정밀 실시간 트래커 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MY_COOKIE = "PHPSESSID=aeoms26i6tggs7vsgrfovuko20"

PLAYERS_DB = {
    # 1. 이바다
    "ebada": {
        "name": "이바다",
        "back_number": "2",
        "team_name": "MAVERICKS (매버릭스)",
        "position": "내야수",
        "gameone_url": "https://www.gameone.kr/locker/?group_code=4FTVYZBDRQ03POLMAEJCW5S261XU879K",
        "nicecatch_url": "http://www.nicecatch.kr/team/31125b52-64db-4568-a8ef-3b18513cea75/playerstat/1abb154d-9758-4623-bf13-1cb0893a1f29",
        "nicecatch_api_url": "http://www.nicecatch.kr/api/team/31125b52-64db-4568-a8ef-3b18513cea75",
        "gameone_stats": {"avg": ".150", "hits": 3, "hr": 0, "ops": ".382", "ab": 20},
        "gameone_recent": [
            {"date": "08.09(일)", "opponent": "IRONY", "stat": "4타석 4타수 1안타 0득점 0타점"},
            {"date": "07.19(일)", "opponent": "The Players", "stat": "3타석 3타수 0안타 0득점 0타점"},
            {"date": "06.14(일)", "opponent": "미제스틱네미스", "stat": "3타석 2타수 0안타 0득점 1타점"},
            {"date": "05.17(일)", "opponent": "트래피스", "stat": "3타석 3타수 1안타 2득점 2타점"},
            {"date": "04.19(일)", "opponent": "류", "stat": "3타석 3타수 0안타 0득점 0타점"}
        ],
        "nicecatch_stats": {"avg": ".407", "hits": 11, "hr": 0, "ops": "1.025", "ab": 27}
    },
    # 2. 이재혁
    "jaehyuk": {
        "name": "이재혁",
        "back_number": "13",
        "team_name": "Mavericks / 무적LG / MIZAR",
        "position": "내야수 (우투좌타)",
        "gameone_url": "https://www.gameone.kr/locker/record/sum?group_code=B65B172516B4454C2FC8478691E4D760",
        "gameone_official_stats": {"avg": ".418", "hits": "33", "hr": "0", "ops": "1.108"},
        "mavericks_recent": [
            {"date": "08.09(일)", "sort_key": "08.09", "opponent": "IRONY (Mavericks)", "stat": "4타석 2타수 0안타 0득점 1타점"},
            {"date": "07.19(일)", "sort_key": "07.19", "opponent": "The Players (Mavericks)", "stat": "4타석 3타수 3안타 2득점 1타점"},
            {"date": "07.05(일)", "sort_key": "07.05", "opponent": "레드빅 (Mavericks)", "stat": "5타석 4타수 1안타 1득점 0타점"},
            {"date": "06.14(일)", "sort_key": "06.14", "opponent": "미제스틱네미스 (Mavericks)", "stat": "4타석 4타수 1안타 1득점 1타점"},
            {"date": "05.17(일)", "sort_key": "05.17", "opponent": "트래피스 (Mavericks)", "stat": "4타석 3타수 1안타 1득점 0타점"}
        ],
        "lgtwins_recent": [
            {"date": "08.02(일)", "sort_key": "08.02", "opponent": "Gideon brothers (무적LG)", "stat": "3타석 2타수 2안타 2득점 1타점"},
            {"date": "07.26(일)", "sort_key": "07.26", "opponent": "NYDS (무적LG)", "stat": "3타석 2타수 2안타 1득점 0타점"},
            {"date": "07.19(일)", "sort_key": "07.19", "opponent": "Airline Baseball 1 (무적LG)", "stat": "6타석 4타수 0안타 3득점 1타점"},
            {"date": "07.12(일)", "sort_key": "07.12", "opponent": "CB Bros (무적LG)", "stat": "4타석 3타수 3안타 3득점 0타점"},
            {"date": "07.05(일)", "sort_key": "07.05", "opponent": "귀가본능 (무적LG)", "stat": "5타석 4타수 0안타 1득점 0타점"}
        ],
        "mizar_recent": [
            {"date": "07.25(토)", "sort_key": "07.25", "opponent": "언디피티드 남 (MIZAR)", "stat": "3타석 2타수 0안타 0득점 1타점"},
            {"date": "06.27(토)", "sort_key": "06.27", "opponent": "빨간마일 (MIZAR)", "stat": "3타석 3타수 1안타 1득점 0타점"}
        ]
    },
    # 3. 황환주
    "hwanjoo": {
        "name": "황환주",
        "back_number": "33",
        "team_name": "MAVERICKS / 무적LG / 초인",
        "position": "내야수 (우투우타)",
        "gameone_url": "https://www.gameone.kr/locker/?group_code=P8AIVLPI0N4FB6KQZSVCT9BDGNO3WRYZ",
        "nicecatch_player_id": "f2210158-7bc3-4224-9cca-c409ddf973f7",
        "nicecatch_api_url": "http://www.nicecatch.kr/api/team/31125b52-64db-4568-a8ef-3b18513cea75",
        
        "gameone_official_stats": {"avg": ".319", "hits": 15, "hr": 0, "ops": ".955", "ab": 47},
        "nicecatch_official_stats": {"avg": ".200", "hits": 1, "hr": 0, "ops": ".733", "ab": 5},

        "mavericks_recent": [
            {"date": "08.09(일)", "sort_key": "08.09", "opponent": "IRONY (MAVERICKS)", "stat": "4타석 2타수 1안타 2득점 0타점"},
            {"date": "07.19(일)", "sort_key": "07.19", "opponent": "The Players (MAVERICKS)", "stat": "3타석 3타수 2안타 0득점 1타점"},
            {"date": "07.05(일)", "sort_key": "07.05", "opponent": "레드빅 (MAVERICKS)", "stat": "2타석 1타수 0안타 0득점 1타점"},
            {"date": "05.17(일)", "sort_key": "05.17", "opponent": "트래피스 (MAVERICKS)", "stat": "3타석 2타수 1안타 0득점 1타점"},
            {"date": "03.22(일)", "sort_key": "03.22", "opponent": "HustlePlays (MAVERICKS)", "stat": "3타석 2타수 1안타 1득점 1타점"}
        ],
        "lgtwins_recent": [
            {"date": "07.26(일)", "sort_key": "07.26", "opponent": "NYDS (무적LG)", "stat": "3타석 2타수 1안타 1득점 3타점"},
            {"date": "07.19(일)", "sort_key": "07.19", "opponent": "Airline Baseball T (무적LG)", "stat": "5타석 4타수 1안타 2득점 2타점"},
            {"date": "07.12(일)", "sort_key": "07.12", "opponent": "CB Bros (무적LG)", "stat": "3타석 3타수 0안타 0득점 0타점"},
            {"date": "07.05(일)", "sort_key": "07.05", "opponent": "귀가본능 (무적LG)", "stat": "4타석 3타수 2안타 2득점 1타점"},
            {"date": "06.21(일)", "sort_key": "06.21", "opponent": "Winning Takers (무적LG)", "stat": "4타석 3타수 1안타 1득점 0타점"}
        ]
    },
    # 4. 강전웅
    "jeonwoong": {
        "name": "강전웅",
        "back_number": "29",
        "team_name": "MAVERICKS (매버릭스)",
        "position": "외야수 (우투우타)",
        "gameone_url": "https://www.gameone.kr/locker/?group_code=5BO1OHKJROG000LP2V4",
        "gameone_official_stats": {"avg": ".250", "hits": "2", "hr": "0", "ops": ".775"},
        "mavericks_recent": [
            {"date": "08.09(일)", "opponent": "IRONY", "stat": "4타석 4타수 1안타 1득점 0타점"},
            {"date": "07.19(일)", "opponent": "The Players", "stat": "3타석 1타수 0안타 2득점 0타점"},
            {"date": "07.05(일)", "opponent": "레드빅", "stat": "1타석 1타수 0안타 0득점 0타점"},
            {"date": "06.14(일)", "opponent": "미제스틱베이스볼", "stat": "2타석 2타수 1안타 1득점 0타점"}
        ]
    },
    # 5. 정우정
    "woojeong": {
        "name": "정우정",
        "back_number": "4",
        "team_name": "MAVERICKS / 나이스캐치(초인)",
        "position": "외야수 (우투우타)",
        "gameone_url": "https://www.gameone.kr/locker/record/sum?group_code=2BKIPBMVLFL0000002AUQJ",
        "nicecatch_url": "http://www.nicecatch.kr/team/31125b52-64db-4568-a8ef-3b18513cea75/playerstat/02cba256-86fb-4afb-b7c5-b5679459f6a2",
        "nicecatch_api_url": "http://www.nicecatch.kr/api/team/31125b52-64db-4568-a8ef-3b18513cea75",
        
        "gameone_stats": {"avg": ".375", "hits": 3, "hr": 0, "ops": ".875", "ab": 8},
        "nicecatch_stats": {"avg": ".333", "hits": 4, "hr": 0, "ops": ".800", "ab": 12},

        "gameone_recent": [
            {"date": "06.14(일)", "opponent": "미제스틱베이스볼", "stat": "3타석 2타수 1안타 1득점 1타점"},
            {"date": "04.19(일)", "opponent": "류", "stat": "3타석 2타수 0안타 2득점 0타점"},
            {"date": "03.15(일)", "opponent": "Baseballclub BBs", "stat": "4타석 4타수 2안타 2득점 1타점"}
        ]
    }
}

def fetch_nicecatch_schedules_from_api(api_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json, text/plain, */*",
        "Referer": "http://www.nicecatch.kr/"
    }
    schedules = []
    try:
        res = requests.get(api_url, headers=headers, timeout=5)
        if res.status_code in [200, 304]:
            res_json = res.json()
            if res_json.get("ok"):
                games_data = res_json.get("data", {}).get("schedules", []) or res_json.get("data", {}).get("games", [])
                for g in games_data:
                    schedules.append({
                        "date": g.get("gameDate") or g.get("date") or "2026-08-23 13:00",
                        "opponent": g.get("awayTeamName") or g.get("vsTeam") or "TEAM BROS",
                        "stadium": g.get("stadiumName") or "고덕유수지야구장",
                        "league": "강동하반기일요일리그"
                    })
    except Exception as e:
        print(f"[API 호출 알림] {e}")

    if not schedules:
        schedules = [
            {"date": "2026-08-23 13:00", "opponent": "TEAM BROS", "stadium": "고덕유수지야구장", "league": "강동하반기일요일리그"},
            {"date": "2026-08-30 07:00", "opponent": "재미꾸로 야구단", "stadium": "고덕유수지야구장", "league": "강동하반기일요일리그"}
        ]
    return schedules


@app.get("/api/player/{player_id}")
def get_player_data(player_id: str):
    if player_id not in PLAYERS_DB:
        raise HTTPException(status_code=404, detail="존재하지 않는 선수입니다.")

    p_info = PLAYERS_DB[player_id]

    if player_id in ["ebada", "woojeong"]:
        go_s = p_info["gameone_stats"]
        nc_s = p_info["nicecatch_stats"]
        go_next_games = [{"date": "08월23일(일) 06:00", "opponent": "안드로메다", "stadium": "명품구장", "league": "MAVERICKS"}]
        nc_next_games = fetch_nicecatch_schedules_from_api(p_info["nicecatch_api_url"])

        tot_ab = go_s["ab"] + nc_s["ab"]
        tot_hits = go_s["hits"] + nc_s["hits"]
        tot_hr = go_s["hr"] + nc_s["hr"]
        combined_avg = f".{int(round(tot_hits / tot_ab, 3) * 1000):03d}" if tot_ab > 0 else ".000"

        return {
            "player_info": {
                "name": p_info["name"],
                "back_number": p_info["back_number"],
                "team_name": p_info["team_name"],
                "position": p_info["position"],
                "has_multi_platform": True,
                "teams": ["통합 기록", "게임원", "나이스캐치"]
            },
            "platforms": {
                "combined": {
                    "label": "통합 기록",
                    "season_stats": {"avg": combined_avg, "hits": str(tot_hits), "hr": str(tot_hr), "ops": ".830"},
                    "recent_games": p_info["gameone_recent"],
                    "next_games": go_next_games + nc_next_games
                },
                "gameone": {
                    "label": "게임원",
                    "season_stats": {"avg": go_s["avg"], "hits": str(go_s["hits"]), "hr": str(go_s["hr"]), "ops": go_s["ops"]},
                    "recent_games": p_info["gameone_recent"],
                    "next_games": go_next_games
                },
                "nicecatch": {
                    "label": "나이스캐치",
                    "season_stats": {"avg": nc_s["avg"], "hits": str(nc_s["hits"]), "hr": str(nc_s["hr"]), "ops": nc_s["ops"]},
                    "recent_games": [],
                    "next_games": nc_next_games
                }
            }
        }

    elif player_id == "hwanjoo":
        go_s = p_info["gameone_official_stats"]
        nc_s = p_info["nicecatch_official_stats"]
        
        tot_ab = go_s["ab"] + nc_s["ab"]
        tot_hits = go_s["hits"] + nc_s["hits"]
        tot_hr = go_s["hr"] + nc_s["hr"]
        combined_avg = f".{int(round(tot_hits / tot_ab, 3) * 1000):03d}" if tot_ab > 0 else ".000"

        m_rec = p_info["mavericks_recent"]
        lg_rec = p_info["lgtwins_recent"]
        all_recents_merged = sorted(m_rec + lg_rec, key=lambda x: x["sort_key"], reverse=True)

        go_next = [
            {"date": "08월16일(일) 06:00", "opponent": "Tyrant Baseball", "stadium": "에코리그", "league": "무적LG트윈스"},
            {"date": "08월23일(일) 06:00", "opponent": "안드로메다", "stadium": "명품구장", "league": "MAVERICKS"}
        ]
        nc_next = fetch_nicecatch_schedules_from_api(p_info["nicecatch_api_url"])

        return {
            "player_info": {
                "name": p_info["name"],
                "back_number": p_info["back_number"],
                "team_name": p_info["team_name"],
                "position": p_info["position"],
                "has_multi_platform": True,
                "teams": ["전체 소속팀", "MAVERICKS", "무적LG트윈스"]
            },
            "platforms": {
                "combined": {
                    "label": "전체 통합",
                    "season_stats": {"avg": combined_avg, "hits": str(tot_hits), "hr": str(tot_hr), "ops": ".934"},
                    "recent_games": all_recents_merged[:5],
                    "team_recents": {
                        "전체 소속팀": all_recents_merged[:5],
                        "MAVERICKS": m_rec[:5],
                        "무적LG트윈스": lg_rec[:5]
                    },
                    "next_games": go_next + nc_next
                },
                "gameone": {
                    "label": "게임원",
                    "season_stats": {"avg": go_s["avg"], "hits": str(go_s["hits"]), "hr": str(go_s["hr"]), "ops": go_s["ops"]},
                    "recent_games": all_recents_merged[:5],
                    "next_games": go_next
                },
                "nicecatch": {
                    "label": "나이스캐치",
                    "season_stats": {"avg": nc_s["avg"], "hits": str(nc_s["hits"]), "hr": str(nc_s["hr"]), "ops": nc_s["ops"]},
                    "recent_games": [],
                    "next_games": nc_next
                }
            }
        }

    elif player_id == "jaehyuk":
        off_s = p_info["gameone_official_stats"]
        m_rec = p_info["mavericks_recent"]
        lg_rec = p_info["lgtwins_recent"]
        mz_rec = p_info["mizar_recent"]

        all_recents_merged = sorted(m_rec + lg_rec + mz_rec, key=lambda x: x["sort_key"], reverse=True)

        next_games = [
            {"date": "08월16일(일) 06:00", "opponent": "Tyrant Baseball", "stadium": "에코리그", "league": "무적LG트윈스"},
            {"date": "08월23일(일) 06:00", "opponent": "안드로메다", "stadium": "명품구장", "league": "Mavericks"},
            {"date": "08월30일(일) 08:00", "opponent": "비체모스", "stadium": "남양주 에코 1야구장", "league": "무적LG트윈스"}
        ]

        return {
            "player_info": {
                "name": p_info["name"],
                "back_number": p_info["back_number"],
                "team_name": p_info["team_name"],
                "position": p_info["position"],
                "has_multi_platform": False,
                "teams": ["전체 소속팀", "Mavericks", "무적LG트윈스", "MIZAR"]
            },
            "platforms": {
                "combined": {
                    "label": "전체 통합",
                    "season_stats": {"avg": off_s["avg"], "hits": off_s["hits"], "hr": off_s["hr"], "ops": off_s["ops"]},
                    "recent_games": all_recents_merged[:5],
                    "team_recents": {
                        "전체 소속팀": all_recents_merged[:5],
                        "Mavericks": m_rec[:5],
                        "무적LG트윈스": lg_rec[:5],
                        "MIZAR": mz_rec[:5]
                    },
                    "next_games": next_games
                }
            }
        }

    else: # 강전웅
        off_s = p_info["gameone_official_stats"]
        m_rec = p_info["mavericks_recent"]
        go_next_games = [{"date": "08월23일(일) 06:00", "opponent": "안드로메다", "stadium": "명품구장", "league": "MAVERICKS"}]

        return {
            "player_info": {
                "name": p_info["name"],
                "back_number": p_info["back_number"],
                "team_name": p_info["team_name"],
                "position": p_info["position"],
                "has_multi_platform": False,
                "teams": ["MAVERICKS"]
            },
            "platforms": {
                "combined": {
                    "label": "게임원 기록",
                    "season_stats": {"avg": off_s["avg"], "hits": off_s["hits"], "hr": off_s["hr"], "ops": off_s["ops"]},
                    "recent_games": m_rec,
                    "team_recents": {
                        "MAVERICKS": m_rec
                    },
                    "next_games": go_next_games
                }
            }
        }

@app.get("/")
def read_root():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, "index.html")
    return FileResponse(html_path)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import requests
from bs4 import BeautifulSoup
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI(title="멀티 플랫폼 야구 선수 정밀 트래커 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PLAYERS_DB = {
    "ebada": {
        "name": "이바다",
        "back_number": "2",
        "team_name": "MAVERICKS (매버릭스)",
        "position": "내야수",
        "gameone_url": "https://www.gameone.kr/locker/?group_code=4FTVYZBDRQ03POLMAEJCW5S261XU879K",
        "nicecatch_url": "http://www.nicecatch.kr/team/31125b52-64db-4568-a8ef-3b18513cea75/playerstat/1abb154d-9758-4623-bf13-1cb0893a1f29",
        "gameone_schedule_url": "https://www.gameone.kr/club/info/schedule/table?club_idx=38528",
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
    "jaehyuk": {
        "name": "이재혁",
        "back_number": "우투좌타",
        "team_name": "MAVERICKS (매버릭스)",
        "position": "내야수",
        "gameone_url": "https://www.gameone.kr/locker/record/sum?group_code=B65B172516B4454C2FC8478691E4D760",
        "gameone_schedule_url": "https://www.gameone.kr/club/info/schedule/table?club_idx=38528",
        "gameone_stats": {"avg": ".418", "hits": 33, "hr": 0, "ops": "1.108", "ab": 79},
        "gameone_recent": [
            {"date": "08.09(일)", "opponent": "IRONY", "stat": "4타석 2타수 0안타 0득점 1타점"},
            {"date": "07.19(일)", "opponent": "The Players", "stat": "4타석 3타수 3안타 2득점 1타점"},
            {"date": "07.05(일)", "opponent": "레드빅", "stat": "5타석 4타수 1안타 1득점 0타점"},
            {"date": "06.14(일)", "opponent": "미제스틱네미스", "stat": "4타석 4타수 1안타 1득점 1타점"},
            {"date": "05.17(일)", "opponent": "트래피스", "stat": "4타석 3타수 1안타 1득점 0타점"}
        ]
    }
}

def fetch_nicecatch_schedules_from_api(api_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
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
                    game_date = g.get("gameDate") or g.get("date") or "2026-08-23 13:00"
                    vs_team = g.get("awayTeamName") or g.get("vsTeam") or "TEAM BROS"
                    stadium = g.get("stadiumName") or "고덕유수지야구장"
                    schedules.append({
                        "date": game_date,
                        "opponent": vs_team,
                        "stadium": stadium,
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
    go_next_games = [{"date": "08월23일(일) 06:00", "opponent": "안드로메다", "stadium": "명품구장", "league": "게임원 리그"}]

    if player_id == "ebada":
        go_s = p_info["gameone_stats"]
        nc_s = p_info["nicecatch_stats"]
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
                "has_multi_platform": True
            },
            "platforms": {
                "combined": {
                    "label": "통합 기록",
                    "season_stats": {"avg": combined_avg, "hits": str(tot_hits), "hr": str(tot_hr), "ops": ".752"},
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
            },
            "next_games": go_next_games
        }
    else:
        go_s = p_info["gameone_stats"]
        return {
            "player_info": {
                "name": p_info["name"],
                "back_number": p_info["back_number"],
                "team_name": p_info["team_name"],
                "position": p_info["position"],
                "has_multi_platform": False
            },
            "platforms": {
                "gameone": {
                    "label": "게임원",
                    "season_stats": {"avg": go_s["avg"], "hits": str(go_s["hits"]), "hr": str(go_s["hr"]), "ops": go_s["ops"]},
                    "recent_games": p_info["gameone_recent"],
                    "next_games": go_next_games
                }
            },
            "next_games": go_next_games
        }

@app.get("/")
def read_root():
    return FileResponse("index.html")
import tweepy
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.library.parameters import SeasonAll
import os
import random
import time
import update_repo_var

PROXY_LIST = os.getenv("PROXY_LIST", "").split(",")
PROXY_LIST = [p.strip().strip('"') for p in PROXY_LIST if p.strip()]

def get_proxy():
    return random.choice(PROXY_LIST) if PROXY_LIST else None

import requests
import subprocess
from requests.auth import HTTPBasicAuth

# Twitter API OAuth 2.0 PKCE credentials
TWITTER_CLIENT_ID = os.getenv('TWITTER_CLIENT_ID')
TWITTER_CLIENT_SECRET = os.getenv('TWITTER_CLIENT_SECRET')
TWITTER_REFRESH_TOKEN = os.getenv('TWITTER_REFRESH_TOKEN')

def get_oauth2_client():
    if not TWITTER_REFRESH_TOKEN or not TWITTER_CLIENT_ID:
        print("Missing TWITTER_REFRESH_TOKEN or TWITTER_CLIENT_ID secret.")
        return None
        
    url = "https://api.twitter.com/2/oauth2/token"
    data = {
        "refresh_token": TWITTER_REFRESH_TOKEN,
        "grant_type": "refresh_token",
        "client_id": TWITTER_CLIENT_ID,
    }
    
    # If client secret is provided (confidential client), add basic auth
    auth = HTTPBasicAuth(TWITTER_CLIENT_ID, TWITTER_CLIENT_SECRET) if TWITTER_CLIENT_SECRET else None
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=data, auth=auth, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to refresh Twitter token: {response.text}")
        return None
        
    tokens = response.json()
    new_access_token = tokens["access_token"]
    new_refresh_token = tokens.get("refresh_token")
    
    if new_refresh_token:
        try:
            # Update the GitHub Secret using the gh CLI natively installed in GitHub Actions
            subprocess.run(
                ["gh", "secret", "set", "TWITTER_REFRESH_TOKEN", "-b", new_refresh_token],
                check=True
            )
            print("Successfully updated TWITTER_REFRESH_TOKEN secret in GitHub.")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to update GitHub secret via gh CLI: {e}")
            
    return tweepy.Client(new_access_token)


# Function to fetch LeBron's latest game stats and compare with history
def get_lebron_stats():
    logs = playergamelog.PlayerGameLog(player_id='2544', season=SeasonAll.all, timeout=100, proxy=get_proxy()).get_data_frames()[0]
    print(logs)
    latest_game = logs.iloc[0]
    points = latest_game['PTS']
    rebounds = latest_game['REB']
    assists = latest_game['AST']
    found = False
    count = 0
    most_recent = None

    if latest_game['WL'] not in ['W', 'L']:
        return None
    
    for i in range(1, len(logs)):
        if not found and logs.iloc[i]['PTS'] == points and logs.iloc[i]['REB'] == rebounds and logs.iloc[i]['AST'] == assists:
            found = True
            most_recent = logs.iloc[i]['GAME_DATE']
            count += 1
        elif logs.iloc[i]['PTS'] == points and logs.iloc[i]['REB'] == rebounds and logs.iloc[i]['AST'] == assists:
            count += 1
    return {
        'points': points,
        'rebounds': rebounds,
        'assists': assists,
        'count': count,
        'most_recent': most_recent,
        'game_date': latest_game['GAME_DATE']   
    }


# Function to check stats and tweet
def check_and_tweet():
    stats = get_lebron_stats()
    if not stats or os.getenv('LAST_TWEET_DATE') == stats['game_date']:
        print(stats)
        print(os.getenv('LAST_TWEET_DATE'))
        print("No new updates")
        return
    stat_line = f"{stats['points']}PTS {stats['rebounds']}REB {stats['assists']}AST"
    end = "th"
    if stats['count'] == 1:
        end = 'nd'
    elif stats['count'] == 2:
        end = 'rd'
    if stats['count'] >= 1:
        tweet = (f"No Scorigami. LeBron James just recorded a stat line of {stat_line} for the {stats['count'] + 1}{end} time! He most recently achieved this stat line on {stats['most_recent']}🏀")
    else:
        tweet = (f"🚨 SCORIGAMI! 🚨 LeBron James just achieved a new stat line: {stat_line}! 🔥 #striveforgreatness🚀 #thekidfromakron👑 #jamesgang👑 #bronknows")
    client = get_oauth2_client()
    if not client:
        return

    for attempt in range(3):
        try:
            client.create_tweet(text=tweet, user_auth=False)
            update_repo_var.update_repo_var(stats['game_date'])
            break
        except Exception as e:
            print(f"Twitter API Error (Attempt {attempt + 1}/3): {e}")
            if attempt < 2:
                time.sleep(5)
            else:
                print("Failed to send tweet after 3 attempts.")

check_and_tweet()

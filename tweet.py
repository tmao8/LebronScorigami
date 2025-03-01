import tweepy
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.library.parameters import SeasonAll
import os
import update_repo_var

# Twitter API credentials
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

# Set up Twitter API
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)


custom_headers = {
    'Host': 'stats.nba.com',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'https://www.nba.com',
    'Referer': 'https://www.nba.com/',
}

# Function to fetch LeBron's latest game stats and compare with history
def get_lebron_stats():
    logs = playergamelog.PlayerGameLog(player_id='2544', season=SeasonAll.all, headers=custom_headers, timeout=100).get_data_frames()[0]
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
    if stats['count'] == 2:
        end = 'nd'
    elif stats['count'] == 3:
        end = 'rd'
    if stats['count'] >= 1:
        tweet = (f"No Scorigami. LeBron James just recorded a stat line of {stat_line} for the {stats['count'] + 1}{end} time! He most recently achieved this stat line on {stats['most_recent']}🏀")
    else:
        tweet = (f"🚨 SCORIGAMI! 🚨 LeBron James just achieved a new stat line: {stat_line}! 🔥 #striveforgreatness🚀 #thekidfromakron👑 #jamesgang👑 #bronknows")
    client.create_tweet(text=tweet)
    update_repo_var.update_repo_var(stats['game_date'])

check_and_tweet()

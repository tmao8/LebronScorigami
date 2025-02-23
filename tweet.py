import tweepy
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.library.parameters import SeasonAll
import os


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

def get_last_tweet_date():
    try:
        with open('last_tweet_date.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None

def save_last_tweet_date(date):
    with open('last_tweet_date.txt', 'w') as f:
        f.write(date)

# Function to fetch LeBron's latest game stats and compare with history
def get_lebron_stats():
    logs = playergamelog.PlayerGameLog(player_id='2544', season=SeasonAll.all).get_data_frames()[0]
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
    if not stats or get_last_tweet_date() == stats['game_date']:
        return
    stat_line = f"{stats['points']}PTS {stats['rebounds']}REB {stats['assists']}AST"
    if stats['count'] >= 1:
        tweet = (f"LeBron James just recorded a stat line of {stat_line} for the {stats['count'] + 1}th time! He most recently achieved this stat line on {stats['most_recent']}🏀")
    else:
        tweet = (f"LeBron James just achieved a new stat line: {stat_line}! 🏀 This is the first time ever! 🔥 #striveforgreatness🚀 #thekidfromakron👑 #jamesgang👑 #bronknows")
    client.create_tweet(text=tweet)
    save_last_tweet_date(stats['game_date'])

check_and_tweet()
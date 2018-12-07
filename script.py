import requests
import trueskill
import itertools

# The 10 players that are playing in the game.
players = [
    'gaR',
    'all3nvan',
    'edzwoo',
    'idontcareeee',
    'dat hass',
    'Ngoskills',
    'cerealcereal',
    'CoolCoachDan',
    'Arata Y',
    'bakarich',
]

# Pull match data.
url = 'https://league-tracker-api-stage.herokuapp.com/single_page_app_initializations'
response = requests.get(url).json()

# Build lookup maps.
summoner_id_to_name = {}
for sid, obj in response['summoners'].iteritems():
    summoner_id_to_name[int(sid)] = obj['name']

summoner_name_to_id = {name: sid for sid, name in summoner_id_to_name.iteritems()}

summoner_id_to_rating = {}
for sid in summoner_id_to_name.iterkeys():
    summoner_id_to_rating[int(sid)] = trueskill.Rating()

# Sort games by create time.
sorted_games = [g for g in response['games'].itervalues()]
sorted_games.sort(key=lambda o: o['createTime'])

# Iterate through all games and calculate ratings.
for game in sorted_games:
    winning_team = []
    losing_team = []
    for pid in game['gameParticipantIds']:
        if response['gameParticipants'][pid]['win']:
            winning_team.append(response['gameParticipants'][pid]['summonerId'])
        else:
            losing_team.append(response['gameParticipants'][pid]['summonerId'])

    winning_team_ratings = [summoner_id_to_rating[p] for p in winning_team]
    losing_team_ratings = [summoner_id_to_rating[p] for p in losing_team]

    new_winning_team_ratings, new_losing_team_ratings =  trueskill.rate([
        winning_team_ratings, losing_team_ratings], ranks=[0, 1])

    for p, r in zip(winning_team, new_winning_team_ratings):
        summoner_id_to_rating[p] = r
    for p, r in zip(losing_team, new_losing_team_ratings):
        summoner_id_to_rating[p] = r

# Generate a sorted ranking.
rankings = [(summoner_id_to_name[sid], trueskill.expose(rating)) for sid, rating in summoner_id_to_rating.iteritems()]
rankings.sort(reverse=True, key=lambda t: t[1])
for r in rankings:
    print r[0], r[1]

# Calculate match quality for all possible combinations of teams.
qualities = []
all_player_ids = set([summoner_name_to_id[p] for p in players])
for left_team in itertools.combinations(all_player_ids, 5):
    right_team = set(all_player_ids) - set(left_team)

    left_team_names = [summoner_id_to_name[p] for p in left_team]
    right_team_names = [summoner_id_to_name[p] for p in right_team]

    left_team_ratings = [summoner_id_to_rating[p] for p in left_team]
    right_team_ratings = [summoner_id_to_rating[p] for p in right_team]

    quality = trueskill.quality([left_team_ratings, right_team_ratings])
    qualities.append((quality, left_team_names, right_team_names))

qualities.sort(key=lambda t: t[0], reverse=True)

truncated = qualities[0:5]
for q in truncated:
    print q[0]
    print q[1]
    print q[2]

import game_objects
from pymongo import MongoClient


def connect():
    client = MongoClient('localhost', 27017)
    db = client.space_invaders.users
    return db


def upload_user(stats):
    db = connect()
    data = db.find_one({"username": stats.username})
    if data:
        stats.records = data["records"]
        stats.killed_enemies = data["killed_enemies"]
        stats.played_games = data["played_games"]
    else:
        stats.records = [0, 0, 0, 0, 0]
        stats.killed_enemies = 0
        stats.played_games = 0
        save_user(stats)


def save_user(stats):
    db = connect()
    db.update({'username': stats.username},
              {'username': stats.username, 'records': stats.records,
               'killed_enemies': stats.killed_enemies,
               'played_games': stats.played_games}, upsert=True)


def delete_user(username):
    db = connect()
    db.remove({'username': username}, True)


def get_global_records():
    db = connect()
    users = db.find()
    tops = []
    for user in users:
        for i in range(game_objects.Statistics.RECORDS_COUNT):
            tops.append([user["records"][i], user["username"]])
    tops.sort(key=lambda x: x[0], reverse=True)
    for i in range(game_objects.Statistics.RECORDS_COUNT):
        if tops[i][0] == 0:
            tops[i] = ["-", "-"]
    return tops[:game_objects.Statistics.RECORDS_COUNT]
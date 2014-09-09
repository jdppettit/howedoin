from models import *
from flask import *
from dateutil.relativedelta import relativedelta

import datetime

'''
1 = Good
2 = Okay
3 = Bad
'''

def getRatingsPerDay(account_id):
    now = datetime.datetime.now()
    week_ago = now - datetime.timedelta(days=7)
    yesterday = now - datetime.timedelta(days=1)
    two_ago = now - datetime.timedelta(days=2)
    three_ago = now - datetime.timedelta(days=3)
    four_ago = now - datetime.timedelta(days=4)
    five_ago = now - datetime.timedelta(days=5)
    six_ago = now - datetime.timedelta(days = 6)
    
    weekAgoRatings = Rating.query.filter_by(account_id=account_id).filter(Rating.date>=week_ago).filter(Rating.date<six_ago).all()
    yesterdayRatings = Rating.query.filter_by(account_id=account_id).filter(Rating.date>=yesterday).filter(Rating.date<now).all()
    twoAgoRatings = Rating.query.filter_by(account_id=account_id).filter(Rating.date>=two_ago).filter(Rating.date<yesterday).all()
    threeAgoRatings = Rating.query.filter_by(account_id=account_id).filter(Rating.date>=three_ago).filter(Rating.date<two_ago).all()
    fourAgoRatings = Rating.query.filter_by(account_id=account_id).filter(Rating.date>=four_ago).filter(Rating.date<three_ago).all()
    fiveAgoRatings = Rating.query.filter_by(account_id=account_id).filter(Rating.date>=five_ago).filter(Rating.date<four_ago).all()
    sixAgoRatings = Rating.query.filter_by(account_id=account_id).filter(Rating.date>=six_ago).filter(Rating.date<five_ago).all()
    
    num_ratings = [0,0,0,0,0,0,0]
    happy_ratings = [0,0,0,0,0,0,0]
    okay_ratings = [0,0,0,0,0,0,0]
    bad_ratings = [0,0,0,0,0,0,0]

    for rating in yesterdayRatings:
        if rating.score == 1:
            happy_ratings[0] += 1
        elif rating.score == 2:
            okay_ratings[0] += 1
        elif rating.score == 3:
            bad_ratings[0] += 1
    
    for rating in twoAgoRatings:
        if rating.score == 1:
            happy_ratings[1] += 1
        elif rating.score == 2:
            okay_ratings[1] += 1
        elif rating.score == 3:
            bad_ratings[1] += 1

    for rating in threeAgoRatings:
        if rating.score == 1:
            happy_ratings[2] += 1
        elif rating.score == 2:
            okay_ratings[2] += 1
        elif rating.score == 3:
            bad_ratings[2] += 1

    for rating in fourAgoRatings:
        if rating.score == 1:
            happy_ratings[3] += 1
        elif rating.score == 2:
            okay_ratings[3] += 1
        elif rating.score == 3:
            bad_ratings[3] += 1

    for rating in fiveAgoRatings:
        if rating.score == 1:
            happy_ratings[4] += 1
        elif rating.score == 2:
            okay_ratings[4] += 1
        elif rating.score == 3:
            bad_ratings[4] += 1

    for rating in sixAgoRatings:
        if rating.score == 1:
            happy_ratings[5] += 1
        elif rating.score == 2:
            okay_ratings[5] += 1
        elif rating.score == 3:
            bad_ratings[5] += 1

    for rating in weekAgoRatings:
        if rating.score == 1:
            happy_ratings[6] += 1
        elif rating.score == 2:
            okay_ratings[6] += 1
        elif rating.score == 3:
            bad_ratings[6] += 1


    num_ratings[0] = len(yesterdayRatings)
    num_ratings[1] = len(twoAgoRatings)
    num_ratings[2] = len(threeAgoRatings)
    num_ratings[3] = len(fourAgoRatings)
    num_ratings[4] = len(fiveAgoRatings)
    num_ratings[5] = len(sixAgoRatings)
    num_ratings[6] = len(weekAgoRatings)
    
    print num_ratings
    print happy_ratings
    print okay_ratings
    print bad_ratings

    return num_ratings, happy_ratings, okay_ratings, bad_ratings

'''
1 = Week
2 = Month
3 = Year
4 = All time
'''

def getLeaderboard(account_id, scale):
    scale = int(scale)
    users = User.query.filter_by(account_id=account_id).all()
    leaderboard = {}
    if scale == 1:
        time = datetime.datetime.now() - datetime.timedelta(weeks=1)
        ratings = Rating.query.filter_by(account_id=account_id).filter(Rating.date>=time).all()
        # week
        return 1
    elif scale == 2:
        time = datetime.datetime.now() - datetime.timedelta(months=1)
        ratings = Rating.query.filter_by(account_id=account_id).filter(Rating.date>=time).all()
        # month
        return 2
    elif scale == 3:
        time = datetime.datetime.now() - datetime.timedelta(years=1)
        ratings = Rating.query.filter_by(account_id=account_id).filter(Rating.date>=time).all()
        # year
        return 3
    elif scale == 4:
        ratings = Rating.query.filter_by(account_id=account_id).all()
        # all time
        return 4


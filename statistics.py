from models import *
from flask import *
from dateutil.relativedelta import relativedelta

import datetime

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
    num_ratings[0] = len(yesterdayRatings)
    num_ratings[1] = len(twoAgoRatings)
    num_ratings[2] = len(threeAgoRatings)
    num_ratings[3] = len(fourAgoRatings)
    num_ratings[4] = len(fiveAgoRatings)
    num_ratings[5] = len(sixAgoRatings)
    num_ratings[6] = len(weekAgoRatings)
    
    print num_ratings

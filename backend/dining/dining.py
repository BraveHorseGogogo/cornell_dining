# -*- coding: utf-8 -*-
"""
    Cornell Dining
    ~~~~~~~~~~~~~~

    It's the back-end code for Cornell Dining app
    :created by Tang Yu, Sep 26th, 2013
"""
# all the imports

import cx_Oracle
import time
import math
import threading
import urllib
import os
import glob
import sys
import datetime
import pytz
import smtplib
import urllib
import flask

from pytz import timezone
from hours import Hours
from datetime import timedelta
from sqlite3 import dbapi2 as sqlite3

from math import radians
from math import cos
from math import sin
from math import asin
from math import sqrt
from flask import abort
from flask import Flask
from flask import flash
from flask import g
from flask import json
from flask import redirect
from flask import request
from flask import session
from flask import url_for

# create Cornell Dining :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    ORACLE_HOST='sf-sas-db-003.serverfarm.cornell.edu',
    ORACLE_PORT=1521,
    ORACLE_SID='PRDH',
    ORACLE_USERNAME='kme_dining',
    ORACLE_PASSWORD='vra4dma$',
    SQLLITE_DB="./dining.sqlite",
    DEBUG=True,
    SECRET_KEY='CornellDiningBackEnd',
    USERNAME='admin',
    PASSWORD='LOveCORNELL!8023',
    EMAIL_SENDER='dining@cornell.edu',
    EMAIL_RECEIVERS=['yt438@cornell.edu'],
    EMAIL_SUBJECT='SUGGESTION FROM A STUDENT'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_sqlite_db():
    """Connects to the sqlite database."""
    rv = sqlite3.connect(app.config['SQLLITE_DB'])
    rv.row_factory = sqlite3.Row
    return rv

glob_hours = None

def get_hours():
    global glob_hours
    if glob_hours == None:
        glob_hours = Hours()
    return glob_hours

def get_sqlite_db():
    """Return sqllite database connection"""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_sqlite_db()
    return g.sqlite_db

def connect_oracle_db():
    dsn_tns = cx_Oracle.makedsn(app.config['ORACLE_HOST'], app.config['ORACLE_PORT'], app.config['ORACLE_SID'])
    con = cx_Oracle.connect('kme_dining','vra4dma$', dsn_tns)
    return con

def get_oracle_db():
    if not hasattr(g, 'oracle_db'):
        g.oracle_db = connect_oracle_db()
    return g.oracle_db

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

    if hasattr(g, 'oracle_db'):
        g.oracle_db.close()

calendar_url = []

def get_calendar_info():
   with app.app_context(): 
        sqlite_db = get_sqlite_db()
        sqlite_cur = sqlite_db.cursor()
        sqlite_cur.execute("SELECT id, ics_url FROM dining_halls")
        sqlite_entries = sqlite_cur.fetchall()
        for row in sqlite_entries:
            calendar_url.append(dict(file_name=str(row[0])+".ics",url=row[1]))


def update_calendar():

    threading.Timer(86400, update_calendar).start()
    timer = threading.Timer(86400, update_calendar)
    timer.daemon = False
    timer.start()
    """Delete all ics files"""
    for fl in glob.glob("./static/ics/*.ics"):
        os.remove(fl)

    with app.app_context():
        """Grab new ics files from Google Server"""
        hours = get_hours()
        for row in calendar_url:
            curr_name = row['file_name']
            urllib.urlretrieve(row['url'],"./static/ics/"+curr_name)
            #print curr_name
            # print row['url']
            hours.hours("./static/ics/"+curr_name)
    
def get_current_hour(diner_id):
    #now = datetime.datetime.now(pytz.utc)+timedelta(hours=14)
    #now = datetime.datetime.now()
    now = datetime.datetime.now(pytz.timezone('US/Eastern'))
    #sys.stderr.write(str(now))
    hours = get_hours()
    today_hour = hours.today_hour[str(diner_id)]
    for open_hour in today_hour:
        if now.time() >= open_hour['dtstart'].time() and now.time() <= open_hour['dtend'].time():
            return open_hour
    return None

def all_not_in_service_meal():
    result_array = []
    for x in xrange(1,11):
        x_not_array = not_in_service_meal(x)
        info_dict = dict(diner_id=x,not_meal=x_not_array)
        result_array.append(info_dict)
    return result_array


def not_in_service_meal(diner_id):
    hours = get_hours()
    today_hour = hours.today_hour[str(diner_id)]
    passed_meals = []
    now = datetime.datetime.now()
    for open_hour in today_hour:
        if now.time() > open_hour['dtend'].time():
            passed_meals.append(open_hour['event_type'])
    return passed_meals

def is_this_meal_in_service(meal):
    meal_str = meal.replace(" ","").lower()
    now = datetime.datetime.now()
    hours = get_hours
    today_hour = hours.today_hour[str(diner_id)]

def getDinersArray(cur_longitude,cur_latitude,sql_statement):
    sqlite_db = get_sqlite_db()
    sqlite_cur = sqlite_db.cursor()
    sqlite_cur.execute(sql_statement)
    sqlite_entries = sqlite_cur.fetchall()
    array = [];

    for row in sqlite_entries:
        # cur_distance = math.sqrt((float(row[3])-float(cur_longitude))**2+(float(row[4])-float(cur_latitude))**2)
        cur_distance = haversine(float(row[3]),float(row[4]),float(cur_longitude),float(cur_latitude))
        current_hour = get_current_hour(row[0])
        close_at = ""
        is_open = 0
        current_meal = ""
        if current_hour != None:
            close_at=current_hour['dtend'].strftime('%I:%M %p')
            is_open=1
            current_meal = current_hour['event_type']
        if is_open == 0:
            continue
        hall_info = dict(
                diner_id=row[0],
                diner_name=row[1],
                diner_desc=row[2],
                close_at=close_at,
                is_open=is_open,
                current_meal=current_meal,
                diner_location=dict(longitude=row[3],latitude=row[4]),
                diner_distance=cur_distance
            )
        array.append(hall_info)
    array = sorted(array, key=lambda hall_itr: float(hall_itr['diner_distance']),reverse=False)
    return array

@app.route("/get_all_diners.json")
def getAllDiners():
    cur_longitude = float(request.args['longitude'])
    cur_latitude = float(request.args['latitude'])    
    sqlite_db = get_sqlite_db()
    sqlite_cur = sqlite_db.cursor()
    sqlite_cur.execute('SELECT id, name, brief_intro, longitude, latitude, position FROM dining_halls')
    sqlite_entries = sqlite_cur.fetchall()
    array = [];

    for row in sqlite_entries:
        # cur_distance = math.sqrt((float(row[3])-float(cur_longitude))**2+(float(row[4])-float(cur_latitude))**2)
        cur_distance = haversine(float(row[3]),float(row[4]),float(cur_longitude),float(cur_latitude))
        current_hour = get_current_hour(row[0])
        close_at = ""
        is_open = 0
        current_meal = ""
        if current_hour != None:
            close_at=current_hour['dtend'].strftime('%I:%M %p')
            is_open = 1
            current_meal = current_hour['event_type']
        hall_info = dict(
                diner_id=row[0],
                diner_name=row[1],
                diner_desc=row[2],
                close_at=close_at,
                is_open=is_open,
                current_meal=current_meal,
                diner_location=dict(longitude=row[3],latitude=row[4]),
                diner_distance=cur_distance,
                position=row[5]
            )
        array.append(hall_info)
    north_array = []
    west_array = []
    central_array = []
    for hall_itr in array:
        if hall_itr['position'] == 'North':
            north_array.append(hall_itr)
        elif hall_itr['position'] == 'West':
            west_array.append(hall_itr)
        elif hall_itr['position'] == 'Central':
            central_array.append(hall_itr)
    north_dict = dict(campus_name='North',
                      diners=north_array)
    west_dict = dict(campus_name='West',
                      diners=west_array)
    central_dict = dict(campus_name='Central',
                      diners=central_array)
    result_array = [north_dict, west_dict, central_dict]

    return json.dumps(result_array)

@app.route("/get_info.json")
def getInfo():
    diner_id = int(request.args['diner_id'])
    
    """
    For hall_id > 10, there's no menu info
    For hall_id < 10, ther will be menu in database
    So, divide the get_info into 2 parts, each deal with a case
    """
    oracle_db = get_oracle_db()
    sqlite_db = get_sqlite_db()
    oracle_curs = oracle_db.cursor()
    sqlite_curs = sqlite_db.cursor()
    now = datetime.datetime.now()
    date_string = now.strftime("%Y-%m-%d")
    if diner_id > 10:
        images = sqlite_curs.execute("SELECT picture_url FROM hall_pictures WHERE hall_id = {0}".format(diner_id)).fetchall()
        image_array = []
        for image_itr in images:
            image_array.append(image_itr[0])

        basic_info = sqlite_curs.execute("SELECT intro, number, location, longitude, latitude FROM dining_halls WHERE id = {0}".format(diner_id)).fetchall()
    

        basic_info_tuple = basic_info[0]
        current_hour = get_current_hour(diner_id)
        current_meal=""
        if current_hour != None:
            current_meal = current_hour['event_type']
        hours = get_hours()
        seven_day_array = []
        for day_itr in xrange(0,7):
            if day_itr == 0:
                future_hour = hours.today_hour[str(diner_id)]
            else:
                future_hour = hours.next_six_days_hour[str(day_itr)][str(diner_id)]
            future_hour_array = []
            for hour_itm in future_hour:
                future_hour_itm = dict(start=hour_itm['dtstart'].strftime('%I:%M%p'),end=hour_itm['dtend'].strftime('%I:%M%p'),event_type=hour_itm['event_type'],is_limited=hour_itm['is_limited'])
                future_hour_array.append(future_hour_itm)
            hours = get_hours()
            future_hour_array = sorted(future_hour_array, key = lambda x: hours.meal_dict[x['event_type']],reverse=False)
            seven_day_array.append(dict(day_offset=day_itr,has_menu=0,info=future_hour_array))
        
        hall_info = dict(
            description=basic_info_tuple[0],
            hall_id=diner_id,
            current_meal=current_meal,
            longitude=basic_info_tuple[3],
            latitude=basic_info_tuple[4],
            images=image_array,
            Contact=dict(phone_number=basic_info_tuple[1],location=basic_info_tuple[2]),
            seven_day_info=seven_day_array
        )
        return json.dumps(hall_info) 
        #return json.dumps(basic_info_tuple)


    week_after = now + datetime.timedelta(days=6)
    week_after_string = week_after.strftime("%Y-%m-%d")
    menus = oracle_curs.execute("SELECT FORMAL_NAME, MEAL, COURSE, EVENTDATE FROM dining.menudetailweb WHERE UNITID = {0} and EVENTDATE >= '{1}' AND EVENTDATE <= '{2}'".format(diner_id, date_string,week_after_string)).fetchall()

    not_serve_meals = not_in_service_meal(diner_id)
    different_day_menu = dict()
    for menu_itr in menus:
        day_diff = int((datetime.datetime.strptime(menu_itr[3], '%Y-%m-%d').date() - datetime.datetime.now().date()).days)
        meal_name_dict = different_day_menu.get(str(day_diff))
        if meal_name_dict == None:
            meal_name_dict = dict()
            different_day_menu[str(day_diff)] = meal_name_dict

        menu_str = menu_itr[1].replace(" ","").lower()
        is_menu_serve = 1
        if day_diff == 0:
            for not_itm in not_serve_meals:
                if menu_str == not_itm:
                    is_menu_serve = 0
                    break
            if is_menu_serve == 0:
                continue
        menu_array = meal_name_dict.get(menu_str)
        if menu_array == None:
            menu_array = []
            meal_name_dict[menu_str] = menu_array
        # course_item = dict(item=menu_itr[0].replace("&nbsp;",""),station=menu_itr[2].replace("&nbsp;",""))
        course_item = dict(item=menu_itr[0],station=menu_itr[2])
        # sys.stderr.write(str(course_item)+"\n")
        menu_array.append(course_item)
    #sys.stderr.write(str(different_day_menu))
    menu_result_dict = dict()
    for diff_str, meal_name_dict in different_day_menu.iteritems():

        menu_result_array = menu_result_dict.get(diff_str)
        if menu_result_array == None:
            menu_result_array = []
            menu_result_dict[diff_str] = menu_result_array
        for key, value in meal_name_dict.iteritems():
            '''
            course_name_dict stores the struct { station: "salad station", items: ["food1","food2"]}
            '''
            course_name_dict = dict()
            for meal_itr in value:
                course_array = course_name_dict.get(meal_itr["station"])
                if course_array == None:
                    course_array = []
                    course_name_dict[meal_itr["station"]] = course_array
                course_array.append(meal_itr["item"])
            # sys.stderr.write(str(course_name_dict)+"\n")
            '''
            convert course_name_dict to an array
            '''
            cur_meal_menu = []
            for key2, value2 in course_name_dict.iteritems():
                cur_menu_item = dict(
                    station=key2,
                    items=value2
                    )
                cur_meal_menu.append(cur_menu_item)
            menu_item = dict(
                meal=key,
                menu_item=cur_meal_menu
                )
            menu_result_array.append(menu_item)

    current_hour = get_current_hour(diner_id)
    current_meal=""
    if current_hour != None:
        current_meal = current_hour['event_type']
    hours = get_hours()
    
    images = sqlite_curs.execute("SELECT picture_url FROM hall_pictures WHERE hall_id = {0}".format(diner_id)).fetchall()
    image_array = []
    for image_itr in images:
        image_array.append(image_itr[0])

    basic_info = sqlite_curs.execute("SELECT intro, number, location, longitude, latitude FROM dining_halls WHERE id = {0}".format(diner_id)).fetchall()
    

    basic_info_tuple = basic_info[0]

    seven_day_array = []
    for day_itr in xrange(0,7):
        if day_itr == 0:
            future_hour = hours.today_hour[str(diner_id)]
        else:
            future_hour = hours.next_six_days_hour[str(day_itr)][str(diner_id)]
        # sys.stderr.write(str(menu_result_dict)+"\n")
        future_menu = menu_result_dict.get(str(day_itr))
        if future_menu == None:
           future_menu = []
        future_array = []
        for hour_itm in future_hour:
            menu_for_hour = [] #None
            for future_menu_itm in future_menu:
                if future_menu_itm['meal'] == hour_itm['event_type']:
                    menu_for_hour=future_menu_itm
                    break
            future_hour_itm = dict(start=hour_itm['dtstart'].strftime('%I:%M%p'),end=hour_itm['dtend'].strftime('%I:%M%p'),event_type=hour_itm['event_type'],is_limited=hour_itm['is_limited'],menu=menu_for_hour)
            future_array.append(future_hour_itm)
        hours = get_hours()
        future_array = sorted(future_array,key = lambda x: hours.meal_dict[x['event_type']],reverse=False) 
        seven_day_array.append(dict(day_offset=day_itr,has_menu=1,info=future_array))

    hall_info = dict(
        description=basic_info_tuple[0],
        hall_id=diner_id,
        longitude=basic_info_tuple[3],
        latitude=basic_info_tuple[4],
        current_meal=current_meal,
        images=image_array,
        Contact=dict(phone_number=basic_info_tuple[1],location=basic_info_tuple[2]),
        seven_day_info=seven_day_array
    )
    return json.dumps(hall_info) 
    
@app.route("/get_nearby.json")
def getNearby():
    cur_longitude = float(request.args['longitude'])
    cur_latitude = float(request.args['latitude'])
    array = getDinersArray(cur_longitude, cur_latitude, 'SELECT id, name, brief_intro, longitude, latitude FROM dining_halls')
    new_array = array[0:31]
    return json.dumps(new_array)

@app.route("/get_favorite.json")
def getFavoriteFood():
    favorite_food_list = request.args["favorite_food"].split("*")
    fav_food_string = "("
    itr = 0
    favorite_food_list_len = len(favorite_food_list)
    for fav_itm in favorite_food_list:
        print fav_itm
        fav_itm_string = fav_itm.replace("%20"," ")
        fav_itm_string = fav_itm_string.replace("'","''")
        fav_itm_string = fav_itm_string.replace("%27","''")
        fav_itm_string = fav_itm_string.replace("%26","&")
        print fav_itm_string
        fav_food_string += "'"
        fav_food_string += fav_itm_string
        # fav_food_string += fav_itm.replace("%20"," ")
        # fav_food_string += "&nbsp;&nbsp;"
        fav_food_string += "'"
        if not itr == favorite_food_list_len-1:
            fav_food_string += ","
        itr = itr+1
    fav_food_string += ")"
    #sys.stderr.write(fav_food_string+"\n")
    date_string = time.strftime("%Y-%m-%d")
    oracle_db = get_oracle_db()
    oracle_curs = oracle_db.cursor()
    exe_string = "SELECT FORMAL_NAME, EVENTDATE, MEAL, UNITID FROM dining.menudetailweb WHERE FORMAL_NAME IN {0} AND EVENTDATE >= '{1}' ORDER BY EVENTDATE".format(fav_food_string, date_string)

    #sys.stderr.write(exe_string)
    fav_foods = oracle_curs.execute(exe_string).fetchall()
    all_not_meal = all_not_in_service_meal()
    #sys.stderr.write(str(fav_foods))
    oracle_fav_food_array = []
    for fav_food_itm in fav_foods:
        if datetime.datetime.strptime(fav_food_itm[1], '%Y-%m-%d').date() > datetime.datetime.now().date():
            oracle_fav_food_array.append(fav_food_itm)
        else :
            not_meal_array = None
            for not_meal_itm in all_not_meal:
                if not_meal_itm['diner_id'] == int(fav_food_itm[3]):
                    not_meal_array = not_meal_itm['not_meal']
                break
            if not_meal_array != None:
                is_item_in_service = 1
                for not_meal_itm in not_meal_array:
                    if fav_food_itm[2].replace(" ","").lower() == not_meal_itm:
                        is_item_in_service = 0
                        break
                if is_item_in_service == 1:
                    oracle_fav_food_array.append(fav_food_itm)
            else:
                oracle_fav_food_array.append(fav_food_itm)
    
    global glob_hall_id_dict
    all_fav_foods = []
    for fav_food_itm in oracle_fav_food_array:
        fav_food_dict = dict(diner_id=fav_food_itm[3],diner_name=glob_hall_id_dict["h{0}".format(fav_food_itm[3])],meal=fav_food_itm[2],fav_food=fav_food_itm[0],serve_date=fav_food_itm[1])
        all_fav_foods.append(fav_food_dict)

    return json.dumps(all_fav_foods)

@app.route("/search.json")
def searchDiningHalls():
    key_words = request.args['key_word']
    key_word_list = key_words.split("*")
    cur_longitude = float(request.args['longitude'])
    cur_latitude = float(request.args['latitude'])

    now = datetime.datetime.now()
    week_after = now + datetime.timedelta(days=6)
    date_string = now.strftime("%Y-%m-%d")
    week_after_string = week_after.strftime("%Y-%m-%d")
    like_string = "("
    like_string_len = len(key_word_list)
    like_itr = 0
    for key_itm in key_word_list:
        like_string += "LOWER(FORMAL_NAME) LIKE LOWER('%"
        like_string += key_itm
        like_string += "%')"
        if not like_itr == like_string_len - 1:
            like_string += " OR "
        like_itr += 1
    like_string += ")"

    oracle_db = get_oracle_db()
    oracle_curs = oracle_db.cursor()
    """
    test_str = "SELECT UNITID, MEAL, FORMAL_NAME, EVENTDATE, COURSE FROM dining.menudetailweb WHERE {0} AND EVENTDATE >= '{1}' AND EVENTDATE <= '{2}'".format(like_string,date_string,week_after_string) + "\n"
    sys.stderr.write(test_str)
    """
    meal_info = oracle_curs.execute("SELECT UNITID, MEAL, FORMAL_NAME, EVENTDATE, COURSE FROM dining.menudetailweb WHERE {0} AND EVENTDATE >= '{1}' AND EVENTDATE <= '{2}'".format(like_string,date_string,week_after_string)).fetchall()
    in_string = "("
    for oracle_itm in meal_info:
        in_string += str(oracle_itm[0])
        in_string += ","
    if len(in_string) > 1:
        in_string = in_string[:-1]
    in_string += ")"
    sqlite_db = get_sqlite_db()
    sqlite_cur = sqlite_db.cursor()
    # sys.stderr.write('SELECT id, name, longitude, latitude FROM dining_halls WHERE id IN {0}'.format(in_string))
    sqlite_cur.execute('SELECT id, name, longitude, latitude FROM dining_halls WHERE id IN {0}'.format(in_string))
    sqlite_entries = sqlite_cur.fetchall()
    diners_array = [];

    for row in sqlite_entries:
        # cur_distance = math.sqrt((float(row[2])-float(cur_longitude))**2+(float(row[3])-float(cur_latitude))**2)
        cur_distance = haversine(float(row[2]),float(row[3]),float(cur_longitude),float(cur_latitude))
        hall_info = dict(
                diner_id=row[0],
                diner_name=row[1],
                diner_location=dict(longitude=row[2],latitude=row[3]),
                diner_distance=cur_distance
            )
        diners_array.append(hall_info)
    # sorted(array, key=lambda hall_itr: hall_itr['diner_distance'],reverse=False)
    all_not_meal = all_not_in_service_meal()
    search_result_array = []
    for oracle_itm in meal_info:
        if not datetime.datetime.strptime(oracle_itm[3], '%Y-%m-%d').date() > datetime.datetime.now().date():
            not_meal_array = None
            for not_meal_itm in all_not_meal:
                if not_meal_itm['diner_id'] == int(oracle_itm[0]):
                    not_meal_array = not_meal_itm['not_meal']
                    break
            if not_meal_array != None:
               is_this_meal_in_service = 1
               for not_meal_itm in not_meal_array:
                   if oracle_itm[1].replace(" ","").lower() == not_meal_itm:
                       is_this_meal_in_service = 0
                       break
               if is_this_meal_in_service == 0:
                   continue
        for hall_info_itm in diners_array:
            if hall_info_itm['diner_id'] == oracle_itm[0] :
                # item_string = oracle_itm[2].replace("&nbsp;","")
                item_string = oracle_itm[2]
                priority = 0
                for key_list_item in key_word_list:
                    if key_list_item.find(key_list_item) != -1:
                        priority += 1
                # return_result_info = dict(diner_id=oracle_itm[0],diner_name=hall_info_itm['diner_name'],diner_location=hall_info_itm['diner_location'],diner_distance=hall_info_itm['diner_distance'],meal=oracle_itm[1],item=oracle_itm[2].replace("&nbsp;",""),station=oracle_itm[4].replace("&nbsp;",""),serve_date=oracle_itm[3],priority=priority)
                return_result_info = dict(diner_id=oracle_itm[0],diner_name=hall_info_itm['diner_name'],diner_location=hall_info_itm['diner_location'],diner_distance=hall_info_itm['diner_distance'],meal=oracle_itm[1],item=oracle_itm[2],station=oracle_itm[4],serve_date=oracle_itm[3],priority=priority)
                search_result_array.append(return_result_info)
    search_result_array = sorted(search_result_array, key = lambda x: (datetime.datetime.strptime(x['serve_date'],'%Y-%m-%d').date(), x['diner_distance'], x['priority']))[:15]
    #search_result_array = sorted(search_result_array, key=lambda x: (x['serve_date'], x['diner_distance']))
    return json.dumps(search_result_array)

    
glob_hall_id_dict = dict(h1='Cook House Dining Room',
                    h9='104 West!',
                    h10='Okenshields',
                    h4='Rose House Dining Room',
                    h5="Hans Bethe House - Jansen's Dining Room",
                    h8='Risley Dining',
                    h2='Becker House Dining Room',
                    h6='Robert Purcell Marketplace Eatery',
                    h3='Keeton House Dining Room',
                    h7='North Star',
                    h11='Bear Necessities',
                    h12="Carol's Cafe",
                    h13='Amit Bhatia Libe Cafe',
                    h14='Atrium Cafe',
                    h15='Big Red Barn',
                    h16='Cascadeli',
                    h17='Cafe Jennie',
                    h18='Cornell Dairy Bar',
                    h19='Green Dragon',
                    h20="Goldie's Cafe",
                    h21='Ivy Room',
                    h22="Martha's Cafe",
                    h23="Mattins Cafe",
                    h24='One World Cafe',
                    h25="Rusty's",
                    h26='Sage Coffee Cart',
                    h27='Synapsis Cafe',
                    h28='Trillium',
                    h29='Trillium Express',
                    h30='Jansen’s Market',
                    h31='West Side Express')
@app.route('/comment.json', methods=['GET', 'POST'])
def comment():
    if request.method == 'POST':
        netID = str(request.form['netID'])
        netID = netID.replace("'","''")
        commentContent = str(request.form['commentContent'])
        commentContent = urllib.unquote(commentContent)
        commentContent = commentContent.replace("'","''")
        hallID = int(request.form['hallID'])
    elif request.method == 'GET':
        netID = request.args['netID']
        netID = netID.replace("'","''")
        commentContent = str(request.args['commentContent'])
        commentContent = urllib.unquote(commentContent)
        commentContent = commentContent.replace("'","''")
        hallID = int(request.args['hallID'])
    sqlite_db = get_sqlite_db()
    sqlite_cur = sqlite_db.cursor()
    sqlite_cur.execute("INSERT INTO comments (content, net_id, hall_id) VALUES ('{0}', '{1}', {2})".format(commentContent, netID, hallID))
    sqlite_db.commit()
    global glob_hall_id_dict
    # sys.stderr.write("hello comment")
    try:
        now = datetime.datetime.now()
        commentContent = commentContent.replace("''","'")
        mailMessage = "Subject: {0}\n\n {1} said {2} about {3} at {4}".format(app.config['EMAIL_SUBJECT'],netID, commentContent, glob_hall_id_dict["h{0}".format(hallID)], str(now))
        smtpObj = smtplib.SMTP('localhost')
        # sys.stderr.write(app.config['EMAIL_SENDER'])
        #sys.stderr.write(app.config['EMAIL_RECEIVERS'])
        # sys.stderr.write(mailMessage)
        smtpObj.sendmail(app.config['EMAIL_SENDER'], app.config['EMAIL_RECEIVERS'], mailMessage)         
        # sys.stderr.write("Successfully sent email")
    except smtplib.SMTPException:
        sys.stderr.write("Error: unable to send email")
    return '{"status":200}'
    # commentFile = open('static/testData/comment.json')
    # return commentFile.read()



@app.route('/<path:path>')
def catch_all(path):
    return 'You want path: %s' % path

@app.route("/image")
def image():
    image_name = request.args['image_name']
    return flask.send_from_directory("./static/images",image_name)

if __name__ == '__main__':
    get_calendar_info()
    update_calendar()
    # app.run(host='0.0.0.0',port=80)
    app.run(host='0.0.0.0',port=80, use_reloader=False)

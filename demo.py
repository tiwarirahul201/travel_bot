from flask import Flask, jsonify,request,session
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import collections
import re
import urllib
import requests
import json
import requests
import shelve 
from urllib.request import Request, urlopen
from io import BytesIO
from rasa.nlu.model import Metadata, Interpreter
import json
import os 
import copy 
import random
import spacy
from sutime import SUTime
import datetime
import sys
import calendar



nlp = spacy.load("en_core_web_sm")

abspath = os.path.abspath(__file__)

ROOT_PATH = os.path.dirname(abspath)


interpreter = Interpreter.load(ROOT_PATH+"/models/nlu")

sutime = SUTime(mark_time_ranges=True, include_range=True)



def Intent(sentence,interpreter):
    sentence = re.sub(r"[^a-zA-Z0-9$£]+", ' ', sentence)

    answer = (interpreter.parse(sentence))

    dic = {}

    score = (answer['intent']['confidence'])
    ans = (answer['intent']['name'])

    person = []

    for j in range(len(answer['entities'])):
        if (answer['entities'][j]['entity'] == 'amenities'):
            amenities = (answer['entities'][j]['value'])
            dic['amenities'] = amenities
        if(answer['entities'][j]['entity'] == 'guest'):
            print(answer['entities'][j]['value'])
            guest = (answer['entities'][j]['value'])
            dic['guest'] = guest
        elif(answer['entities'][j]['entity'] == 'day'):
            day = (answer['entities'][j]['value'])
            dic['day'] = day
        elif(answer['entities'][j]['entity'] == 'currency'):
            currency = (answer['entities'][j]['value'])
            dic['currency'] = currency
        elif(answer['entities'][j]['entity'] == 'month'):
            month = (answer['entities'][j]['value'])
            dic['month'] = month
        elif(answer['entities'][j]['entity'] == 'person'):
            person_val = (answer['entities'][j]['value'])
            person.append(person_val)

    if person:
        if 'parents' in person:
            len_guest = len(person) + 1
        else :
            len_guest = len (person)
        # str1 = ' '.join(person)
        dic['person'] = str (len_guest) + ' people'

    return(ans,dic)


def clear_memory():
    session.pop('currency',None)
    session.pop('day', None)
    session.pop('guest', None)
    session.pop('amenities', None)
    session.pop('location', None)
    session.pop('intent', None)
    session.pop('check_in', None)
    session.pop('check_out_date', None)
    session.pop('month',None)
    session.pop('person',None)
    session.pop('flag',None)
    session.pop('a',None)
    session.pop('b',None)


def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        print('correct format')
        return(0)
    except ValueError:
        print("Incorrect data format, should be YYYY-MM-DD")
        return(1)

def time(sentence):
    ans = (json.dumps(sutime.parse(sentence), sort_keys=True, indent=4))
    ans = json.loads(ans)
    print((ans))
    return(ans)

def capture_entity(ans,ans1):

    if 'intent' not in session:
        session['intent'] = ans
        print(session.get('intent'))


    if 'day' in ans1:
        session['day'] = session.get('day', ans1['day'])
        print(session['day'])
   
    if 'amenities' in ans1:
        session['amenities'] = session.get('amenities', ans1['amenities'])
        print(session['amenities'])

    if 'guest' in ans1:
        session['guest'] = session.get('guest', ans1['guest'])
        print(session['guest'])

    if 'person' in ans1:
        session['guest'] = session.get('guest', ans1['person'])
        print(session['guest'])

    if 'currency' in ans1:
        session['currency'] = session.get('currency', ans1['currency'])
        print(session['currency'])

    if 'month' in ans1:
        session['month'] = session.get('month', ans1['month'])
        print(session['month'])




def Result(sentence):
    sent = sentence
    doc = nlp(sent)
    for ent in doc.ents:
        if(ent.label_ == 'GPE' or ent.label_ == 'LOC' ):
            session['location'] = session.get('loc',ent.text)
            print(session['location'])
        else:
            print('No location found')
 
    sentence = sentence.lower()
    time_value = time(sentence)
    for i in range(len(time_value)):
        if (time_value[i]['type'] == 'DATE'):
            valid_result = validate(time_value[i]['value'])
            if (valid_result == 0):
                check_in_date = time_value[i]['value']
                session['check_in'] = session.get('check_in', check_in_date)
                print(session['check_in'])
            else:
                a = (time(time_value[i]['value']))
                date = a[0]['value']
                a_split = date.split('-')
                print(a_split)
                if (len(a_split) == 2):
                    year = int(a_split[0].lstrip('0'))
                    month = int(a_split[1].lstrip('0'))
                    print(year,month)
                    last_friday = max(week[-3] for week in calendar.monthcalendar(year,month))
                    check_in_date = ('{}-{}-{:2}'.format(year, calendar.month_abbr[month], last_friday))
                    session['check_in'] = session.get('check_in', check_in_date)


    if (sentence.strip() == 'confirm'):
        ans = confirm_book()
        return(ans)

    elif(sentence.strip() == 'cancel'):
        ans = cancel_book()
        return(ans)

    elif(sentence.strip() == 'alter'):
        ans = alter_book()
        return(ans)

    if (sentence.strip() == 'days of stay'):
        day = get_day()
        session.pop('day', None)
        return(day)

    elif (sentence.strip() == 'no of guests'):
        guest = get_guest()
        session.pop('guest', None)
        return(guest)

    elif (sentence.strip() == 'budget'):
        currency = get_currency()
        session.pop('currency',None)
        return(currency)

    elif (sentence.strip() == 'location'):
        location = get_location()
        session.pop('location', None)
        return(location)

    elif (sentence.strip() == 'amenities'):
        amenities = get_amenities()
        session.pop('amenities', None)
        return(amenities)
  

    elif (sentence.strip() == 'check in date'):
        chk_in = get_check_in()
        session.pop('check_in', None)
        return(chk_in)




    ans,ans1 = Intent(sentence,interpreter)
   
    print(ans,ans1)

    capture_entity(ans,ans1)


    if(session['intent'] == 'hotel_book'):

        if 'day' not in session:
            day = get_day()
            return(day)

        if 'check_in' not in session:
            check_in = get_check_in()
            return(check_in)

        if 'guest' not in session:
            guest = get_guest()
            return(guest)


        if 'currency' not in session:
            currency = get_currency()
            return(currency)

        if 'amenities' not in session:
            amenities = get_amenities()
            return(amenities)


        if 'location' not in session:
            location = get_location()
            return(location)



        else:
            C_day = session.get('day')
            C_guest = session.get('guest')
            C_amenities = session.get('amenities')
            C_currency = session.get('currency')
            C_location = session.get('location')
            C_check_in = session.get('check_in')
            # C_check_out = session.get('check_out_date')
            day_dic = {'week' : 7, 'fortnight': 15 , 'weekend': 2}

            if C_day in day_dic.keys():
                C_day = str(day_dic[C_day])+' day' 

            # session['day'] = session.get('day',C_day)




            res = [int(i) for i in C_day.split() if i.isdigit()]

            print(res[0])
            print(type(res[0]))

            res2 = int(''.join([i for i in C_currency if  i.isdigit()]))
            print(res2)
            print(type(res2))


            res1 = ''.join([i for i in C_currency if not i.isdigit()])
            print(res1[0])
            print(type(res1[0]))


            ans = res1[0]+str(res[0] * res2) 

            print(ans)

            C_currency = ans

            # session['currency'] = session.get('currency',C_currency)




            # clear_memory()

            a = cofirmation_prompt(C_day,C_guest,C_location,C_amenities,C_currency,C_check_in)
            
            return(a)
            # return('Based on your budget of '+C_currency+' a hotel in '+C_location+' for '+C_guest+' with amenities like '+C_amenities+' for '+C_day+' is The Ritz-Carlton, Los Angeles')

    if(session['intent'] == 'greet'):
        clear_memory()
        return('Hello. I can help you with your hotel booking')

    if(session['intent'] == 'goodbye'):
        clear_memory()
        return('Thankyou it was great interacting with you.')
  
    if(session['intent'] == 'bot_challenge'):
        clear_memory()
        return('I am hotel booking bot.You can book your hotels with me.')

    else:
        clear_memory()
        return("Sorry I am unable to answer your query right now.I wil surely try to improve it.")



def get_day():
    b = ("Please provide your number days of stay .")
    return(b)

def get_amenities():
    b = ("Please select a must available amenities: <br> <a href='javascript:void(0)' class='response_back'>Swimming Pool</a> <a href='javascript:void(0)' class='response_back'>Laundry</a> <a href='javascript:void(0)' class='response_back'>Parking</a> <a href='javascript:void(0)' class='response_back'>Wifi</a>")
    return(b)

def get_guest():
    c = ("How many people will be in your party?")
    return(c)

def get_currency():
    c = ("Great, and how much would you like to spend per a night?")
    return(c)

def get_location():
    c = ("Please provide your location of stay.")
    return(c)

def get_check_in():
    d = ("Please enter check in date.")
    return(d)

def cofirmation_prompt(day,guest,location,amenity,budget,check_in):
    ans = ("Please confirm details provided by you : <br>Check in date:    "+check_in+" <br>Number of days:   "+day+"<br>No. of guest:    "+guest+"<br>Amenities:     "+amenity+"<br>Location:    "+location+"<br>Budget:     "+budget+"<br>  <a href='javascript:void(0)' class='response_back'> Confirm </a> <a href='javascript:void(0)' class='response_back'> Alter </a><a href='javascript:void(0)' class='response_back'> Cancel </a>")
    return(ans)

def confirm_book():
    C_day = session.get('day')
    C_guest = session.get('guest')
    C_amenities = session.get('amenities')
    C_currency = session.get('currency')
    C_location = session.get('location')
    C_check_in = session.get('check_in')


    day_dic = {'week' : 7, 'fortnight': 15 , 'weekend': 2}

    if C_day in day_dic.keys():
        C_day = str(day_dic[C_day])+' day' 

    # session['day'] = session.get('day',C_day)




    res = [int(i) for i in C_day.split() if i.isdigit()]

    print(res[0])
    print(type(res[0]))

    res2 = int(''.join([i for i in C_currency if  i.isdigit()]))
    print(res2)
    print(type(res2))


    res1 = ''.join([i for i in C_currency if not i.isdigit()])
    print(res1[0])
    print(type(res1[0]))


    ans = res1[0]+str(res[0] * res2) 

    print(ans)

    C_currency = ans


    answer_dic = {
     "Day of Stay": C_day,
     "Check in": C_check_in,
     "Guests": C_guest,
     "Amenities": C_amenities,
     "Budget": C_currency,
     "Location": C_location  
    }

    final_json = json.dumps(answer_dic , indent = 4)

    final_json = json.loads(final_json)

    print(final_json)
    print(type(final_json))

    clear_memory()

    return('Based on your budget of '+C_currency+' a hotel in '+C_location+' for '+C_guest+' with amenities like '+C_amenities+' for '+C_day+' starting from '+C_check_in+' is The Ritz-Carlton, Los Angeles')

def cancel_book():
    clear_memory()
    ans = 'Your booking has been cancelled.'
    return(ans)

def alter_book():
    ans = ("Please select a option which needs to be changed: <br> <a href='javascript:void(0)' class='response_back'> Days of Stay  </a> <a href='javascript:void(0)' class='response_back'> Budget </a> <a href='javascript:void(0)' class='response_back'> No of Guests </a> <a href='javascript:void(0)' class='response_back'> Location </a> <a href='javascript:void(0)' class='response_back'> Amenities </a><a href='javascript:void(0)' class='response_back'> Check in date </a>")
    return(ans)

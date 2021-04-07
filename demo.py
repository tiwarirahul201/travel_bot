from flask import Flask, jsonify,request,session
import spacy
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import collections
import os 
import re
import urllib
import requests
import json
import requests
import shelve 
from urllib.request import Request, urlopen
from io import BytesIO
import ssl
from rasa.nlu.model import Metadata, Interpreter
import json
import os 
import copy 
import random
import spacy

nlp = spacy.load("en_core_web_sm")

abspath = os.path.abspath(__file__)

ROOT_PATH = os.path.dirname(abspath)

interpreter = Interpreter.load(ROOT_PATH+"/models/nlu-20210326-120228/nlu")


def Intent(sentence,interpreter):
    sentence = re.sub(r"[^a-zA-Z0-9$]+", ' ', sentence)

    answer = (interpreter.parse(sentence))
    print(answer)
    dic = {}

    score = (answer['intent']['confidence'])
    ans = (answer['intent']['name'])


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


    return(ans,dic)


def clear_memory():
    session.pop('currency',None)
    session.pop('day', None)
    session.pop('guest', None)
    session.pop('amenities', None)
    session.pop('location', None)
    session.pop('intent', None)

def location_fetch(sentence):
    text = list()
    label = list()
    nlp2 = spacy.load("/home/rahul/Desktop/hotel/goldmodel")
    a = re.sub(r'[^\w]', ' ', sentence)
    doc1 = nlp2(a)

    for i in doc1.ents:
        text.append(i.text)

        
    ans = {'location': text}
    print(ans)
    return(text)

def test(sentence):
    print("the sentence is :" + sentence)


def Result(sentence):
    sent = sentence
    sentence = sentence.lower()
    currency_regex = re.compile(r"(?:[,\d][0-9]+[\£\$\€\₹| usd|usd]+.?\d*)")

    match = currency_regex.search(sentence)
    if match:
        session['currency'] = session.get('currency', match[0])
        print(session['currency'])

    ans,ans1 = Intent(sentence,interpreter)

    print(sent)


    doc = nlp(sent)
    for ent in doc.ents:
        if(ent.label_ == 'GPE' or ent.label_ == 'LOC' ):
            session['location'] = session.get('loc',ent.text)
            print(session['location'])
        else:
            print('No location found')
    
    print(ans,ans1)
    

    if 'intent' not in session:
        session['intent'] = ans
        # print(session.get('intent'))
  
    if 'day' in ans1:
        session['day'] = session.get('day', ans1['day'])
   
    if 'amenities' in ans1:
        session['amenities'] = session.get('amenities', ans1['amenities'])
        print(session['amenities'])

    if 'guest' in ans1:
        session['guest'] = session.get('guest', ans1['guest'])
        print(session['guest'])

    if 'currency' in ans1:
        session['currency'] = session.get('currency', ans1['currency'])
        print(session['currency'])


    print(session.get('intent'))



    if(session['intent'] == 'hotel_book'):

        if 'day' not in session:
            day = get_day()
            return(day)

        if 'amenities' not in session:
            amenities = get_amenities()
            return(amenities)

        if 'guest' not in session:
            guest = get_guest()
            return(guest)


        if 'currency' not in session:
            currency = get_currency()
            return(currency)

        if 'location' not in session:
            location = get_location()
            return(location)



        else:
            C_day = session.get('day')
            C_guest = session.get('guest')
            C_amenities = session.get('amenities')
            C_currency = session.get('currency')
            C_location = session.get('location')

            clear_memory()
            
            return('Based on your budget of '+C_currency+' a hotel in '+C_location+' for '+C_guest+' with amenities like '+C_amenities+' for '+C_day+' is The Ritz-Carlton, Los Angeles')

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
    b = ("Please select number of days of stay <br> <a href='javascript:void(0)' class='response_back'>1 Days </a> <a href='javascript:void(0)' class='response_back'>2 Days </a> <a href='javascript:void(0)' class='response_back'>3 Days </a> <a href='javascript:void(0)' class='response_back'>4 Days </a>")
    return(b)

def get_amenities():
    b = ("Please select a must available amenities: <br> <a href='javascript:void(0)' class='response_back'>Swimming Pool</a> <a href='javascript:void(0)' class='response_back'>Laundry</a> <a href='javascript:void(0)' class='response_back'>Parking</a> <a href='javascript:void(0)' class='response_back'>Wifi</a>")
    return(b)

def get_guest():
    c = ("Please select number of guests. <br> <a href='javascript:void(0)' class='response_back'>1 Person </a> <a href='javascript:void(0)' class='response_back'>2 People</a> <a href='javascript:void(0)' class='response_back'>3 People</a> <a href='javascript:void(0)' class='response_back'>4 People</a>")
    return(c)

def get_currency():
    c = ("Please select price range. <br> <a href='javascript:void(0)' class='response_back'>200$ </a> <a href='javascript:void(0)' class='response_back'>300$ </a> <a href='javascript:void(0)' class='response_back'>400$ </a> <a href='javascript:void(0)' class='response_back'>600$ </a>")
    return(c)

def get_location():
    c = ("Please select a country. <br> <a href='javascript:void(0)' class='response_back'>Nepal </a> <a href='javascript:void(0)' class='response_back'>London </a> <a href='javascript:void(0)' class='response_back'>India </a> <a href='javascript:void(0)' class='response_back'>Japan </a>")
    return(c)


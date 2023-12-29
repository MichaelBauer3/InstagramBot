# Michael Bauer
# Summer 2023
# Programming Project: Use API's to get a word of the day

import json
import requests
import random
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
import logging

cl = Client()
logger = logging.getLogger()

def login_user():
    """
    Attempts to login to Instagram using either the provided session information
    or the provided username and password.
    """
    instagram_user = "Micha3lBot"
    instagram_pass = "vebqo9-quwkag-mykvaR"
    
    session = cl.load_settings("session.json")

    login_via_session = False
    login_via_pw = False

    if session:
        try:
            cl.set_settings(session)
            cl.login(instagram_user, instagram_pass)

            # check if session is valid
            try:
                cl.get_timeline_feed()
            except LoginRequired:
                logger.info("Session is invalid, need to login via username and password")

                old_session = cl.get_settings()

                # use the same device uuids across logins
                cl.set_settings({})
                cl.set_uuids(old_session["uuids"])

                cl.login(instagram_user, instagram_pass)
            login_via_session = True
        except Exception as e:
            logger.info("Couldn't login user using session information: %s" % e)

    if not login_via_session:
        try:
            logger.info("Attempting to login via username and password. username: %s" % instagram_user)
            if cl.login(instagram_user, instagram_pass):
                login_via_pw = True
        except Exception as e:
            logger.info("Couldn't login user using username and password: %s" % e)

    if not login_via_pw and not login_via_session:
        raise Exception("Couldn't login user with either password or session")
    

def instagram(id, definition, pronun):

    followers = cl.user_followers(cl.user_id)
    followers_list = list(followers.keys())
    followers_list = [int(follower_id) for follower_id in followers_list]

    cl.direct_send(f"Todays word of the day is: {id}", followers_list)
    cl.direct_send(f"Pronounced: {pronun}", followers_list)

    num = 1
    for i in definition:
        cl.direct_send(str(num) + ". " + i, followers_list)
        num+=1        

def getPro(word):
    url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key=aa2ebf40-278d-463f-8f8a-f6122fcbed1a"
    r = requests.get(url)
    data = r.json()
    pronun = data[0].get("hwi").get("hw")

    return pronun

def getWord(file_name):
    with open(file_name, 'r') as file:
        word_list = file.read().splitlines()
    return random.choice(word_list)

def getID(word):
    url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key=aa2ebf40-278d-463f-8f8a-f6122fcbed1a"
    r = requests.get(url)
    data = r.json()
    id = data[0].get("meta").get("id")
    print(id)
    return id

def getDefs(word, file_name):
    url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key=aa2ebf40-278d-463f-8f8a-f6122fcbed1a"
    r = requests.get(url)
    data = r.json()
    definition = data[0].get("shortdef", ["No definition found"])

    while not definition:
        with open("/Users/michaelbauer/Documents/Outside Work/Summer Project 2023/JunkWords.txt", "a") as file:  
            file.write(str(word) + "\n")
        
        word = getWord(file_name).capitalize()
        url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key=aa2ebf40-278d-463f-8f8a-f6122fcbed1a"
        r = requests.get(url)
        data = r.json()
        definition = data[0].get("shortdef", [])

    return definition

def main():
    file_name = "/Users/michaelbauer/Documents/Outside Work/Summer Project 2023/WordList.txt"
    
    word = getWord(file_name).capitalize()
    
    id = getID(word)
    definition = getDefs(word, file_name)
    pronun = getPro(word)

    login_user()
    instagram(id, definition, pronun)
    print("Word Sent")
    
main()
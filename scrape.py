import json
import os
import time

import pymongo
import requests
from bs4 import BeautifulSoup

import mysecrets

def scrape(start,end,page):
    uri = mysecrets.URI
    client = pymongo.MongoClient(uri)
    db = client["Magic-DB"]
    deckcollection = db["Deck-Collection"]


    with open("log.txt","a") as logfile:
        logfile.write("\nLast Scrape:\n")
        logfile.write("Start Date: {0}\n".format(start))
        logfile.write("End Date: {0}\n".format(end))
        logfile.write("Pages Scraped: {0} - {1}".format(page,page))

    nextpage = True
    trackingpage = page - 1
    while nextpage:
        trackingpage += 1
        response = requests.get("https://www.mtgtop8.com/search?format=LE&date_start={0}&date_end={1}&current_page={2}".format(start,end,trackingpage))
        soup = BeautifulSoup(response.content, "html.parser")
        rawdeckdata = soup.find_all(class_ = "hover_tr")

        if rawdeckdata == []:
            nextpage = False
            return("Completed Scan pages {0} to {1}".format(page,trackingpage))
            break
        else:
            builddeckentries(rawdeckdata,deckcollection)


            with open("log.txt","a+") as logfile:
                logfile.seek(0, os.SEEK_END)
                logfile.seek(logfile.tell() - len(str(trackingpage-1)), os.SEEK_SET)
                logfile.truncate()
                logfile.write(str(trackingpage))



def builddeckentries(rawdeckdata,deckcollection):
    entrieslist = []
    for entry in rawdeckdata:
        column = entry.find_all("td")
        if column[4].find("img")["src"] == "/graph/bigstar.png":
            tournement_size = "4"
        else:
            tournement_size = str(len(column[4].find_all("img")))
        decklist = getdecklist(column[0].find_all("input")[1]["value"])
        deck = {
                "_id" : int(column[0].find_all("input")[1]["value"]),
                "url" : column[1].find("a")["href"],
                "archtype" : column[1].text.strip().encode().decode(encoding = "unicode_escape"),
                "player" : column[2].text.strip().encode().decode(encoding = "unicode_escape"),
                "event" : column[3].text.strip().encode().decode(encoding = "unicode_escape"),
                "tournement_size" : tournement_size,
                "place" : column[5].text.strip(),
                "date" : column[6].text.strip(),
                "deck_list" : decklist
                }
        deckcollection.update_one(deck, {"$set": deck}, upsert=True)
        time.sleep(.1)


def getdecklist(deckid):
    response = requests.get("https://www.mtgtop8.com/mtgo?d=%s" % deckid)
    decoded = response.content.decode(encoding= "unicode_escape").split("Sideboard")
    decklist = {"maindeck":{}, "sideboard":{}}
    listed = []
    if len(decoded) == 2:
        for half in decoded:
            listed.append(half.strip().split("\r\n"))
        for card in listed[0]:
            info = card.split(" ", 1)
            decklist["maindeck"][info[1]] = int(info[0])
        for card in listed[1]:
            info = card.split(" ", 1)
            decklist["sideboard"][info[1]] = int(info[0])
    return decklist

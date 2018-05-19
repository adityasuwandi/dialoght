#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import sys
import logging
import MySQLdb
import time

from bs4 import BeautifulSoup
from datetime import datetime

from flask import Flask, render_template
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
#des isch super

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)     #req = anfrage json
    print("Request:")
    print(json.dumps(req, indent=4))
    action = req.get("result").get("action")    # auslesen der action = wird nachher zum richtig zuerueckgeben fuer unterschiedliche intents verwendet
    query = req.get("result").get("resolvedQuery")    # auslesen der action = wird nachher zum richtig zuerueckgeben fuer unterschiedliche intents verwendet
    if action == "yahooWeatherForecast":
        res = processWeather(req)
    elif action == "searchOnLustenauAT":
        res = processSearchLustenauAT(req)
    elif action == "parkbadLustenau":
        res = processParkbadLustenau(req)
    elif action == "getAbfahrtszeiten":
        res = processAbfahrtszeiten(req)
    elif action == "openCurrentWeatherForecast":
        res = processCurrentOpenWeather(req)
    elif action == "openVorhersageWeatherForecast":
        res = processVorhersageOpenWeather(req)
    elif action == "newEvents":
        res = processNewEventsQuery(query, 256)
    elif action == "newEventsMusic":
        res = processNewEventsQuery(query, 255)
    elif action == "newEventsSport":
        res = processNewEventsQuery(query, 198)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r




######################## fallback search auf homepage ########################
def processSearchLustenauAT(req):
    userInput = req.get("result").get("resolvedQuery")
    print("Suchbegriff in processSearchLustenauAT:" + userInput)
    userInput = userInput.replace(" ", "%20")   # removing whitespaces

    if userInput == "FACEBOOK_MEDIA":
        return {
            "speech": "Tut mir leid :(. Mir wurde mitgeteilt, dass ich die Dateien anderer nicht lesen darf.",
            "displayText": "Tut mir leid :(. Mir wurde mitgeteilt, dass ich die Dateien anderer nicht lesen darf.",
            # "data": data,
            # "contextOut": [],
            "source": "lustenaubot"
        }
    else:
        return {
            "speech": "",
            "messages": [
            {
            "type": 0,
            "speech": "Tut mir leid, so gut bin ich leider noch nicht :(",
            "displayText": "Tut mir leid, so gut bin ich leider noch nicht :("
            },
            {
            "type": 0,
            "speech": "Vielleicht wirst du aber auf der Homepage der Marktgemeinde Lustenau fündig :)",
            "displayText": "Vielleicht wirst du aber auf der Homepage der Marktgemeinde Lustenau, oder im Lustenauer-Wiki fündig :)"
            },
            {
            "type": 0,
            "speech": "Homepage: " + "https://www.lustenau.at/de/search?q=" + userInput,
            "displayText": "Homepage: " + "https://www.lustenau.at/de/search?q=" + userInput
            }
            ],
            "source": "lustenaubot"
        }


#######################parki, vier kategorien -> eingestellt##################################
def processParkbadLustenau(req):
    userInput = req.get("result").get("resolvedQuery")
    userOutput = "Tut mir leid, da ist ein Fehler aufgetreten..."
    result = req.get("result")
    parameters = result.get("parameters")
    parkiInfo = parameters.get("parki")
    if parkiInfo == "oeffnungszeiten":
        userOutput = "Das Parkbad Lustenau hat an folgenden Tagen und Zeiten geöffnet: " + \
        "06. Mai bis 10. September 2017  \n" + \
        "Badezeit von 09.00 bis 20.00 Uhr, Einlass bis 19.30 Uhr \n" + \
        "Kurzbadezeit werktags von 12.00 bis 14.00 Uhr und täglich von 17.00 bis 20.00 Uhr"
    if parkiInfo == "preise":
        userOutput = "Eine Einzelkarte für Erwachsene kostet € 4,00. \n" + \
        "Genauere Informationen findest du unter: " + \
        "http://bit.ly/2sRP6m6"
    if parkiInfo == "kontakt":
        userOutput = "Du kannst das Parkbad unter folgenden Adressen kontaktieren: \n" + \
        "Telefon: +43 5577 8181-3210 | E-Mail: parkbad@lustenau.at"
    if parkiInfo == "information":
        userOutput = "Seit nunmehr 50 Jahren bietet das Lustenauer Parkbad" + \
        " uneingeschränkten Badespaß für Groß und Klein. Rund um Sportbecken, " + \
        "Riesenrutsche und Sprungturm sorgen ein Fußballplatz, Tischfußball und Tischtennis, "+ \
        "Beachvolleyball oder Freiluftschach für sportliche Abwechslung."
    return {
        "speech": userOutput,
        "displayText": userOutput,
        # "data": data,
        # "contextOut": [],
        "source": "lustenaubot"
    }





############################# openweather, wetterbericht neu ##################################

def processCurrentOpenWeather(req):
    url = "http://api.openweathermap.org/data/2.5/weather?q=Lustenau&lang=DE&APPID=62b7126dccc0b9861f6b5487f62f2c71"
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    result = urlopen(url).read()
    data = json.loads(result)
    res = makeCurrentOpenWeatherWebhookResult(data)
    return res


def makeCurrentOpenWeatherWebhookResult(data):
    main = data.get('main')
    temperature = main.get('temp')
    weather = data.get('weather')
    #icon = weather_aktuell[0].get('icon')
    description = weather[0].get('description')
    final_temperature = int(temperature) - 273  # von kelvin in celius
    aktuell = "Aktuelle Wetterlage: " + str(description) + ", die 🌡️Temperatur liegt bei " + str(final_temperature) + " °C"
    return {
        "speech": str(aktuell),
        "displayText": str(aktuell),
        "source": "lustenaubot"
    }


def processVorhersageOpenWeather(req):
    #vorhersage (tage bei cnt= aendern): https://openweathermap.org/forecast5
    url = "http://api.openweathermap.org/data/2.5/forecast/daily?q=LUSTENAU,AT&cnt=2&lang=DE&APPID=62b7126dccc0b9861f6b5487f62f2c71&format=json"
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    result = urlopen(url).read()
    data = json.loads(result)
    res = makeVorhersageOpenWeatherWebhookResult(data)
    return res

def makeVorhersageOpenWeatherWebhookResult(data):
    vorhersage = data.get('list')
    temperature_heute = vorhersage[0].get('temp')
    weather_today = vorhersage[0].get('weather')
    description_today = weather_today[0].get('description')
    temperature_heute = temperature_heute.get('day')
    final_temperature_heute = int(temperature_heute) - 273  # von kelvin in celius
    temperature_tomorrow = vorhersage[1].get('temp')
    temperature_tomorrow = temperature_tomorrow.get('day')
    final_temperature_tomorrow = int(temperature_tomorrow) - 273  # von kelvin in celius
    weather_tomorrow = vorhersage[1].get('weather')
    description_tomorrow = weather_tomorrow[0].get('description')
    einleitung = "☀️🌈❄️ Glücklicherweise hat mir die Wetterfee die Wettervorhersage verraten: 😊"
    heute = "Heute: " + str(description_today) + ", der 🌡️Tageshöchstwert liegt bei " + str(final_temperature_heute) + " °C"
    morgen = "Morgen: " + str(description_tomorrow) + ", der 🌡️Tageshöchstwert liegt bei " + str(final_temperature_tomorrow) + " °C"
    return {
        "speech": "",
        "messages": [
        {
        "type": 0,
        "speech": str(einleitung),
        "displayText": str(einleitung)
        },
        {
        "type": 0,
        "speech": str(heute),
        "displayText": str(heute)
        },
        {
        "type": 0,
        "speech": str(morgen),
        "displayText": str(morgen)
        }
        ],
        "source": "lustenaubot"
    }

####### holt abfhartszeiten von haltestelle, umwandlung in eigener funktion von name -> id #######
def processAbfahrtszeiten(req):
    # buhslatestellen entity -> wird in id umgewandelt ->
    # holt tabelle aus abfahrtszeiten.at -> output formatiert
    userInput = req.get("result").get("resolvedQuery")
    bushaltestelle = req.get("result").get("parameters").get("bushaltestellen")
    print (bushaltestelle)
    haltenstelle_id = getIDfromHaltstelle(bushaltestelle)
    createdUrl = "http://www.abfahrtszeiten.at/index.cfm?job=dsp&bk=1%2C2&htext=&HstId=" + haltenstelle_id
    html = urlopen(createdUrl).read()
    soup = BeautifulSoup(html)
    tables = soup.findAll("table", { "class" : "cinfo" })
    retValue = ""
    count = 0
    count_inside = 0
    for table in tables:
        for row in table.findAll("tr"):
            if count > 2:   #erste 2 zeilen nicht ausgeben (headings)
                for col in row.findAll("td"):
                    if count_inside == 0:
                        retValue += "Plan: " + col.getText() + "\n"
                    if count_inside == 1:
                        retValue += "Linie: " + col.getText() + "\n"
                    if count_inside == 2:
                        retValue += "Ziel: " + col.getText() + "\n\n"
                    count_inside = count_inside + 1
            count = count + 1
            count_inside = 0
    if retValue == "":
        retValue = "Fehler im AppPY occured"
    retValue = retValue.replace("\n"+bushaltestelle, "")   # removing whitespaces
    return {
        "speech": "",
        "messages": [
        {
        "type": 0,
        "speech": "🚌🚆Abfahrtszeiten im Überblick:",
        "displayText": "🚌🚆Abfahrtszeiten im Überblick"
        },
        {
        "type": 0,
        "speech": retValue,
        "displayText": retValue
        },
        {
        "type": 0,
        "speech": "Genaueres findest du auf http://abfahrtszeiten.at ;)",
        "displayText": "Genaueres findest du auf http://abfahrtszeiten.at ;)"
        }
        ],
        "source": retValue
    }



def getIDfromHaltstelle(bushaltestelle):
    halteID = "404"
    if bushaltestelle == "Am Schlatt":
        halteID = "211_16895"
    elif bushaltestelle == "Augarten":
        halteID = "211_17067"
    elif bushaltestelle == "Badlochstraße":
        halteID = "211_17069"
    elif bushaltestelle == "Bahngasse":
        halteID = "211_16893"
    elif bushaltestelle == "Bahnhof":
        halteID = "211_16677"
    elif bushaltestelle == "Bettleweg":
        halteID = "211_16790"
    elif bushaltestelle == "Bhf-/Bundesstraße":
        halteID = "211_67321"
    elif bushaltestelle == "Binsenfeld":
        halteID = "211_66678"
    elif bushaltestelle == "Brändlestraße":
        halteID = "211_17153"
    elif bushaltestelle == "Carini Saal":
        halteID = "211_16792"
    elif bushaltestelle == "Eicheleweg/Ersatz":
        halteID = "211_17764"
    elif bushaltestelle == "Feldrast":
        halteID = "211_16680"
    elif bushaltestelle == "Feuerwehr":
        halteID = "211_17206"
    elif bushaltestelle == "Fischerbühel":
        halteID = "211_16682"
    elif bushaltestelle == "Flurstraße":
        halteID = "211_67064"
    elif bushaltestelle == "Forststraße":
        halteID = "211_17768"
    elif bushaltestelle == "Frühlingsgarten":
        halteID = "211_17076"
    elif bushaltestelle == "Gasthaus Austria":
        halteID = "211_16684"
    elif bushaltestelle == "Gasthaus Bräuhaus":
        halteID = "211_16686"
    elif bushaltestelle == "Gasthaus Engel":
        halteID = "211_16688"
    elif bushaltestelle == "Gasthaus Linde":
        halteID = "211_16690"
    elif bushaltestelle == "Gasthaus Lustenauer Hof":
        halteID = "211_16692"
    elif bushaltestelle == "Gasthaus Schäfle":
        halteID = "211_16694"
    elif bushaltestelle == "Grüttstraße":
        halteID = "211_17231"
    elif bushaltestelle == "HAK/HAS":
        halteID = "211_16863"
    elif bushaltestelle == "Hasenfeldstraße/Ersatz":
        halteID = "211_17762"
    elif bushaltestelle == "Heitere":
        halteID = "211_16698"
    elif bushaltestelle == "Holzmühlestraße":
        halteID = "211_16802"
    elif bushaltestelle == "Holzstraße":
        halteID = "211_66763"
    elif bushaltestelle == "Industriegebiet Nord":
        halteID = "211_16796"
    elif bushaltestelle == "Kirchplatz":
        halteID = "211_66700"
    elif bushaltestelle == "Körnerstraße":
        halteID = "211_16767"
    elif bushaltestelle == "Lindenstraße":
        halteID = "211_17099"
    elif bushaltestelle == "Loretokapelle":
        halteID = "211_17078"
    elif bushaltestelle == "P.-Krapf-Straße":
        halteID = "211_16784"
    elif bushaltestelle == "Pestalozziweg":
        halteID = "211_66810"
    elif bushaltestelle == "Rathaus":
        halteID = "211_17101"
    elif bushaltestelle == "Rheinhalle":
        halteID = "211_16808"
    elif bushaltestelle == "Rosenlächerstraße":
        halteID = "211_17756"
    elif bushaltestelle == "Rotkreuzstraße":
        halteID = "211_17227"
    elif bushaltestelle == "Sägerstraße":
        halteID = "211_66861"
    elif bushaltestelle == "Scheibenbrücke":
        halteID = "211_16794"
    elif bushaltestelle == "Scheibenstraße":
        halteID = "211_17237"
    elif bushaltestelle == "Schmitter":
        halteID = "211_16972"
    elif bushaltestelle == "Staldenstraße":
        halteID = "211_66800"
    elif bushaltestelle == "Teilenstraße":
        halteID = "211_17074"
    elif bushaltestelle == "Vorachstraße":
        halteID = "211_16703"
    elif bushaltestelle == "VS Kirchdorf":
        halteID = "211_16765"
    elif bushaltestelle == "VS Rotkreuz":
        halteID = "211_16788"
    elif bushaltestelle == "Wiesenrain":
        halteID = "211_66813"
    elif bushaltestelle == "Wiesenrainstraße":
        halteID = "211_17242"
    elif bushaltestelle == "Zellgasse":
        halteID = "211_16891"

    return halteID








############################# Get New Events from Database ##########################################################
def processNewEventsQuery(query, cate_id):
    #Change Host (temporary)
    db = MySQLdb.connect(host = "racingbull.at", port = 3306, user = "d0283414", passwd = "3G7BHexGMtRrW8h3", db = "d0283414", charset = "utf8")
    cursor = db.cursor()
    cursor.execute("""
            select ev_event_translations.title, ev_event_dates.from, ev_event_dates.to, ev_event_translations.locationTitle, ev_event_translations.content from ev_events
	              inner join ev_event_dates
		                 on ev_event_dates.idEvents = ev_events.id
	                         inner join ev_event_translations
		                           on ev_event_translations.idEvents = ev_events.id
	                         inner join ev_event_categories
		                           on ev_event_categories.idEvents = ev_events.id
	                         where idCategories = """ + str(cate_id) + """ and ev_event_dates.from >= '2016-06-24 00:00:00'
	                         order by ev_event_dates.from asc
                             limit 6;
                """)
    data = cursor.fetchall()

    if data == None:
        return {
            "speech": "Es sind momentan keine Veranstaltungen verfügbar.",
            "displayText": "Es sind momentan keine Veranstaltungen verfügbar.",
            # "data": data,
            # "contextOut": [],
            "source": "lustenaubot"
        }
    else:

        # arrays for db query
        title_list = []
        date1_list = []
        date2_list = []
        location_list = []
        content_list = []
        response1 = ""
        response2 = ""
        response3 = ""
        response4 = ""
        response5 = ""


        #einleitungssatz:
        if cate_id == 255:  # music
            response_satz = "Camping 🏕️🚙 auf dem Festival oder doch lieber einem stimmungsvollen Konzert " +\
            "auf dem Blauen Platz lauschen? In Lustenau gibt es eine Vielzahl an Musik- und Konzertveranstaltungen: 🎵"
            qr_buttons = ['🎵Mehr Musik & Konzerte', '🏆Highlights', '⚽Sport']
        elif cate_id == 198:    # sport
            response_satz = "Ob hitziges Derby im Reichshofstadion ⚽ oder stimmungsvolle Action in der Eishalle 🏒" + \
            " - in Lustenau gibt es unzählige Sportveranstaltungen: 🏅"
            qr_buttons = ['⚽Weitere Sportevents' , '🏆Highlights', '🎵Musik & Konzerte']
        else:
            response_satz = 'Wie heißt es doch so schön, "only the best is good enough"! 🎉 ' + \
            'Diese Veranstaltungen solltest du auf keinen Fall verpassen: 🏀🎸🎫'
            qr_buttons = ['🏆Mehr Highlights', '🎵Musik & Konzerte', '⚽Sport']

        # andere quick replies (kein "mehr anzeigen"), wenn bereits zweites mal gecallt:
        query = query.lower()
        verschiebung = 0  # zweite ergebnisse anzeigen -> wert auf +3, dann addieren im array
        if "mehr" in query:
            verschiebung = 3
            response_satz = "Dein Wunsch sei mir Befehl:"
            if cate_id == 255:  # music
                qr_buttons = ['🏆Highlights', '⚽Sport']
            elif cate_id == 198:    # sport
                qr_buttons = ['🏆Highlights', '🎵Musik & Konzerte']
            else:
                qr_buttons = ['🎵Musik & Konzerte', '⚽Sport']


        # hole daten aus query:
        # prinzip: 3 werte werden angezeigt, wenn zweites mal "musik" bsp aufgerufen, events 4-6 anzeigen, sonst 1-3
        for row in data:
            title_list.append("📌 " + row[0])

            date_format = datetime.strptime(str(row[1]), '%Y-%m-%d %H:%M:%S')
            new_format = date_format.strftime("%d.%m. %H:%M Uhr")
            date1_list.append("🕗 " + str(new_format))

            date_format = datetime.strptime(str(row[2]), '%Y-%m-%d %H:%M:%S')
            new_format = date_format.strftime("%d.%m. %H:%M Uhr")
            date2_list.append(str(new_format))

            if row[3] != "":
                location_list.append("🗺️ " + row[3] + ", ")
            else:
                location_list.append("🗺️ ")

            content_list.append(row[4])

        print(title_list)
        print(date1_list)
        print(date2_list)
        print(location_list)
        print(content_list)

        json1 = json.loads(content_list[0+verschiebung])
        #Adding Title
        response1 += title_list[0+verschiebung] + "\n"
        #Adding Dates
        response1 += str(date1_list[0+verschiebung]) + " - " + str(date2_list[0+verschiebung]) + "\n"
        #Adding Location
        response1 += location_list[0+verschiebung]
        #Cut Address from Content...
        response1 += json1['addressStreet']
        print(response1)

        json2 = json.loads(content_list[1+verschiebung])
        #Adding Title
        response2 += title_list[1+verschiebung] + "\n"
        #Adding Dates
        response2 +=  str(date1_list[1+verschiebung]) + " - " + str(date2_list[1+verschiebung]) + "\n"
        #Adding Location
        response2 += location_list[1+verschiebung]
        #Cut Address from Content...
        response2 += json2['addressStreet']
        #str(response2)
        print(response2)

        json3 = json.loads(content_list[2+verschiebung])
        #Adding Title
        response3 += title_list[2+verschiebung] + "\n"
        #Adding Dates
        response3 += str(date1_list[2+verschiebung]) + " - " + str(date2_list[2+verschiebung]) + "\n"
        #Adding Location
        response3 += location_list[2+verschiebung]
        #Cut Address from Content...
        response3 += json3['addressStreet']
        #str(response2)
        print(response3)


        return {
            "speech": "",
            "messages": [
            {
            "type": 0,
            "speech": str(response_satz),
            "displayText": str(response_satz)
            },
            {
            "type": 0,
            "speech": str(response1),
            "displayText": str(response1)
            },
            {
            "type": 0,
            "speech": str(response2),
            "displayText": str(response2)
            },
            {
            "type": 0,
            "speech": str(response3),
            "displayText": str(response3)
            },
            {'title': 'Suchst du nach etwas anderem? 🤔',
                'replies': qr_buttons,
                'type': 2}
            ],
            "source": "lustenauAT-webDB"
        }

    db.close()








############################# yahoo weather shit -> deprecated(?) cause not working ##################################
def processWeather(req):
    if req.get("result").get("action") != "yahooWeatherForecast":
        return {}
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = makeYahooWeatherQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWeatherWebhookResult(data)
    return res



def makeYahooWeatherQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where u='c' and woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWeatherWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))
    wetterText = condition.get('text')
    wetterTextDeutsch = wetterText
    speech = "Heute schaut das Wetter in " + location.get('city') + \
     " wiefolgt aus: " + wetterTextDeutsch + \
     ", die Temperatur liegt bei " + condition.get('temp') + " °" + units.get('temperature')
    print("Response:")
    print(speech)
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "lustenaubot"
    }



def translateWeatherStrings(wetterText):
    # im select kein deutsch verfuegbar
    if wetterText == "AM Clouds/PM Sun":
        wetterText = wetterText.replace('AM Clouds/PM Sun','vormittags bewölkt/nachmittags sonnig')
    elif wetterText == "AM Drizzle/Wind":
        wetterText = wetterText.replace('AM Drizzle/Wind','vorm. Nieselregen/Wind')
    elif wetterText == "AM Drizzle":
        wetterText = wetterText.replace('AM Drizzle','vormittags Nieselregen')
    elif wetterText == "AM Fog/PM Clouds":
        wetterText = wetterText.replace('AM Fog/PM Clouds','vormittags Nebel/nachmittags bewölkt')
    elif wetterText == "AM Fog/PM Sun":
        wetterText = wetterText.replace('AM Fog/PM Sun','vormittags Nebel, nachmittags sonnig')
    elif wetterText == "AM Ice":
        wetterText = wetterText.replace('AM Ice','vorm. Eis')
    elif wetterText == "AM Light Rain/Wind":
        wetterText = wetterText.replace('AM Light Rain/Wind','vorm. leichter Regen/Wind')
    elif wetterText == "AM Light Rain":
        wetterText = wetterText.replace('AM Light Rain','vormittags leichter Regen')
    elif wetterText == "AM Light Snow":
        wetterText = wetterText.replace('AM Light Snow','vormittags leichter Schneefall')
    elif wetterText == "AM Rain/Snow Showers":
        wetterText = wetterText.replace('AM Rain/Snow Showers','vorm. Regen-/Schneeschauer')
    elif wetterText == "AM Rain/Snow/Wind'":
        wetterText = wetterText.replace('AM Rain/Snow/Wind','vorm. Regen/Schnee/Wind')
    elif wetterText == "AM Rain/Snow":
        wetterText = wetterText.replace('AM Rain/Snow','vormittags Regen/Schnee')
    elif wetterText == "AM Rain/Wind":
        wetterText = wetterText.replace('AM Rain/Wind','vorm. Regen/Wind')
    elif wetterText == "AM Rain":
        wetterText = wetterText.replace('AM Rain','vormittags Regen')
    elif wetterText == "AM Showers/Wind":
        wetterText = wetterText.replace('AM Showers/Wind','vormittags Schauer/Wind')
    elif wetterText == "AM Showers":
        wetterText = wetterText.replace('AM Showers','vormittags Schauer')
    elif wetterText == "AM Snow Showers":
        wetterText = wetterText.replace('AM Snow Showers','vormittags Schneeschauer')
    elif wetterText == "AM Snow":
        wetterText = wetterText.replace('AM Snow','vormittags Schnee')
    elif wetterText == "AM Thundershowers":
        wetterText = wetterText.replace('AM Thundershowers','vorm. Gewitterschaur')
    elif wetterText == "Blowing Snow":
        wetterText = wetterText.replace('Blowing Snow','Schneetreiben')
    elif wetterText == "Clear/Windy":
        wetterText = wetterText.replace('Clear/Windy','Klar/Windig')
    elif wetterText == "Clear":
        wetterText = wetterText.replace('Clear','Klar')
    elif wetterText == "Clouds Early/Clearing Late":
        wetterText = wetterText.replace('Clouds Early/Clearing Late','früh Wolken/später klar')
    elif wetterText == "Cloudy/Windy":
        wetterText = wetterText.replace('Cloudy/Windy','Wolkig/Windig')
    elif wetterText == "Cloudy/Wind":
        wetterText = wetterText.replace('Cloudy/Wind','Bewölkt/Wind')
    elif wetterText == "Cloudy":
        wetterText = wetterText.replace('Cloudy','Bewölkt')
    elif wetterText == "Drifting Snow/Windy":
        wetterText = wetterText.replace('Drifting Snow/Windy','Schneetreiben/Windig')
    elif wetterText == "Drifting Snow":
        wetterText = wetterText.replace('Drifting Snow','Schneetreiben')
    elif wetterText == "Drizzle Early":
        wetterText = wetterText.replace('Drizzle Early','früh Nieselregen')
    elif wetterText == "Drizzle Late":
        wetterText = wetterText.replace('Drizzle Late','später Nieselregen')
    elif wetterText == "Drizzle/Fog":
        wetterText = wetterText.replace('Drizzle/Fog','Nieselregen/Nebel')
    elif wetterText == "Drizzle/Windy":
        wetterText = wetterText.replace('Drizzle/Windy','Nieselregen/Windig')
    elif wetterText == "Drizzle/Wind":
        wetterText = wetterText.replace('Drizzle/Wind','Nieselregen/Wind')
    elif wetterText == "Drizzle":
        wetterText = wetterText.replace('Drizzle','Nieselregen')
    elif wetterText == "Fair/Windy":
        wetterText = wetterText.replace('Fair/Windy','Heiter/Windig')
    elif wetterText == "Fair":
        wetterText = wetterText.replace('Fair','Heiter')
    elif wetterText == "Few Showers/Wind":
        wetterText = wetterText.replace('Few Showers/Wind','vereinzelte Schaür/Wind')
    elif wetterText == "Few Snow Showers":
        wetterText = wetterText.replace('Few Snow Showers','vereinzelt Schneeschaür')
    elif wetterText == "Few Showers":
        wetterText = wetterText.replace('Few Showers','vereinzelte Schaür')
    elif wetterText == "Fog Early/Clouds Late":
        wetterText = wetterText.replace('Fog Early/Clouds Late','früh Nebel, später Wolken')
    elif wetterText == "Fog Late":
        wetterText = wetterText.replace('Fog Late','später neblig')
    elif wetterText == "Fog/Windy":
        wetterText = wetterText.replace('Fog/Windy','Nebel/Windig')
    elif wetterText == "Foggy":
        wetterText = wetterText.replace('Foggy','neblig')
    elif wetterText == "Fog":
        wetterText = wetterText.replace('Fog','Nebel')
    elif wetterText == "Freezing Drizzle/Windy":
        wetterText = wetterText.replace('Freezing Drizzle/Windy','gefrierender Nieselregen/Windig')
    elif wetterText == "Freezing Rain":
        wetterText = wetterText.replace('Freezing Rain','gefrierender Regen')
    elif wetterText == "Freezing Drizzle":
        wetterText = wetterText.replace('Freezing Drizzle','gefrierender Nieselregen')
    elif wetterText == "Haze":
        wetterText = wetterText.replace('Haze','Dunst')
    elif wetterText == "Heavy Drizzle":
        wetterText = wetterText.replace('Heavy Drizzle','starker Nieselregen')
    elif wetterText == "Heavy Rain Shower":
        wetterText = wetterText.replace('Heavy Rain Shower','Starker Regenschauer')
    elif wetterText == "Heavy Rain/Windy":
        wetterText = wetterText.replace('Heavy Rain/Windy','Starker Regen/Windig')
    elif wetterText == "Heavy Rain/Wind":
        wetterText = wetterText.replace('Heavy Rain/Wind','starker Regen/Wind')
    elif wetterText == "Heavy Rain":
        wetterText = wetterText.replace('Heavy Rain','Starker Regen')
    elif wetterText == "Heavy Snow Shower":
        wetterText = wetterText.replace('Heavy Snow Shower','Starker Schneeschauer')
    elif wetterText == "Heavy Snow/Wind":
        wetterText = wetterText.replace('Heavy Snow/Wind','Starker Schneefall/Wind')
    elif wetterText == "Heavy Snow":
        wetterText = wetterText.replace('Heavy Snow','Starker Schneefall')
    elif wetterText == "Heavy Thunderstorm/Windy":
        wetterText = wetterText.replace('Heavy Thunderstorm/Windy','Schweres Gewitter/Windig')
    elif wetterText == "Heavy Thunderstorm":
        wetterText = wetterText.replace('Heavy Thunderstorm','Schweres Gewitter')
    elif wetterText == "Ice Crystals":
        wetterText = wetterText.replace('Ice Crystals','Eiskristalle')
    elif wetterText == "Ice Late":
        wetterText = wetterText.replace('Ice Late','später Eis')
    elif wetterText == "Isolated T-storms":
        wetterText = wetterText.replace('Isolated T-storms','Vereinzelte Gewitter')
    elif wetterText == "Isolated Thunderstorms":
        wetterText = wetterText.replace('Isolated Thunderstorms','Vereinzelte Gewitter')
    elif wetterText == "Light Drizzle":
        wetterText = wetterText.replace('Light Drizzle','Leichter Nieselregen')
    elif wetterText == "Light Freezing Drizzle":
        wetterText = wetterText.replace('Light Freezing Drizzle','Leichter gefrierender Nieselregen')
    elif wetterText == "Light Freezing Rain/Fog":
        wetterText = wetterText.replace('Light Freezing Rain/Fog','Leichter gefrierender Regen/Nebel')
    elif wetterText == "Light Freezing Rain":
        wetterText = wetterText.replace('Light Freezing Rain','Leichter gefrierender Regen')
    elif wetterText == "Light Rain Early":
        wetterText = wetterText.replace('Light Rain Early','anfangs leichter Regen')
    elif wetterText == "Light Rain Late":
        wetterText = wetterText.replace('Light Rain Late','später leichter Regen')
    elif wetterText == "Light Rain Shower/Fog":
        wetterText = wetterText.replace('Light Rain Shower/Fog','Leichter Regenschauer/Nebel')
    elif wetterText == "Light Rain Shower/Windy":
        wetterText = wetterText.replace('Light Rain Shower/Windy','Leichter Regenschauer/windig')
    elif wetterText == "Light Rain Shower":
        wetterText = wetterText.replace('Light Rain Shower','Leichter Regenschauer')
    elif wetterText == "Light Rain with Thunder":
        wetterText = wetterText.replace('Light Rain with Thunder','Leichter Regen mit Gewitter')
    elif wetterText == "Light Rain/Fog":
        wetterText = wetterText.replace('Light Rain/Fog','Leichter Regen/Nebel')
    elif wetterText == "Light Rain/Freezing Rain":
        wetterText = wetterText.replace('Light Rain/Freezing Rain','Leichter Regen/Gefrierender Regen')
    elif wetterText == "Light Rain/Wind Early":
        wetterText = wetterText.replace('Light Rain/Wind Early','früh leichter Regen/Wind')
    elif wetterText == "Light Rain/Wind Late":
        wetterText = wetterText.replace('Light Rain/Wind Late','später leichter Regen/Wind')
    elif wetterText == "Light Rain/Windy":
        wetterText = wetterText.replace('Light Rain/Windy','Leichter Regen/Windig')
    elif wetterText == "Light Rain/Wind":
        wetterText = wetterText.replace('Light Rain/Wind','leichter Regen/Wind')
    elif wetterText == "Light Rain":
        wetterText = wetterText.replace('Light Rain','Leichter Regen')
    elif wetterText == "Light Sleet":
        wetterText = wetterText.replace('Light Sleet','Leichter Schneeregen')
    elif wetterText == "Light Snow Early":
        wetterText = wetterText.replace('Light Snow Early','früher leichter Schneefall')
    elif wetterText == "Light Snow Grains":
        wetterText = wetterText.replace('Light Snow Grains','Leichter Schneegriesel')
    elif wetterText == "Light Snow Late":
        wetterText = wetterText.replace('Light Snow Late','später leichter Schneefall')
    elif wetterText == "Light Snow Shower/Fog":
        wetterText = wetterText.replace('Light Snow Shower/Fog','Leichter Schneeschauer/Nebel')
    elif wetterText == "Light Snow Shower":
        wetterText = wetterText.replace('Light Snow Shower','Leichter Schneeschauer')
    elif wetterText == "Light Snow with Thunder":
        wetterText = wetterText.replace('Light Snow with Thunder','Leichter Schneefall mit Gewitter')
    elif wetterText == "Light Snow/Fog":
        wetterText = wetterText.replace('Light Snow/Fog','Leichter Schneefall/Nebel')
    elif wetterText == "Light Snow/Freezing Rain":
        wetterText = wetterText.replace('Light Snow/Freezing Rain','Leichter Schneefall/Gefrierender Regen')
    elif wetterText == "Light Snow/Windy/Fog":
        wetterText = wetterText.replace('Light Snow/Windy/Fog','Leichter Schneefall/Windig/Nebel')
    elif wetterText == "Light Snow/Windy":
        wetterText = wetterText.replace('Light Snow/Windy','Leichter Schneeschauer/Windig')
    elif wetterText == "Light Snow/Wind":
        wetterText = wetterText.replace('Light Snow/Wind','Leichter Schneefall/Wind')
    elif wetterText == "Light Snow":
        wetterText = wetterText.replace('Light Snow','Leichter Schneefall')
    elif wetterText == "Mist":
        wetterText = wetterText.replace('Mist','Nebel')
    elif wetterText == "Mostly Clear":
        wetterText = wetterText.replace('Mostly Clear','überwiegend Klar')
    elif wetterText == "Mostly Cloudy/Wind":
        wetterText = wetterText.replace('Mostly Cloudy/Wind','meist bewölkt/Wind')
    elif wetterText == "Mostly Cloudy":
        wetterText = wetterText.replace('Mostly Cloudy','Überwiegend bewölkt')
    elif wetterText == "Mostly Sunny":
        wetterText = wetterText.replace('Mostly Sunny','Überwiegend sonnig')
    elif wetterText == "Partial Fog":
        wetterText = wetterText.replace('Partial Fog','teilweise Nebel')
    elif wetterText == "Partly Cloudy/Wind":
        wetterText = wetterText.replace('Partly Cloudy/Wind','teilweise bewölkt/Wind')
    elif wetterText == "Partly Cloudy":
        wetterText = wetterText.replace('Partly Cloudy','Teilweise bewölkt')
    elif wetterText == "Patches of Fog/Windy":
        wetterText = wetterText.replace('Patches of Fog/Windy','Nebelfelder/Windig')
    elif wetterText == "Patches of Fog":
        wetterText = wetterText.replace('Patches of Fog','Nebelfelder')
    elif wetterText == "PM Drizzle":
        wetterText = wetterText.replace('PM Drizzle','nachm. Nieselregen')
    elif wetterText == "PM Fog":
        wetterText = wetterText.replace('PM Fog','nachmittags Nebel')
    elif wetterText == "PM Light Rain/Wind":
        wetterText = wetterText.replace('PM Light Rain/Wind','nachm. leichter Regen/Wind')
    elif wetterText == "PM Light Rain":
        wetterText = wetterText.replace('PM Light Rain','nachmittags leichter Regen')
    elif wetterText == "PM Light Snow/Wind":
        wetterText = wetterText.replace('PM Light Snow/Wind','nachm. leichter Schneefall/Wind')
    elif wetterText == "PM Light Snow":
        wetterText = wetterText.replace('PM Light Snow','nachmittags leichter Schneefall')
    elif wetterText == "PM Rain/Snow Showers":
        wetterText = wetterText.replace('PM Rain/Snow Showers','nachmittags Regen/Schneeschauer')
    elif wetterText == "PM Rain/Snow":
        wetterText = wetterText.replace('PM Rain/Snow','nachmittags Regen/Schnee')
    elif wetterText == "PM Rain/Wind":
        wetterText = wetterText.replace('PM Rain/Wind','nachm. Regen/Wind')
    elif wetterText == "PM Rain":
        wetterText = wetterText.replace('PM Rain','nachmittags Regen')
    elif wetterText == "PM Showers/Wind":
        wetterText = wetterText.replace('PM Showers/Wind','nachmittags Schauer/Wind')
    elif wetterText == "PM Snow Showers/Wind":
        wetterText = wetterText.replace('PM Snow Showers/Wind','nachm. Schneeschauer/Wind')
    elif wetterText == "PM Snow Showers":
        wetterText = wetterText.replace('PM Snow Showers','nachmittags Schneeschauer')
    elif wetterText == "PM Showers":
        wetterText = wetterText.replace('PM Showers','nachmittags Schauer')
    elif wetterText == "PM Snow":
        wetterText = wetterText.replace('PM Snow','nachm. Schnee')
    elif wetterText == "PM T-storms":
        wetterText = wetterText.replace('PM T-storms','nachmittags Gewitter')
    elif wetterText == "PM Thundershowers":
        wetterText = wetterText.replace('PM Thundershowers','nachmittags Gewitterschauer')
    elif wetterText == "PM Thunderstorms":
        wetterText = wetterText.replace('PM Thunderstorms','nachm. Gewitter')
    elif wetterText == "Rain and Snow/Windy":
        wetterText = wetterText.replace('Rain and Snow/Windy','Regen und Schnee/Windig')
    elif wetterText == "Rain/Snow Showers/Wind":
        wetterText = wetterText.replace('Rain/Snow Showers/Wind','Regen/Schneeschauer/Wind')
    elif wetterText == "Rain and Snow":
        wetterText = wetterText.replace('Rain and Snow','Schneeregen')
    elif wetterText == "Rain Early":
        wetterText = wetterText.replace('Rain Early','früh Regen')
    elif wetterText == "Rain Late":
        wetterText = wetterText.replace('Rain Late','später Regen')
    elif wetterText == "Rain Shower/Windy":
        wetterText = wetterText.replace('Rain Shower/Windy','Regenschauer/Windig')
    elif wetterText == "Rain Shower":
        wetterText = wetterText.replace('Rain Shower','Regenschauer')
    elif wetterText == "Rain to Snow":
        wetterText = wetterText.replace('Rain to Snow','Regen, in Schnee übergehend')
    elif wetterText == "Rain/Snow Early":
        wetterText = wetterText.replace('Rain/Snow Early','früh Regen/Schnee')
    elif wetterText == "Rain/Snow Late":
        wetterText = wetterText.replace('Rain/Snow Late','später Regen/Schnee')
    elif wetterText == "Rain/Snow Showers Early":
        wetterText = wetterText.replace('Rain/Snow Showers Early','früh Regen-/Schneeschauer')
    elif wetterText == "Rain/Snow Showers Late":
        wetterText = wetterText.replace('Rain/Snow Showers Late','später Regen-/Schneeschnauer')
    elif wetterText == "Rain/Snow Showers":
        wetterText = wetterText.replace('Rain/Snow Showers','Regen/Schneeschauer')
    elif wetterText == "Rain/Snow/Wind":
        wetterText = wetterText.replace('Rain/Snow/Wind','Regen/Schnee/Wind')
    elif wetterText == "Rain/Snow":
        wetterText = wetterText.replace('Rain/Snow','Regen/Schnee')
    elif wetterText == "Rain/Thunder":
        wetterText = wetterText.replace('Rain/Thunder','Regen/Gewitter')
    elif wetterText == "Rain/Wind Early":
        wetterText = wetterText.replace('Rain/Wind Early','früh Regen/Wind')
    elif wetterText == "Rain/Wind Late":
        wetterText = wetterText.replace('Rain/Wind Late','später Regen/Wind')
    elif wetterText == "Rain/Windy":
        wetterText = wetterText.replace('Rain/Windy','Regen/Windig')
    elif wetterText == "Rain/Wind":
        wetterText = wetterText.replace('Rain/Wind','Regen/Wind')
    elif wetterText == "Rain":
        wetterText = wetterText.replace('Rain','Regen')
    elif wetterText == "Scattered Showers/Wind":
        wetterText = wetterText.replace('Scattered Showers/Wind','vereinzelte Schauer/Wind')
    elif wetterText == "Scattered Showers":
        wetterText = wetterText.replace('Scattered Showers','vereinzelte Schauer')
    elif wetterText == "Scattered Snow Showers/Wind":
        wetterText = wetterText.replace('Scattered Snow Showers/Wind','vereinzelte Schneeschauer/Wind')
    elif wetterText == "Scattered Snow Showers":
        wetterText = wetterText.replace('Scattered Snow Showers','vereinzelte Schneeschauer')
    elif wetterText == "Scattered T-storms":
        wetterText = wetterText.replace('Scattered T-storms','vereinzelte Gewitter')
    elif wetterText == "Scattered Thunderstorms":
        wetterText = wetterText.replace('Scattered Thunderstorms','vereinzelte Gewitter')
    elif wetterText == "Shallow Fog":
        wetterText = wetterText.replace('Shallow Fog','flacher Nebel')
    elif wetterText == "Showers Early":
        wetterText = wetterText.replace('Showers Early','früh Schauer')
    elif wetterText == "Showers Late":
        wetterText = wetterText.replace('Showers Late','später Schauer')
    elif wetterText == "Showers in the Vicinity":
        wetterText = wetterText.replace('Showers in the Vicinity','Regenfälle in der Nähe')
    elif wetterText == "Showers/Wind":
        wetterText = wetterText.replace('Showers/Wind','Schauer/Wind')
    elif wetterText == "Showers":
        wetterText = wetterText.replace('Showers','Schauer')
    elif wetterText == "Sleet and Freezing Rain":
        wetterText = wetterText.replace('Sleet and Freezing Rain','Schneeregen und gefrierender Regen')
    elif wetterText == "Sleet/Windy":
        wetterText = wetterText.replace('Sleet/Windy','Schneeregen/Windig')
    elif wetterText == "Snow Grains":
        wetterText = wetterText.replace('Snow Grains','Schneegriesel')
    elif wetterText == "Snow Late":
        wetterText = wetterText.replace('Snow Late','später Schnee')
    elif wetterText == "Snow Showers Early":
        wetterText = wetterText.replace('Snow Showers Early','früh Schneeschauer')
    elif wetterText == "Snow Showers Late":
        wetterText = wetterText.replace('Snow Showers Late','später Schneeschauer')
    elif wetterText == "Snow Showers":
        wetterText = wetterText.replace('Snow Showers','Schneeschauer')
    elif wetterText == "Snow Showers/Wind":
        wetterText = wetterText.replace('Snow Showers/Wind','Schneeschauer/Wind')
    elif wetterText == "Snow Shower":
        wetterText = wetterText.replace('Snow Shower','Schneeschauer')
    elif wetterText == "Snow to Rain":
        wetterText = wetterText.replace('Snow to Rain','Schneeregen')
    elif wetterText == "Snow/Windy":
        wetterText = wetterText.replace('Snow/Windy','Schnee/Windig')
    elif wetterText == "Snow/Wind":
        wetterText = wetterText.replace('Snow/Wind','Schneefall/Wind')
    elif wetterText == "Snow":
        wetterText = wetterText.replace('Snow','Schneefall')
    elif wetterText == "Squalls":
        wetterText = wetterText.replace('Squalls','Böen')
    elif wetterText == "Sunny/Windy":
        wetterText = wetterText.replace('Sunny/Windy','Sonnig/Windig')
    elif wetterText == "Sunny/Wind":
        wetterText = wetterText.replace('Sunny/Wind','Sonnig/Wind')
    elif wetterText == "Sunny":
        wetterText = wetterText.replace('Sunny','Sonnig')
    elif wetterText == "T-showers":
        wetterText = wetterText.replace('T-showers','Gewitterschauer')
    elif wetterText == "Thunder in the Vicinity":
        wetterText = wetterText.replace('Thunder in the Vicinity','Gewitter in der Umgebung')
    elif wetterText == "Thundershowers Early":
        wetterText = wetterText.replace('Thundershowers Early','früh Gewitterschauer')
    elif wetterText == "Thundershowers":
        wetterText = wetterText.replace('Thundershowers','Gewitterschauer')
    elif wetterText == "Thunderstorm/Windy":
        wetterText = wetterText.replace('Thunderstorm/Windy','Gewitter/Windig')
    elif wetterText == "Thunderstorms Early":
        wetterText = wetterText.replace('Thunderstorms Early','früh Gewitter')
    elif wetterText == "Thunderstorms Late":
        wetterText = wetterText.replace('Thunderstorms Late','später Gewitter')
    elif wetterText == "Thunderstorms":
        wetterText = wetterText.replace('Thunderstorms','Gewitter')
    elif wetterText == "Thunderstorm":
        wetterText = wetterText.replace('Thunderstorm','Gewitter')
    elif wetterText == "Thunder":
        wetterText = wetterText.replace('Thunder','Gewitter')
    elif wetterText == "Unknown Precipitation":
        wetterText = wetterText.replace('Unknown Precipitation','Niederschlag')
    elif wetterText == "Unknown":
        wetterText = wetterText.replace('Unknown','unbekannt')
    elif wetterText == "Wintry Mix":
        wetterText = wetterText.replace('Wintry Mix','Winterlicher Mix')

    return wetterText


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')

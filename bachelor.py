#imports
import os
import time
import datetime
import dateutil
import requests
import pandas as pd

end = datetime.date(2000, 1, 1)
start = datetime.date(2000, 1, 1)
months_array = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]

#input Dialog
def input_dialog():
    print("Bitte geben Sie das Jahr und danach den Monat an, für welches Sie die Artikel downloaden wollen.")
    input_start_year = int(input("Mit diesem Jahr beginnt die Zeitspanne: "))
    input_start_month = int(input("Mit diesem Monat beginnt die Zeitspanne: "))

    input_end_year = int(input("Mit diesem Jahr endet die Zeitspanne: "))
    input_end_month = int(input("Mit diesem Monat endet die Zeitspanne: "))

    try:
        global start
        start = datetime.date(input_start_year, input_start_month, 1)
        global end
        end = datetime.date(input_end_year, input_end_month + 1, 1)
   
        months_in_range = [x.split(' ') for x in pd.date_range(start, end, freq='MS').strftime("%Y %#m").tolist()]
        print(f'Sie wollen alle Artikel in der Zeitspanne: {months_array[input_start_month - 1]} {input_start_year} bis {months_array[input_end_month - 1]} {input_end_year} herunter laden?')
    except:
        print(f'Es ist ein Fehler aufgetreten. \nBitte überprüfen Sie Ihre Eingaben. \nTipps: Der Anfangs- und Endmonat dürfen nicht 0 sein. \nDas Format der Monatseingabe ist nicht 03 für März, sonder nur 3.')
        input_dialog()

    date_boolean = input("Ist diese Zeitspanne korrekt? (ja/nein/stop)")
    if(date_boolean == "ja"):
        get_data(months_in_range)
    if(date_boolean == "nein"):
        input_dialog()
    if(date_boolean == "stop"):
        return

def get_data(dates):
    #Sends and parses request/response to/from NYT Archive API for given dates.
    total = 0
    if not os.path.exists('niklas_bachelor'):
        os.mkdir('niklas_bachelor')
    for date in dates:
        if not os.path.exists(f'niklas_bachelor/{date[0]}'):
            os.mkdir(f'niklas_bachelor/{date[0]}')
        if date == dates[-1]:
            break
        response = send_request(date)
        data_frame = parse_response(response)
        total += len(data_frame)
        data_frame.to_csv('niklas_bachelor/' + date[0] + '/' + date[0] + '-' + date[1] + '.csv', sep=";", encoding="utf-8-sig", index=False)
        print('Speichere niklas_bachelor/' + date[0] + '-' + date[1] + '.csv...')
    print('Anzahl der gesammelten Artikel: ' + str(total))

#Keys/ID
API_KEY = "xoJtnoC7G7ymhifGS6Fv3gju2FYi06A7"

def send_request(date):
    #Sends a request to the NYT Archive API for a given date.
    base = 'https://api.nytimes.com/svc/archive/v1/'
    url = base + '/' + date[0] + '/' + date[1] + '.json?api-key=' + API_KEY
    response = requests.get(url).json()
    time.sleep(6)
    return response

def parse_response(response):
    #Parses and returns the response in pandas data frame.
    data = {'Überschrift': [],
        'Datum': [],
        'Dokument-Typ': [],
        'Material-Typ': [],
        'Anzahl der Wörter': [],
        'Rubrik': [],
        'Schlüsselworte': [], 
        'Author': [],}

    articles = response['response']['docs']
    for article in articles:
        date = dateutil.parser.parse(article['pub_date']).date()
        if validation_check(article, date):
            data['Datum'].append(date)
            data['Überschrift'].append(article['headline']['main'])
            if 'section_name' in article:
                data['Rubrik'].append(article['section_name'])
            else:
                data['Rubrik'].append('XEmptyX')
            data['Dokument-Typ'].append(article['document_type'])
            if 'type_of_material' in article:
                data['Material-Typ'].append(article['type_of_material'])
            else:
                data['Material-Typ'].append('XEmptyX')
            data['Anzahl der Wörter'].append(article['word_count'])
            keywords = [keyword['value'] for keyword in article['keywords'] if keyword['name'] == 'subject']
            data['Schlüsselworte'].append(keywords)
            if 'byline' in article:
                data['Author'].append(article['byline']['original'])
            else: 
                data['Author'].append('XEmptyX')
    return pd.DataFrame(data)

def validation_check(article, date):
    #The article is only important if has been creating in our time window and was given a headline
    in_range = date > start and date < end
    has_headline = type(article['headline']) == dict and 'main' in article['headline'].keys()
    return in_range and has_headline

input_dialog()
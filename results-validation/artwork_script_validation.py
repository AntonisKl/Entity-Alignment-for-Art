import requests
import json
import pandas as pd
from unidecode import unidecode
import os


def fetch_wikidata(params):
    url = 'https://www.wikidata.org/w/api.php'
    try:
        return requests.get(url, params=params)
    except:
        return 'There was and error'

def obtain_creator_label(id_creator):
    params = {
                'action': 'wbgetentities',
                'ids':id_creator, 
                'format': 'json',
                #'languages': 'en' # We will accept all lang
            }
     
    # fetch the API
    data = fetch_wikidata(params)
     

    # Show response
    data = data.json()
    #print(data)
    #with open('creator.json', 'w') as f:
    #    json.dump(data, f)


    try:
        _creator = data['entities'][id_creator]['labels']['en']['value']
    except:
        _creator = 'not_found'
    #print("Creator: ",_creator)
    return _creator


def wikidata_response(id):
    # Get ID from the wbsearchentities response
    #id = 'Q62116516'#'Q17327441'
     
    # Create parameters
    params = {
                'action': 'wbgetentities',
                'ids':id, 
                'format': 'json',
                #'languages': 'en' # We will accept all lang
            }
     
    # fetch the API
    data = fetch_wikidata(params)
     
    # Show response
    data = data.json()
    #print(data)
    with open('data.json', 'w') as f:
        json.dump(data, f)


    try:
        title = data['entities'][id]['labels']['en']['value']
    except:
        title = 'not_found'
    try:
        list_title = [title for title in data['entities'][id]['labels']]#['en']['value']
        title_allLang = [ data['entities'][id]['labels'][title]['value'] for title in list_title ]#['en']['value']
    except:
        title_allLang = 'not_found'
    try:
        alternate_names = [v['value'] for v in data['entities'][id]['aliases']['en']]
    except:
        alternate_names = 'not_found'
    try:
        list_names = [ name for name in data['entities'][id]['aliases']]
        alternate_names_all = [ data['entities'][id]['aliases'][name]['value'] for name in list_names ]
    except:
        alternate_names_all = 'not_found'
    try:
        description = data['entities'][id]['descriptions']['en']['value'] 
    except:
        description = 'not_found'
    try:
        list_lang = [ lang for lang in data['entities'][id]['descriptions']]#['en']['value'] 
        description_allLang = [ data['entities'][id]['descriptions'][lang]['value'] for lang in list_lang ]
    except:
        description_allLang = 'not_found'
    
    try:
        instance_of = [v['mainsnak']['datavalue']['value']['numeric-id'] for v in data['entities'][id]['claims']['P31']]
    except:
        instance_of = 'not_found'
    try:
        part_of = [v['mainsnak']['datavalue']['value']['id'] for v in data['entities'][id]['claims']['P361']]
    except:
        part_of = 'not_found'
    try:
        creator_of = [v['mainsnak']['datavalue']['value']['id'] for v in data['entities'][id]['claims']['P170']]
        creator_of = obtain_creator_label(creator_of[0])
    except:
        creator_of = 'not_found'
    try:
        image_names = [v['mainsnak']['datavalue']['value'] for v in data['entities'][id]['claims']['P18']]
    except:
        image_names = 'not_found'
    try:
        title_of = [v['mainsnak']['datavalue']['value'] ['text']for v in data['entities'][id]['claims']['P1476']]
    except:
        title_of = 'not_found'
    try:
        inception = data['entities'][id]['claims']['P571'][0]['mainsnak']['datavalue']['value']['time']
    except:
        inception = 'not_found'
     
     
    result = {
        #'wikidata_id':id,
        'title':title,
        'title_allLang':title_allLang,
        'description':description,
        'description_allLang':description_allLang,
        'alternate_names':alternate_names,
        'alternate_names_all':alternate_names_all,
        #'instance_of':instance_of,
        'creator_of':creator_of,
        #'inception':inception,
        'image_names':image_names,
        'title_of':title_of,
        }
    text = ""
    #print(result)
    for item in result.values():
        if type(item) == str:
            if item == "not_found":
                continue
            text += item + ' '
        elif type(item) == list:
            for element in item:
                text += element + ' '
    #print(result)
    #print(text)
    #print("."*50)
    

    return result,text

def text_cleaning(word,_type):
    word = word.lower() 
    word = unidecode(word) # Remove spetial characters
    word = word.replace('-', ' ') # Replace -
    
    if _type == "art" or _type == "creator":
        the = word.split(' ', 1)[0]
        if the == "the":
            #print("word before: ",word)
            word = word.split(' ', 1)[1] # If text star with "the" it removes it
            #print("word after: ",word)
    return word


def validation(path,n):
    df = pd.read_csv(path)
    n = df.shape[0]
    #print("Number of rows: ", df.shape)
    #print(df.head())
    entities = df["Entity ID"].values[:n]
    creators = df["Creator Label"].values[:n]
    art_works = df["Input Text"].values[:n]

    validation_list = list()
    for id, creator, art in zip(entities,creators,art_works):
        only_id = id.split("/")[-1]
        print("-"*20)
        print(only_id," - ",creator," - ",art)
        result,wikidata_text = wikidata_response(only_id)

        "Cleaning text"
        creator = text_cleaning(creator,"creator")
        art = text_cleaning(art,"art")
        wikidata_text = text_cleaning(wikidata_text,"None")
        
        flag_creator, flag_art = False, False

        if creator in wikidata_text:
            flag_creator = True

        if art in wikidata_text:
            flag_art = True


        # It means, if found somewhete in the wikidata page the creator and art_work
        # Sometimes in the figure caption or as other language.
        if flag_creator ==True and flag_art == True:
            #print("GREAT")
            validation_list.append('Y')
        elif flag_creator ==False and flag_art == False:
            #print("GREAT")
            validation_list.append('N')
        # C? it means not 100% confident about creator
        elif flag_creator ==False and flag_art == True:
            validation_list.append('C?')
            print("Flags: Creator(",flag_creator,") Art(",flag_art,")")
            print(id)
            print(result)
        # A? it means not 100% confident about art work
        elif flag_creator ==True and flag_art == False:
            validation_list.append('A?')
            print("Flags: Creator(",flag_creator,") Art(",flag_art,")")
            print(id)
            print(result)
        print("-"*20)

    #print("validation_list: ",validation_list)
    "Add the results to CSV file"
    df["script_val"] = validation_list
    df.to_csv(os.getcwd()+'/script.csv')

 
################# PUT HERE YOUR PATH :) #################
path = "/Users/danielafe/Desktop/sample_5_script.csv"
validation(path,1)


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

def obtain_outsite_label(_id):
    params = {
                'action': 'wbgetentities',
                'ids':_id, 
                'format': 'json',
                'languages': 'en' # We will accept all lang, too long for artist
            }
     
    # fetch the API
    data = fetch_wikidata(params)
     

    # Show response
    data = data.json()
    #print(_id,data)
    #with open('creator.json', 'w') as f:
    #    json.dump(data, f)


    try:
        _label = data['entities'][_id]['labels']['en']['value']
    except:
        _label = 'not_found'
    #print("_label: ",_label)
    return _label


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
        langs = [ name for name in data['entities'][id]['aliases']]
        all_also_knows_as = list()
        for lang in langs:
            all_also_knows_as += [v['value'] for v in data['entities'][id]['aliases'][lang]]
            #print(lang,[v['value'] for v in data['entities'][id]['aliases'][lang]])
        alternate_names_all = all_also_knows_as
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
        image_names = [v['mainsnak']['datavalue']['value'] for v in data['entities'][id]['claims']['P18']]
    except:
        image_names = 'not_found'

    try:
        placeBirth = [v['mainsnak']['datavalue']['value'] ['id']for v in data['entities'][id]['claims']['P19']][0]
        placeBirth = obtain_outsite_label(placeBirth)
    except:
        placeBirth = 'not_found'

    try:
        placeDeath = [v['mainsnak']['datavalue']['value'] ['id']for v in data['entities'][id]['claims']['P20']][0]
        placeDeath = obtain_outsite_label(placeDeath)
    except:
        placeDeath = 'not_found'

    try:
        nationality = [v['mainsnak']['datavalue']['value'] ['id']for v in data['entities'][id]['claims']['P27']]
        list_n = []
        for n in nationality:
            nation = obtain_outsite_label(n)
            list_n.append(nation)
        nationality = list_n
    except:
        nationality = ['not_found']
    
    try:
        occupations = [v['mainsnak']['datavalue']['value'] ['id']for v in data['entities'][id]['claims']['P106']]
        list_o = []
        for o in occupations:
            occupation = obtain_outsite_label(o)
            list_o.append(occupation)
        occupations = list_o
    except:
        occupations = ['not_found']
  

    result = {
        #'wikidata_id':id,
        'title':title,
        'title_allLang':title_allLang,
        'description':description,
        'description_allLang':description_allLang,
        'alternate_names':alternate_names,
        'alternate_names_all':alternate_names_all, #also known as
        'image_names':image_names,
        'placeBirth':placeBirth,
        'placeDeath':placeDeath,
        'nationality':nationality,
        'occupation':occupations,
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

##artist,sentence,wikidata_url,is_correct,correct_wikidata_url,notes
def validation(path,n):
    df = pd.read_csv(path)
    n = df.shape[0]
    #print("Number of rows: ", df.shape)
    #print(df.head())
    entities = df["wikidata_url"].values[:n]
    art_works = df["artwork"].values[:n]
    sentences = df["sentence"].values[:n] # Extra info about the artist
    creators = df["artist"].values[:n] # Extra info about the artist

    validation_list = list()
    for id, creator, art, info in zip(entities,creators,art_works, sentences):
        only_id = id.split("/")[-1]
        print("-"*20)
        print(only_id," - ",creator," - ",art)
        print("Info Artist: ",info)

        result,wikidata_text = wikidata_response(only_id) # Conecting to Wikidata API
        #print(result)
        #print(wikidata_text)

        "Cleaning text"
        creator = text_cleaning(creator,"creator")
        #art = text_cleaning(art,"art")
        wikidata_text = text_cleaning(wikidata_text,"None")
        info = text_cleaning(info,"None") + creator
        occupations = result['occupation']
        description =  result['description']
        artis_names = result["title_allLang"]
        
        print("From wikidata:")
        print("occupation:",occupations)        
        print("description:",description)        
        print("artis_names:",artis_names)        

        flag_creator, flag_occupation, flag_nationality = False, False, False
        if description == "Wikimedia disambiguation page": 
            print("No wikidata url")

        else:
            for creator in artis_names:
                creator = text_cleaning(creator,"None")
                if creator in info:
                    flag_creator = True
                    break

            for occupation in occupations:
                occupation = text_cleaning(occupation,"None")
                if occupation in info:
                    flag_occupation = True
                    break

            description = text_cleaning(description,"None")
            nationality = description.split()
            for nation in nationality:
                if nation in info:
                    flag_nationality = True
                    break

        print("Flags:")
        print("flag_creator:", flag_creator," flag_occupation: ",flag_occupation, " flag_nationality:",flag_nationality)
        
        # It means, if found somewhere in the wikidata page the creator and art_work
        # Sometimes in the figure caption or as other language.
        if flag_creator ==True and flag_occupation == True and flag_nationality == True:
            #print("GREAT")
            validation_list.append('yes')
        else:
            validation_list.append('no')
        print("-"*20)
    
    #print("validation_list: ",validation_list)
    "Add the results to CSV file"
    df["script_val"] = validation_list
    df.to_csv(os.getcwd()+'/scriptArtist.csv')
    

 
################# PUT HERE YOUR PATH :) #################
path = "/Users/danielafe/Desktop/ISWSvOCANS/Antonies_Eval.csv"
validation(path,1)


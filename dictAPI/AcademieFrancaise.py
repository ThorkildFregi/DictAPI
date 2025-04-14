from mechanicalsoup import StatefulBrowser
from bs4 import BeautifulSoup
import unicodedata
import requests

url = "https://www.dictionnaire-academie.fr/article/"
headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:35.0) Gecko/20100101 Firefox/35.0'}

def _find_id(name: str, edition: int) -> str:
    browser = StatefulBrowser()
    browser.open("https://www.dictionnaire-academie.fr/")

    browser.select_form("form[id='frm_search']")
    
    browser["term"] = name

    submit = browser.submit_selected()
    
    id = submit.url.replace("https://www.dictionnaire-academie.fr/searcharticle/", "")

    response = requests.get(url + id, headers=headers)

    if response.status_code == 404:
        raise Exception(f'The word "{name}" is not in the dictionnaries of the Académie Française !')
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    dictionaries_edition = soup.find("ul", {"id": "ulFlexDictionnaire"}).find_all("a")

    final_id = ""
    for dictionary_edition in dictionaries_edition:
        id = dictionary_edition["href"].replace("/article/", "")

        if id[1] == str(edition):
            final_id = id

    if final_id == "":
        raise Exception(f'The word "{name.lower()}" is not in the {str(edition)}th dictionnary of the Académie Française !')
    
    return final_id

def _get_infos(id: str):
    response = requests.get(url + id, headers=headers)

    soup = BeautifulSoup(response.text, 'html.parser')

    definition_html = soup.find("meta", {"name": "description"})["content"]

    type = soup.find("span", {"class": "s_cat"}).text

    is_def = False
    definition = ""
    for letter in definition_html:
        if is_def ==  True:
            definition = definition + letter

        if letter == ":":
            is_def = True

    definition = definition[1:]

    return type, definition

class Word:
    def __init__(self, name: str, edition: int):
        self.name = name.upper()
        self.edition = edition

        self.id = _find_id(self.name, self.edition)
        self.type, self.definition = _get_infos(self.id)
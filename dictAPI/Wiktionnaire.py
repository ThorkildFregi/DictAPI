from bs4 import BeautifulSoup
import unicodedata
import requests

url = "https://fr.wiktionary.org/wiki/"
headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:35.0) Gecko/20100101 Firefox/35.0',}

def _get_etymology(name: str) -> list:
    response = requests.get(url + name, headers=headers)

    soup = BeautifulSoup(response.text, 'html.parser')

    etymologys_html = soup.find_all("h3", {"id": "Étymologie"})[0].parent.parent.find_all("dd")

    etymologys = []
    for etymology_html in etymologys_html:
        etymologys.append(unicodedata.normalize("NFKD", etymology_html.text))

    return etymologys

def _get_infos(name: str, id: str):
    response = requests.get(url + name, headers=headers)

    soup = BeautifulSoup(response.text, 'html.parser')

    title_html = soup.find("span", {"id": id})

    title = title_html.text

    def_html = title_html.parent.parent.parent

    api = def_html.find("span", {"class": "API"}).text

    defs_html = def_html.find("ol").contents

    defs = []
    for meaning in defs_html:
        if meaning != "\n":
            meaning = unicodedata.normalize("NFKD", meaning.text).replace("\n", "|")
            meaning = meaning.split("|")

            i = 0
            examples = ""
            for example in meaning:
                if i != 0:
                    examples = f"{examples} {example}"
                else:
                    i += 1

            meanings = {"definition": meaning[0], "examples": examples}

            defs.append(meanings)

    sections_html = def_html.find_all("section")

    synonyms = []
    antonyms = []
    deriveds = []
    hypernyms = []
    traductions = []
    etymological_relatives = []
    for section_html in sections_html:
        if section_html.find("span", {"class": "titreanto"}) != None:
            for antonym in section_html.find("span", {"class": "titreanto"}).parent.parent.parent.find_all("li"):
                antonyms.append(antonym.text)
        if section_html.find("span", {"class": "titrederiv"}) != None:
            for derived in section_html.find("span", {"class": "titrederiv"}).parent.parent.parent.find_all("li"):
                deriveds.append(derived.text)
        if section_html.find("span", {"class": "titreappar"}) != None:
            for etymological_relative in section_html.find("span", {"class": "titreappar"}).parent.parent.parent.find_all("li"):
                etymological_relatives.append(etymological_relative.text)
        if section_html.find("span", {"class": "titretrad"}) != None:
            for traduction in section_html.find("span", {"class": "titretrad"}).parent.parent.parent.find_all("li"):
                traductions.append(unicodedata.normalize("NFKD", traduction.text))
        if section_html.find("span", {"class": "titresyno"}) != None:
            for synonym in section_html.find("span", {"class": "titresyno"}).parent.parent.parent.find_all("li"):
                synonyms.append(unicodedata.normalize("NFKD", synonym.text))
        if section_html.find("span", {"class": "titrehyper"}) != None:
            for hypernym in section_html.find("span", {"class": "titrehyper"}).parent.parent.parent.find_all("li"):
                hypernyms.append(unicodedata.normalize("NFKD", hypernym.text))

    return title, api, defs, antonyms, deriveds, etymological_relatives, traductions, synonyms, hypernyms

class Definition:
    def __init__(self, name: str, id: str):
        self._id = id
        self.name = name

        self.title, self.api, self.meaning, self.antonym, self.derived, self.etymological_relatives, self.traductions, self.synonyms, self.hypernyms = _get_infos(name, id)

def _get_defs(name: str):
    response = requests.get(url + name, headers=headers)

    soup = BeautifulSoup(response.text, 'html.parser')

    sections_html = soup.find("span", {"id": "fr"}).parent.parent.parent

    definitions = []
    for section in sections_html.find_all("section"):
        if section.find_all("h3", {"id": "Étymologie"}) != []:
            pass
        elif section.find_all("span", {"class": "titredef"}) != []:
            definitions.append(Definition(name, section.find("span", {"class": "titredef"})["id"]))

    return definitions

class Word:
    def __init__(self, name: str):
        self.name = name

        self.etymologys = _get_etymology(self.name)
        self.definitions = _get_defs(self.name)

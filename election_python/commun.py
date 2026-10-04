"""Fonctions partagées par les scripts d'élections législatives."""

import datetime
import functools
import re
import unicodedata
from pathlib import Path

import pandas as pd
import requests

DOSSIER_DONNEES = Path(__file__).resolve().parent / "excel_file"

# Dates des deux tours de chaque élection législative au scrutin majoritaire.
# 1986 (scrutin proportionnel départemental) n'a pas de circonscriptions.
DATES_ELECTIONS = {
    1958: (datetime.date(1958, 11, 23), datetime.date(1958, 11, 30)),
    1962: (datetime.date(1962, 11, 18), datetime.date(1962, 11, 25)),
    1967: (datetime.date(1967, 3, 5), datetime.date(1967, 3, 12)),
    1968: (datetime.date(1968, 6, 23), datetime.date(1968, 6, 30)),
    1973: (datetime.date(1973, 3, 4), datetime.date(1973, 3, 11)),
    1978: (datetime.date(1978, 3, 12), datetime.date(1978, 3, 19)),
    1981: (datetime.date(1981, 6, 14), datetime.date(1981, 6, 21)),
    1988: (datetime.date(1988, 6, 5), datetime.date(1988, 6, 12)),
    1993: (datetime.date(1993, 3, 21), datetime.date(1993, 3, 28)),
    1997: (datetime.date(1997, 5, 25), datetime.date(1997, 6, 1)),
    2002: (datetime.date(2002, 6, 9), datetime.date(2002, 6, 16)),
    2007: (datetime.date(2007, 6, 10), datetime.date(2007, 6, 17)),
    2012: (datetime.date(2012, 6, 10), datetime.date(2012, 6, 17)),
    2017: (datetime.date(2017, 6, 11), datetime.date(2017, 6, 18)),
}

# Élections dont les résultats par circonscription sont dans DOSSIER_DONNEES.
ANNEES_DISPONIBLES = [annee for annee in DATES_ELECTIONS if annee <= 2012]

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]

# Nom des départements tel qu'utilisé dans les titres d'articles Wikipédia,
# avec la préposition qui le précède (« 1re circonscription de l'Ain »).
DEPARTEMENTS = [
    ("Ain", "de l'"),
    ("Aisne", "de l'"),
    ("Allier", "de l'"),
    ("Alpes-de-Haute-Provence", "des "),
    ("Hautes-Alpes", "des "),
    ("Alpes-Maritimes", "des "),
    ("Ardèche", "de l'"),
    ("Ardennes", "des "),
    ("Ariège", "de l'"),
    ("Aube", "de l'"),
    ("Aude", "de l'"),
    ("Aveyron", "de l'"),
    ("Bouches-du-Rhône", "des "),
    ("Calvados", "du "),
    ("Cantal", "du "),
    ("Charente", "de la "),
    ("Charente-Maritime", "de la "),
    ("Cher", "du "),
    ("Corrèze", "de la "),
    ("Corse", "de la "),
    ("Corse-du-Sud", "de la "),
    ("Haute-Corse", "de la "),
    ("Côte-d'Or", "de la "),
    ("Côtes-d'Armor", "des "),
    ("Creuse", "de la "),
    ("Dordogne", "de la "),
    ("Doubs", "du "),
    ("Drôme", "de la "),
    ("Eure", "de l'"),
    ("Eure-et-Loir", "d'"),
    ("Finistère", "du "),
    ("Gard", "du "),
    ("Haute-Garonne", "de la "),
    ("Gers", "du "),
    ("Gironde", "de la "),
    ("Hérault", "de l'"),
    ("Ille-et-Vilaine", "d'"),
    ("Indre", "de l'"),
    ("Indre-et-Loire", "d'"),
    ("Isère", "de l'"),
    ("Jura", "du "),
    ("Landes", "des "),
    ("Loir-et-Cher", "de "),
    ("Loire", "de la "),
    ("Haute-Loire", "de la "),
    ("Loire-Atlantique", "de la "),
    ("Loiret", "du "),
    ("Lot", "du "),
    ("Lot-et-Garonne", "de "),
    ("Lozère", "de la "),
    ("Maine-et-Loire", "de "),
    ("Manche", "de la "),
    ("Marne", "de la "),
    ("Haute-Marne", "de la "),
    ("Mayenne", "de la "),
    ("Meurthe-et-Moselle", "de "),
    ("Meuse", "de la "),
    ("Morbihan", "du "),
    ("Moselle", "de la "),
    ("Nièvre", "de la "),
    ("Nord", "du "),
    ("Oise", "de l'"),
    ("Orne", "de l'"),
    ("Pas-de-Calais", "du "),
    ("Puy-de-Dôme", "du "),
    ("Pyrénées-Atlantiques", "des "),
    ("Hautes-Pyrénées", "des "),
    ("Pyrénées-Orientales", "des "),
    ("Bas-Rhin", "du "),
    ("Haut-Rhin", "du "),
    ("Rhône", "du "),
    ("Haute-Saône", "de la "),
    ("Saône-et-Loire", "de "),
    ("Sarthe", "de la "),
    ("Savoie", "de la "),
    ("Haute-Savoie", "de la "),
    ("Paris", "de "),
    ("Seine-Maritime", "de la "),
    ("Seine-et-Marne", "de "),
    ("Yvelines", "des "),
    ("Deux-Sèvres", "des "),
    ("Somme", "de la "),
    ("Tarn", "du "),
    ("Tarn-et-Garonne", "de "),
    ("Var", "du "),
    ("Vaucluse", "de "),
    ("Vendée", "de la "),
    ("Vienne", "de la "),
    ("Haute-Vienne", "de la "),
    ("Vosges", "des "),
    ("Yonne", "de l'"),
    ("Territoire de Belfort", "du "),
    ("Essonne", "de l'"),
    ("Hauts-de-Seine", "des "),
    ("Seine-Saint-Denis", "de la "),
    ("Val-de-Marne", "du "),
    ("Val-d'Oise", "du "),
    ("Guadeloupe", "de la "),
    ("Martinique", "de la "),
    ("Guyane", "de la "),
    ("La Réunion", "de "),
    ("Mayotte", "de "),
    ("Saint-Pierre-et-Miquelon", "de "),
    ("Nouvelle-Calédonie", "de la "),
    ("Polynésie française", "de la "),
    ("Wallis-et-Futuna", "de "),
    ("Saint-Barthélemy et Saint-Martin", "de "),
    ("Français établis hors de France", "des "),
]


def sans_accents(texte):
    """Supprime les accents de ``texte`` (« Hérault » -> « Herault »)."""
    decompose = unicodedata.normalize("NFKD", str(texte))
    return "".join(c for c in decompose if not unicodedata.combining(c))


def cle_departement(nom):
    """Clé de comparaison insensible à la casse, aux accents et à la
    ponctuation : « CORSE DU SUD », « Corse-du-Sud » -> « CORSE-DU-SUD »."""
    return re.sub(r"[^A-Z0-9]+", "-", sans_accents(nom).upper()).strip("-")


_DEPARTEMENTS_PAR_CLE = {cle_departement(nom): (nom, prep)
                         for nom, prep in DEPARTEMENTS}
# Noms employés par le CDSP qui diffèrent de ceux des articles Wikipédia.
_DEPARTEMENTS_PAR_CLE[cle_departement("SAINT-MARTIN/SAINT-BARTHELEMY")] = \
    ("Saint-Barthélemy et Saint-Martin", "de ")
_DEPARTEMENTS_PAR_CLE[cle_departement("FRANCAIS-DE-L'ETRANGER")] = \
    ("Français établis hors de France", "des ")


def departement_wiki(departement):
    """Renvoie ``(nom, préposition)`` d'un département pour Wikipédia.

    Le nom est accepté sous n'importe quelle forme (« ARDECHE », « Ardèche »).
    Un département inconnu est renvoyé tel quel avec la préposition « de ».
    """
    return _DEPARTEMENTS_PAR_CLE.get(cle_departement(departement),
                                     (str(departement).title(), "de "))


def ordinal(nombre):
    """Adjectif ordinal abrégé : 1 -> « 1re », 2 -> « 2e »."""
    return f"{nombre}re" if nombre == 1 else f"{nombre}e"


def jours_election(annee):
    """Jours des deux tours : « 23 et 30 novembre », « 25 mai et 1er juin »."""
    premier, second = DATES_ELECTIONS[annee]
    jour_second = "1er" if second.day == 1 else str(second.day)
    if premier.month == second.month:
        return f"{premier.day} et {jour_second} {MOIS[second.month - 1]}"
    return (f"{premier.day} {MOIS[premier.month - 1]} et "
            f"{jour_second} {MOIS[second.month - 1]}")


def remove_accents(string):
    """Supprime les accents des minuscules.

    Utilisé pour rapprocher les noms des candidats (CDSP) des libellés
    Wikidata. Les majuscules accentuées ne sont pas modifiées.
    """
    if not isinstance(string, str):
        string = str(string, encoding='utf-8')

    string = re.sub("[àáâãäå]", 'a', string)
    string = re.sub("[èéêë]", 'e', string)
    string = re.sub("[ìíîï]", 'i', string)
    string = re.sub("[òóôõö]", 'o', string)
    string = re.sub("[ùúûü]", 'u', string)
    string = re.sub("[ýÿ]", 'y', string)
    return string


@functools.lru_cache(maxsize=None)
def charger_tour(annee, tour):
    """Charge le fichier du CDSP d'une élection et d'un tour (1 ou 2)."""
    for extension in ("xls", "xlsx"):
        chemin = DOSSIER_DONNEES / f"cdsp_legi{annee}t{tour}_circ.{extension}"
        if chemin.exists():
            return pd.read_excel(chemin, index_col=None)
    raise FileNotFoundError(
        f"Aucun fichier pour le tour {tour} de {annee} dans {DOSSIER_DONNEES}")


def find_departement(dataframe, departement):
    """Lignes de ``dataframe`` correspondant au département."""
    cles = dataframe['département'].map(cle_departement)
    return dataframe[cles == cle_departement(departement)]


def find_circo(dataframe, departement, circonscription):
    """Ligne(s) de ``dataframe`` correspondant à la circonscription."""
    dataframe_dep = find_departement(dataframe, departement)
    return dataframe_dep[dataframe_dep['circonscription'] == circonscription]


def candidats(ligne, maximum=None):
    """Candidats d'une ligne des fichiers 1988-2012.

    Les colonnes sont numérotées (« 1 nuance », « 1 Nom candidat »...) ; la
    liste s'arrête au premier numéro sans nuance.
    """
    numero = 1
    while isinstance(ligne.get(f"{numero} nuance"), str):
        if maximum is not None and numero > maximum:
            break
        yield {
            'cle': ligne[f"{numero} nuance"] + ligne[f"{numero} Nom candidat"],
            'nuance': ligne[f"{numero} nuance"],
            'prenom': ligne.get(f"{numero} Prénom candidat"),
            'nom': ligne[f"{numero} Nom candidat"],
            'etiquette': ligne.get(f"{numero} Etiquette liste"),
            'voix': int(ligne[f"{numero} voix"]),
        }
        numero += 1


URL_WIKIDATA = 'https://query.wikidata.org/sparql'
USER_AGENT = ("wikipedia_scripts/1.0 "
              "(https://github.com/adrdufour/wikipedia_scripts)")

# Personnalités politiques françaises nées après 1858 ayant un article sur
# Wikipédia en français.
REQUETE_POLITICIENS = """
SELECT DISTINCT ?itemLabel ?sitelink WHERE {
  ?item wdt:P27 wd:Q142;
        wdt:P31 wd:Q5;
        wdt:P106 wd:Q82955;
        wdt:P569 ?age;
  FILTER(YEAR(?age) >= 1858).
  ?article schema:name ?sitelink ;
           schema:about ?item ;
           schema:isPartOf <https://fr.wikipedia.org/> .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "fr" }
}
"""


def recuperer_politiciens_wikidata():
    """Renvoie ``{« Prénom Nom » sans accents : titre de l'article}``.

    Permet de transformer le nom d'un candidat en lien vers son article.
    """
    reponse = requests.get(URL_WIKIDATA,
                           params={'format': 'json',
                                   'query': REQUETE_POLITICIENS},
                           headers={"User-Agent": USER_AGENT},
                           timeout=300)
    reponse.raise_for_status()
    return {remove_accents(ligne['itemLabel']['value']): ligne['sitelink']['value']
            for ligne in reponse.json()['results']['bindings']}

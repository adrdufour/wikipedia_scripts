"""Ajoute sur Wikidata le nombre d'étudiants inscrits (P2196) par année dans
les établissements d'enseignement supérieur français.

Source : jeu de données « Statistiques sur les effectifs d'étudiants inscrits
par établissement » du ministère de l'Enseignement supérieur et de la
Recherche (export CSV, séparateur « ; »).

Exemple :
    python effectif.py fr-esr-statistiques-sur-les-effectifs-d-etudiants-inscrits-par-etablissement-hcp.csv --simulation
"""

import argparse
import datetime

import pandas as pd
import pywikibot

URL_SOURCE = ("https://data.enseignementsup-recherche.gouv.fr/explore/dataset/"
              "fr-esr-statistiques-sur-les-effectifs-d-etudiants-inscrits-par-"
              "etablissement-hcp/table/?sort=-annee_universitaire")

NOMBRE_ETUDIANTS = 'P2196'
DATE = 'P585'
AFFIRME_DANS = 'P248'
URL_REFERENCE = 'P854'
AUTEUR = 'P50'
DATE_CONSULTATION = 'P813'
# Élément Wikidata de la publication et de son auteur (le ministère).
PUBLICATION = 'Q3016893'
MINISTERE = 'Q2726949'


def sources(repo, date_consultation):
    """Références ajoutées à chaque déclaration."""
    affirme_dans = pywikibot.Claim(repo, AFFIRME_DANS)
    affirme_dans.setTarget(pywikibot.ItemPage(repo, PUBLICATION))
    url = pywikibot.Claim(repo, URL_REFERENCE)
    url.setTarget(URL_SOURCE)
    auteur = pywikibot.Claim(repo, AUTEUR)
    auteur.setTarget(pywikibot.ItemPage(repo, MINISTERE))
    consultation = pywikibot.Claim(repo, DATE_CONSULTATION)
    consultation.setTarget(pywikibot.WbTime(year=date_consultation.year,
                                            month=date_consultation.month,
                                            day=date_consultation.day))
    return [affirme_dans, url, auteur, consultation]


def annees_presentes(item):
    """Années pour lesquelles l'élément a déjà un nombre d'étudiants."""
    annees = set()
    for claim in item.claims.get(NOMBRE_ETUDIANTS, []):
        for qualificatif in claim.qualifiers.get(DATE, []):
            annees.add(qualificatif.getTarget().year)
    return annees


def ajouter_effectif(repo, item, annee, effectif, date_consultation):
    claim = pywikibot.Claim(repo, NOMBRE_ETUDIANTS)
    claim.setTarget(pywikibot.WbQuantity(effectif, site=repo))
    qualificatif = pywikibot.Claim(repo, DATE)
    qualificatif.setTarget(pywikibot.WbTime(year=annee))
    claim.addQualifier(qualificatif, summary='Adding a qualifier.')
    claim.addSources(sources(repo, date_consultation), summary='Adding sources.')
    item.addClaim(claim, summary='Script add student number per year')


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("csv", help="fichier CSV téléchargé depuis "
                                    "data.enseignementsup-recherche.gouv.fr")
    parser.add_argument("--date-consultation",
                        type=datetime.date.fromisoformat,
                        default=datetime.date.today(),
                        help="date de téléchargement du CSV, AAAA-MM-JJ "
                             "(par défaut : aujourd'hui)")
    parser.add_argument("--debut", type=int, default=0,
                        help="index du premier établissement à traiter, "
                             "pour reprendre un traitement interrompu")
    parser.add_argument("--simulation", action="store_true",
                        help="affiche les ajouts sans modifier Wikidata")
    args = parser.parse_args()

    df = pd.read_csv(args.csv, sep=";")
    df = df[df['etablissement_id_wikidata'].notna()]

    site = pywikibot.Site("wikidata", "wikidata")
    repo = site.data_repository()

    etablissements = df['etablissement_id_wikidata'].unique()
    for index, wikidata_id in enumerate(etablissements[args.debut:],
                                        start=args.debut):
        item = pywikibot.ItemPage(repo, wikidata_id)
        item.get()
        deja_presentes = annees_presentes(item)
        lignes = df[df['etablissement_id_wikidata'] == wikidata_id]
        for annee in lignes['annee'].unique():
            annee = int(annee)
            effectif = int(lignes.loc[lignes['annee'] == annee, 'effectif'].iloc[0])
            if annee in deja_presentes:
                print(f"[{index}] {wikidata_id} {annee} : déjà présent")
                continue
            print(f"[{index}] {wikidata_id} {annee} : {effectif} étudiants")
            if not args.simulation:
                ajouter_effectif(repo, item, annee, effectif,
                                 args.date_consultation)


if __name__ == "__main__":
    main()

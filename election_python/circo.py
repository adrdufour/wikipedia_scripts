"""Génère le wikicode des résultats des élections législatives d'une
circonscription (1958-2012), au format du modèle {{Résultats électoraux}}.

Exemple :
    python circo.py -d PAS-DE-CALAIS -c 14 > resultats.txt
"""

import argparse

import partis
from commun import (ANNEES_DISPONIBLES, DATES_ELECTIONS, candidats,
                    charger_tour, departement_wiki, find_circo, jours_election,
                    ordinal, recuperer_politiciens_wikidata, remove_accents)

# Première colonne de nuance dans les fichiers 1958-1981.
PREMIERE_NUANCE_T1 = 7
PREMIERE_NUANCE_T2 = 8
# Nombre maximal de candidats au second tour (1988-2012).
MAX_CANDIDATS_T2 = 3


def afficher_participation(ligne, suffixe=""):
    print(f"| inscrits{suffixe} = {int(ligne['Inscrits'])}")
    print(f"| votants{suffixe} = {int(ligne['Votants'])}")
    print(f"| exprimes{suffixe} = {int(ligne['Exprimés'])}")


def afficher_candidat(numero, nom, parti, suffrages):
    """Affiche les lignes d'un candidat ; ``parti`` = (libellé, couleur)."""
    libelle, couleur = parti
    print(f"| candidat{numero} = {nom}")
    print(f"| parti{numero} = {libelle}")
    print(f"| suffrages{numero} = {suffrages[0]}")
    if len(suffrages) > 1 and suffrages[1] != 0:
        print(f"| suffrages{numero}b = {suffrages[1]}")
    print(f"| hex{numero} = {couleur}")


def lien_candidat(prenom, nom, politiciens):
    """Nom du candidat, avec un lien vers son article s'il en a un."""
    nom_complet = f"{prenom} {nom}"
    page = politiciens.get(nom_complet)
    if page is None:
        return nom_complet
    if page == nom_complet:
        return f"[[{nom_complet}]]"
    if remove_accents(page) == nom_complet:
        # Seuls les accents diffèrent : le titre de l'article suffit.
        return f"[[{page}]]"
    return f"[[{page}|{nom_complet}]]"


def corps_ancien(premier_tour, second_tour, monotour):
    """Candidats des élections 1958-1981 (une colonne par nuance, pas de nom)."""
    ligne_t1 = premier_tour.iloc[0]
    voix = {nuance: [ligne_t1[nuance]]
            for nuance in premier_tour.columns[PREMIERE_NUANCE_T1:]}

    if not monotour:
        ligne_t2 = second_tour.iloc[0]
        for nuance in second_tour.columns[PREMIERE_NUANCE_T2:]:
            if nuance not in voix:
                continue
            cible = nuance
            # Au second tour 1973, la colonne RIUDR regroupe les candidats
            # RI et UDR présents séparément au premier tour.
            if nuance == 'RIUDR':
                if 'RI' in voix and voix['RI'][0] > 0:
                    cible = 'RI'
                elif 'UDR' in voix and voix['UDR'][0] > 0:
                    cible = 'UDR'
            voix[cible].append(int(ligne_t2[nuance]))
        afficher_participation(ligne_t2, suffixe="2")

    numero = 1
    for nuance, suffrages in sorted(voix.items(), key=lambda x: x[1],
                                    reverse=True):
        if suffrages in ([0], [0, 0]):
            continue
        afficher_candidat(numero, "Inconnu", partis.parti_ancien(nuance),
                          suffrages)
        numero += 1
    print("}}")


def corps_recent(premier_tour, second_tour, monotour, politiciens):
    """Candidats des élections 1988-2012 (nom, nuance et étiquette connus)."""
    infos = {}
    voix = {}
    for candidat in candidats(premier_tour.iloc[0]):
        cle = candidat['cle']
        etiquette = candidat['etiquette']
        if not isinstance(etiquette, str):
            etiquette = partis.ETIQUETTE_VIDE
        else:
            etiquette = etiquette.title()
        infos[cle] = (candidat['prenom'].title(), candidat['nom'].title(),
                      etiquette)
        voix[cle] = [candidat['voix']]

    if not monotour:
        ligne_t2 = second_tour.iloc[0]
        for candidat in candidats(ligne_t2, maximum=MAX_CANDIDATS_T2):
            voix[candidat['cle']].append(candidat['voix'])
        afficher_participation(ligne_t2, suffixe="2")

    for numero, (cle, suffrages) in enumerate(
            sorted(voix.items(), key=lambda x: x[1], reverse=True), start=1):
        prenom, nom, etiquette = infos[cle]
        afficher_candidat(numero, lien_candidat(prenom, nom, politiciens),
                          partis.parti_recent(cle, etiquette), suffrages)
    print("}}")


def election(annee, departement, circonscription, politiciens):
    """Affiche le modèle {{Résultats électoraux}} d'une élection."""
    premier_tour = find_circo(charger_tour(annee, 1), departement, circonscription)
    second_tour = find_circo(charger_tour(annee, 2), departement, circonscription)
    if premier_tour.empty:
        return

    # Avant 1981, le fichier du second tour liste toutes les circonscriptions
    # et indique si le député a été élu dès le premier tour.
    monotour = second_tour.empty or (
        annee < 1981 and str(second_tour.iloc[0]['élu premier tour']) == 'O')

    nom_dep, preposition = departement_wiki(departement)
    date_premier_tour = DATES_ELECTIONS[annee][0].strftime("%d/%m/%Y")

    print(f"=== Élections de {annee} ===")
    print("{{Résultats électoraux|candidats" if monotour else "{{Résultats électoraux|2tours")
    print(f"| titre = Résultats des élections législatives des "
          f"{jours_election(annee)} {annee} de la {ordinal(circonscription)} "
          f"circonscription {preposition}{nom_dep}")
    print(f"| references = <ref>Résultats des élections législatives françaises "
          f"premier tour du {date_premier_tour} par circonscription, "
          f"cdsp_legi{annee}t1_circ.xls [fichier informatique], Banque de Données "
          f"Socio-Politiques, Grenoble [producteur], Centre de Données "
          f"Socio-politiques [diffuseur], février 2009.</ref>")
    afficher_participation(premier_tour.iloc[0])

    if annee >= 1988:
        corps_recent(premier_tour, second_tour, monotour, politiciens)
    else:
        corps_ancien(premier_tour, second_tour, monotour)
    print("\n")


def main():
    parser = argparse.ArgumentParser(
        description="Génère le wikicode des résultats des élections "
                    "législatives (1958-2012) d'une circonscription.")
    parser.add_argument("-d", "--departement", required=True,
                        help="nom du département, ex. PAS-DE-CALAIS "
                             "(casse et accents indifférents)")
    parser.add_argument("-c", "--circo", required=True, type=int,
                        help="numéro de la circonscription")
    parser.add_argument("-a", "--annee", type=int, nargs="+",
                        choices=ANNEES_DISPONIBLES, metavar="ANNEE",
                        help="années à traiter (par défaut : toutes)")
    parser.add_argument("--sans-wikidata", action="store_true",
                        help="ne pas interroger Wikidata (pas de liens "
                             "vers les articles des candidats)")
    args = parser.parse_args()

    politiciens = {} if args.sans_wikidata else recuperer_politiciens_wikidata()
    for annee in args.annee or ANNEES_DISPONIBLES:
        election(annee, args.departement, args.circo, politiciens)


if __name__ == "__main__":
    main()

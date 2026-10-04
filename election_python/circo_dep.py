"""Brouillon d'article « Élections législatives de <année> en <département> ».

Génère l'infobox (participation agrégée sur le département), la liste des
candidats par circonscription (1988-2012) et le squelette de l'article.
Ce script est un travail en cours : le tableau des élus reste à compléter.

Exemple :
    python circo_dep.py -d HAUTE-SAVOIE -y 2012 > brouillon.txt
"""

import argparse

import partis
from commun import (ANNEES_DISPONIBLES, DATES_ELECTIONS, MOIS, candidats,
                    charger_tour, departement_wiki, find_departement, ordinal)


def date_infobox(annee):
    """Dates des deux tours au format du modèle {{date}}."""
    premier, second = DATES_ELECTIONS[annee]
    return (f"{{{{date|{premier.day}|{MOIS[premier.month - 1]}-|{annee}-}}}} et "
            f"{{{{date|{second.day}|{MOIS[second.month - 1]}|{annee}}}}}")


def elections_voisines(annee):
    """Années de l'élection précédente et suivante (None si inconnue)."""
    annees = list(DATES_ELECTIONS)
    index = annees.index(annee)
    precedente = annees[index - 1] if index > 0 else None
    suivante = annees[index + 1] if index + 1 < len(annees) else None
    return precedente, suivante


def totaux(dataframe):
    """Inscrits, votants et exprimés cumulés sur le département."""
    return {colonne: int(dataframe[colonne].sum())
            for colonne in ('Inscrits', 'Votants', 'Exprimés')}


def participation(totaux_tour):
    return round(totaux_tour['Votants'] / totaux_tour['Inscrits'] * 100, 2)


def afficher_infobox(annee, nom_dep, nb_circonscriptions, premier, second,
                     precedent):
    annee_pre, annee_post = elections_voisines(annee)
    print("{{Infobox Élection")
    print(" | pays                   = France")
    print(f" | date élection          = {date_infobox(annee)}")
    print(f" | endispute              = {nb_circonscriptions} sièges de députés "
          f"à l'[[Assemblée nationale (France)|Assemblée nationale]]")
    if annee_pre is not None:
        print(f" | élection précédente    = Élections législatives de {annee_pre} en {nom_dep}")
        print(f" | date précédente        = {date_infobox(annee_pre)}")
    if annee_post is not None:
        print(f" | élection suivante      = Élections législatives de {annee_post} en {nom_dep}")
        print(f" | date suivante          = {date_infobox(annee_post)}")
    print(" | type                   = [[Élections législatives en France|Élections législatives]]")
    print(" | habitants              = ")
    print(f" | enregistrés            = {premier['Inscrits']}")
    print(f" | votants                = {premier['Votants']}")
    print(f" | votants2               = {second['Votants']}")
    print(f" | participation          = {participation(premier)}")
    print(" | participation ref      = ")
    print(f" | participation pré      = {participation(precedent) if precedent else ''}")
    print(f" | participation2         = {participation(second)}")
    print(" | participation2 ref     = ")
    print(f" | valables               = {premier['Exprimés']}")
    print(f" | valables2              = {second['Exprimés']}")
    print(" | nom élus               = députés")
    print(" | campagne               = ")
    print(" | débat                  = ")
    print("}}")


def afficher_candidats(premier_tour):
    """Liste, pour chaque circonscription, les candidats du premier tour
    par nombre de voix décroissant."""
    for _, ligne in premier_tour.iterrows():
        print(f"=== {ordinal(int(ligne['circonscription']))} circonscription ===")
        for candidat in sorted(candidats(ligne), key=lambda c: c['voix'],
                               reverse=True):
            etiquette = candidat['etiquette']
            etiquette = etiquette.title() if isinstance(etiquette, str) else partis.ETIQUETTE_VIDE
            libelle, _ = partis.parti_recent(candidat['cle'], etiquette)
            print(f"* {candidat['prenom'].title()} {candidat['nom'].title()} "
                  f"({libelle}) : {candidat['voix']} voix")
        print()


def election(annee, departement):
    nom_dep, preposition = departement_wiki(departement)
    premier_tour = find_departement(charger_tour(annee, 1), departement)
    second_tour = find_departement(charger_tour(annee, 2), departement)
    if premier_tour.empty:
        raise SystemExit(f"Département introuvable pour {annee} : {departement}")

    annee_pre, _ = elections_voisines(annee)
    precedent = None
    if annee_pre in ANNEES_DISPONIBLES:
        precedent = totaux(find_departement(charger_tour(annee_pre, 1), departement))

    afficher_infobox(annee, nom_dep, premier_tour.shape[0],
                     totaux(premier_tour), totaux(second_tour), precedent)
    print()

    if annee >= 1988:
        print("== Candidats ==")
        afficher_candidats(premier_tour)

    print("== Élus ==")
    print()
    print("{| style=\"text-align: center;line-height:14px;\" class=\"wikitable centre\"")
    print("|+")
    print("! scope=\"col\" |Circonscription")
    print("! scope=\"col\" |Député sortant")
    print("! colspan=\"2\" scope=\"col\" |Parti")
    print("! scope=\"col\" |Député élu ou réélu")
    print("! colspan=\"2\" scope=\"col\" |Parti")
    print("|-")
    print("|}")
    print()

    decennie = annee // 10 * 10
    print("== Notes et références ==")
    print("{{Références}}")
    print()
    print("== Articles connexes ==")
    print(f"* [[Liste des circonscriptions législatives {preposition}{nom_dep}]]")
    print(f"* [[Liste des députés {preposition}{nom_dep}]]")
    print(f"* [[Élections législatives françaises de {annee}]]")
    print()
    print(f"{{{{Palette|Élections législatives de {annee} en France}}}}")
    print(f"{{{{Portail|années {decennie}|politique française|{nom_dep}}}}}")
    print()
    print(f"[[Catégorie:Élections législatives françaises de {annee}|Législatives, {annee}]]")
    print(f"[[Catégorie:Élection en {nom_dep}|{nom_dep}]]")


def main():
    parser = argparse.ArgumentParser(
        description="Génère un brouillon d'article sur les élections "
                    "législatives d'une année dans un département.")
    parser.add_argument("-d", "--departement", required=True,
                        help="nom du département, ex. HAUTE-SAVOIE "
                             "(casse et accents indifférents)")
    parser.add_argument("-y", "--year", required=True, type=int,
                        choices=ANNEES_DISPONIBLES, metavar="ANNEE",
                        help="année de l'élection")
    args = parser.parse_args()
    election(args.year, args.departement)


if __name__ == "__main__":
    main()

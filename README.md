# wikipedia_scripts

Scripts utilitaires pour contribuer à Wikipédia en français et à Wikidata.

| Dossier | Contenu |
|---|---|
| [`election_python/`](election_python) | Génération du wikicode des résultats des élections législatives françaises (1958-2012) |
| [`effectif_enseignement_supp/`](effectif_enseignement_supp) | Import sur Wikidata du nombre d'étudiants des établissements d'enseignement supérieur |
| [`AOC_svg_auto_color/`](AOC_svg_auto_color) | Requête SPARQL donnant le code INSEE de communes (coloriage de cartes SVG d'AOC) |

## Installation

Python 3.9 ou plus récent.

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Élections législatives (`election_python/`)

Les scripts lisent les résultats par circonscription publiés par le Centre de
Données Socio-Politiques (CDSP, Sciences Po Grenoble), rangés dans
`election_python/excel_file/`, et affichent du wikicode sur la sortie standard.

### `circo.py` : résultats d'une circonscription

Génère, pour chaque élection de 1958 à 2012 (hors 1986, scrutin
proportionnel), un modèle `{{Résultats électoraux}}` prêt à coller dans
l'article de la circonscription.

```sh
cd election_python
python circo.py -d PAS-DE-CALAIS -c 14 > resultats.txt
python circo.py -d "Côte-d'Or" -c 2 -a 2007 2012 --sans-wikidata
```

| Option | Description |
|---|---|
| `-d`, `--departement` | nom du département (casse, accents et tirets indifférents) |
| `-c`, `--circo` | numéro de la circonscription |
| `-a`, `--annee` | années à traiter (par défaut : toutes) |
| `--sans-wikidata` | ne pas interroger Wikidata |

Fonctionnement :

* **1958-1981** : les fichiers donnent les voix par nuance politique, sans le
  nom des candidats, qui apparaissent comme « Inconnu » et sont à compléter à
  la main.
* **1988-2012** : les candidats sont nommés. Une requête Wikidata récupère les
  personnalités politiques françaises ayant un article ; leurs noms deviennent
  des liens. Le parti est déduit de la nuance et, pour les nuances
  « fourre-tout » (divers droite, extrême gauche...), de l'étiquette déclarée.

Les libellés et couleurs des partis sont définis dans `partis.py` : c'est le
fichier à compléter lorsqu'une étiquette s'affiche telle quelle ou qu'un
`error` apparaît dans la sortie.

### `circo_dep.py` : brouillon d'article départemental (en cours)

Génère le squelette d'un article « Élections législatives de *année* en
*département* » : infobox avec la participation agrégée, liste des candidats
par circonscription (1988-2012), tableau des élus (à remplir), articles
connexes, portails et catégories.

```sh
python circo_dep.py -d HAUTE-SAVOIE -y 2012 > brouillon.txt
```

### Organisation du code

| Fichier | Rôle |
|---|---|
| `commun.py` | dates des scrutins, noms des départements, chargement des fichiers, requête Wikidata |
| `partis.py` | correspondance nuance / étiquette → libellé wiki et couleur |
| `circo.py`, `circo_dep.py` | scripts en ligne de commande |

### Données

`excel_file/` contient les fichiers du CDSP :

* `cdsp_legi<année>t<tour>_circ.xls[x]` : résultats par circonscription,
  utilisés par les scripts ;
* `cdsp_legi<année>t<tour>_comm*.xls` : résultats par commune (non utilisés
  pour l'instant) ;
* `cdsp_legi1981_source_5ecirc_ValdOise.pdf` : source des résultats de 1981
  dans la 5ᵉ circonscription du Val-d'Oise.

Ces fichiers ont été corrigés à la main par rapport aux originaux du CDSP
(coquilles dans les codes de nuance, numérotation des circonscriptions du
Val-d'Oise en 1967 et 1973...). Citation demandée par le CDSP :

> Résultats des élections législatives françaises par circonscription,
> Banque de Données Socio-Politiques, Grenoble [producteur], Centre de Données
> Socio-politiques [diffuseur], 2009.

## Effectifs étudiants (`effectif_enseignement_supp/`)

`effectif.py` ajoute sur l'élément Wikidata de chaque établissement le nombre
d'étudiants inscrits (P2196) pour chaque année universitaire, avec la date
(P585) en qualificatif et la source en référence. Les années déjà présentes
sur l'élément sont ignorées.

1. Télécharger le CSV du jeu de données
   [Statistiques sur les effectifs d'étudiants inscrits par établissement](https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-statistiques-sur-les-effectifs-d-etudiants-inscrits-par-etablissement-hcp/).
2. [Configurer Pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot/user-config.py)
   avec un compte autorisé à modifier Wikidata (idéalement un compte bot).
3. Lancer d'abord une simulation, puis l'import :

```sh
cd effectif_enseignement_supp
python effectif.py effectifs.csv --date-consultation 2023-12-15 --simulation
python effectif.py effectifs.csv --date-consultation 2023-12-15
```

En cas d'interruption, `--debut N` reprend au N-ième établissement (index
affiché entre crochets).

## Codes INSEE des communes (`AOC_svg_auto_color/`)

`INSEE_code_request.SPARQL` renvoie l'élément Wikidata et le code INSEE de
communes à partir du titre de leur article sur Wikipédia en français. Remplacer
la liste de communes puis l'exécuter sur <https://query.wikidata.org/>.

## Licence

[GNU GPL v3](LICENSE).

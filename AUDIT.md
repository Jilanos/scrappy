# Scrappy — Audit de début de projet

> Date: 2026-06-24
> Périmètre: état du dépôt, architecture, écart avec la vision produit, bugs, et feuille de route.
> Statut de cet audit: les correctifs « importants et évidents » ont été implémentés (voir §6). Le reste est listé en questions ouvertes (§7).

## 1. La vision (cible)

Outil qui compare un CV aux offres publiées sur plusieurs sites, les score selon leur proximité avec le profil, avec un **double usage** :

1. **Préparer des CV et lettres de motivation adaptés** à chaque offre.
2. **Repérer les offres qui scoreraient beaucoup plus haut si une compétence clé apparaissait dans le profil**, et en sortie **les compétences à développer qui « boosteraient » le plus le CV**.

## 2. Ce qui existe aujourd'hui (et qui marche)

Le MVP livré couvre la **première moitié** de la vision (comparer/scorer) de façon solide :

| Brique | État | Détail |
| --- | --- | --- |
| Collecte multi-sources | ✅ | WTTJ (Algolia public), Indeed (adaptateur API/Apify configurable), France Travail (OAuth) |
| Persistance | ✅ | SQLite : `offers`, `runs`, `source_observations`, `analyses`, `offer_aliases`, `manual_reviews` ; migrations versionnées |
| Déduplication | ✅ | par URL canonique, `source:source_id`, et empreinte titre/entreprise/localisation |
| Re-traitement évité | ✅ | `content_hash` ; une offre inchangée n'est pas réanalysée |
| Scoring explicable | ✅ | heuristique déterministe avec gates (localisation, contrat, séniorité, domaine) et `strengths`/`gaps`/`risks`/`reasons` |
| Sorties | ✅ | console + classeur XLSX (`all_scored`, `rejected`) sans dépendance externe |
| Boucle de revue | ✅ | `import-reviews` réimporte les décisions manuelles ; `rescore` rejoue tout l'historique |
| Tests | ✅ | 37 tests verts (`pytest`) |
| Couche Logics | ✅ | request / product / ADR / backlog / tasks bien documentés |

**Architecture** : propre et conforme à l'ADR. Quatre frontières nettes — *connecteurs → normalisation/dédup → scoring → présentation*. Zéro dépendance runtime (Python ≥3.11, stdlib seule, y compris l'écriture XLSX). Connecteurs remplaçables via une interface commune (`discover_with_stats` / `DiscoveryResult`).

## 3. Écart principal avec la vision

| Usage cible | État avant audit | État après audit |
| --- | --- | --- |
| Scorer les offres | ✅ fait | ✅ fait |
| **Compétences à développer qui boostent le CV** | ❌ absent | ✅ **implémenté** (§6) |
| Génération CV / lettre adaptés | ❌ absent (acté « hors MVP », données préservées) | ⏳ différé — décision de format requise (§7) |

## 4. Bugs / faiblesses relevés

1. **Faux positifs de matching de compétences** *(corrigé)* — `scoring._matched_terms` faisait un simple `terme in texte`. La compétence `C` (secondaire) matchait donc « scien**c**e », « électroni**c**s », etc. Tout texte d'offre déclenchait un faux « hit » sur `C`, gonflant le score secondaire et affichant `C` comme point fort à tort.
2. **Matching de gates par sous-chaîne** *(non modifié, à surveiller)* — `_contains_any` (contrat, localisation, exclusions) reste en sous-chaîne. Acceptable pour le MVP (les termes sont longs : `cdi`, `internship`, `paris`…) mais peut produire des faux positifs (`stage` ⊂ « back**stage** »). Changement plus risqué pour les gates → laissé en suivi.
3. **Parser YAML maison** — `profile.py` ne gère qu'un sous-ensemble (mappings imbriqués + listes de chaînes). Volontaire pour rester sans dépendance, mais fragile si le profil se complexifie. Migration vers PyYAML possible plus tard.
4. **Plafond de score à 49 pour les non-éligibles** — `score = min(score, 49)`. Conserve le tri éligibles/non-éligibles, mais écrase la granularité fine des offres non-éligibles. Sans impact sur l'analyse de boost (le signal clé y est le *unlock* / passage à éligible), mais à garder en tête si on veut comparer finement des offres rejetées.
5. **`data/scrappy.sqlite` versionné** — une base avec des données réelles est committée. À confirmer : doit-elle l'être (fixture) ou être ignorée comme `.env.local` ?

## 5. Qualité / risques transverses

- **Connecteurs dépendants de surfaces non officielles** : WTTJ via endpoint Algolia public (clé extraite du bundle web) — peut casser sans préavis. Bien isolé derrière la frontière connecteur, conforme à l'ADR. Indeed/France Travail demandent des credentials.
- **Pas de tests réseau réels** : les connecteurs sont testés sur des payloads/fixtures, pas en live (normal et sain pour la CI).
- **Pas de CI configurée** dans le dépôt (pas de workflow GitHub Actions repéré).

## 6. Modifications implémentées dans cet audit

### 6.1 Correctif matching (sûr, ciblé)
`scoring._matched_terms` utilise désormais un matching ancré sur les bornes de tokens (`_term_regex`, avec cache `lru_cache`). `C`, `C++`, `C#` restent précis ; les compétences multi-mots (`signal processing`) continuent de matcher. Aucun test existant cassé.

### 6.2 Analyse de boost de compétences — `scrappy/growth.py` (feature phare)
Répond directement à la 2ᵉ moitié de la vision. Pour chaque **compétence candidate** (déclarée dans `profile.yaml › growth.candidate_skills`), on **ré-score chaque offre stockée** avec un profil hypothétiquement augmenté de cette compétence, puis on agrège :

- `offers_unlocked` : offres qui passent de non-éligible → éligible (offres bloquées *uniquement* par l'absence de compétence-domaine — exactement « les offres qui scoreraient beaucoup plus si une compétence clé apparaissait ») ;
- `offers_boosted` : offres dont le score augmente ;
- `total_score_gain` / `avg_score_gain` : points gagnés.

Le classement est honnête : une compétence ne « boost » que les offres qui la mentionnent réellement (le matching est l'intersection profil ∩ texte d'offre), et ne débloque jamais une offre rejetée pour cause de localisation/contrat/séniorité.

Livré avec :
- section `growth.candidate_skills` dans `examples/profile.yaml` (liste éditable, pré-remplie pour un profil deeptech/imagerie) ;
- commande CLI `skill-gaps` (console + classeur XLSX `skill_boosts`) ;
- 6 tests (`tests/test_growth.py` + 1 test CLI).

**Exemple sur la base réelle (114 offres)** :
```
1. embedded systems -> unlocks 0 offer(s), boosts 4 (+24 pts total, avg +6.0)
2. machine learning -> unlocks 0 offer(s), boosts 4 (+24 pts total, avg +6.0)
3. RF              -> unlocks 0 offer(s), boosts 3 (+18 pts total, avg +6.0)
...
```

Usage :
```bash
python3 -m scrappy skill-gaps --db data/scrappy.sqlite --profile examples/profile.yaml --top 10
```

## 7. Questions ouvertes / développements ultérieurs

Listés par valeur décroissante. Chacun demande une décision ou un cadrage avant implémentation.

1. **Génération CV + lettre adaptés (usage n°1).** Décision de format requise (l'ADR/produit laisse la question ouverte) :
   - PPT→PDF + Word (cible initiale évoquée), **ou** Markdown/HTML/LaTeX (plus modulaire, plus simple à générer/tester) ?
   - Génération par templates déterministes, ou assistée par LLM (Claude) avec le texte d'offre + les `gaps`/`strengths` déjà stockés comme contexte ?
2. **Découverte automatique des compétences candidates.** Aujourd'hui la liste `growth.candidate_skills` est déclarée à la main. Faut-il **extraire automatiquement** du corpus d'offres les compétences fréquentes absentes du profil (avec un vocabulaire/ontologie de skills) pour suggérer des candidats qu'on n'aurait pas pensé à lister ?
3. **Vue « par offre » des compétences manquantes.** En complément du classement agrégé, exposer pour chaque offre non-éligible la (les) compétence(s) qui la débloquerai(en)t — utile pour décider offre par offre.
4. **Calibrage des seuils et du plafond à 49.** Faut-il un vrai score continu pour les non-éligibles afin de comparer finement les offres « presque bonnes » ?
5. **Pondération du scoring** (question produit ouverte) : favoriser les compétences actuelles, celles à développer, ou un mix configurable ?
6. **Connecteur LinkedIn** : non implémenté (APIs orientées partenaires). À cadrer si la couverture LinkedIn est souhaitée.
7. **Matching sémantique** (embeddings) derrière la frontière scoring, si l'heuristique par mots-clés montre ses limites.
8. **Hygiène dépôt** : sortir `data/scrappy.sqlite` du suivi git si ce n'est pas une fixture ; ajouter une CI (`pytest`).
9. **`_contains_any` ancré sur bornes de tokens** pour les gates (cf. §4.2), si des faux positifs apparaissent en usage réel.

## 8. Comment vérifier l'état actuel

```bash
python3 -m pytest -q                 # 37 tests verts
python3 -m scrappy skill-gaps --db data/scrappy.sqlite --profile examples/profile.yaml
```

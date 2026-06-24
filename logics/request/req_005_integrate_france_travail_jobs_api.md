## req_005_integrate_france_travail_jobs_api - Integrer l API Offres d emploi France Travail
> From version: 1.0.0
> Schema version: 1.0
> Status: Done
> Understanding: 95
> Confidence: 90
> Complexity: Medium
> Theme: Provider expansion
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.

# Needs
- Integrer l'API Offres d'emploi France Travail comme provider gratuit/officiel dans Scrappy afin d'augmenter le pool d'offres France/Paris sans dependance a une API Indeed payante.
- Permettre une collecte automatique France Travail via OAuth client credentials, normalisation vers le modele `Offer`, scoring commun, deduplication inter-source et export XLSX.
- Valider que cette source apporte des offres pertinentes pour le profil cible, notamment CDI/full-time, Paris, full remote ou hybride substantiel, avec requetes profil ciblees.

# Context
- La task Indeed tierce reste ouverte parce qu'Apify est payant et qu'aucun token n'est disponible localement. France Travail devient la prochaine source prioritaire car elle est officielle, gratuite et plus alignee avec le perimetre France/Paris.
- L'API Offres d'emploi restitue en temps reel les offres actives collectees par France Travail ou recues de partenaires ayant consenti a leur mise a disposition.
- L'API necessite une application France Travail et une authentification OAuth avec client id / client secret.
- Scrappy dispose deja d'une orchestration multi-provider, de stats provider homogenes, de deduplication inter-source, du scoring commun, et du XLSX `all_scored` / `rejected`.
- L'objectif reste la qualite du top plutot que le volume brut: les requetes doivent rester ciblees sur le profil.

# Acceptance criteria
- AC1: La CLI supporte un provider `france-travail` activable avec `--provider france-travail`, compatible avec les providers existants.
- AC2: Le connecteur France Travail obtient et utilise un token OAuth depuis des variables d'environnement locales, sans stocker de secret dans le depot.
- AC3: Les offres France Travail sont mappees vers `Offer` avec au minimum identifiant stable, titre, entreprise, localisation, contrat, description/snippet, URL et champs remote/salaire si disponibles.
- AC4: La collecte utilise les requetes profil ciblees et le perimetre Paris/full remote/substantial hybrid; les offres hors cible restent visibles avec raisons de rejet/downrank dans le XLSX.
- AC5: Les stats provider affichent hits bruts, offres uniques, target atteint/non atteint, pagination/range utilisee, et warnings API.
- AC6: La deduplication inter-source fonctionne entre France Travail, WTTJ et futurs providers en conservant les identifiants source.
- AC7: Un smoke reel France Travail seul produit un XLSX exploitable.
- AC8: Un smoke reel WTTJ + France Travail produit un XLSX exploitable et continue avec warning si un provider echoue.
- AC9: La documentation explique comment creer/configurer l'application France Travail, quelles variables d'environnement utiliser, les scopes/API requis, limites connues et commandes de validation.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Scope
- In:
  - documenter la creation/configuration d'une application France Travail;
  - ajouter un connecteur `FranceTravailConnector`;
  - ajouter `france-travail` aux providers CLI;
  - implementer OAuth client credentials avec cache memoire simple par execution;
  - mapper les resultats d'offres vers `Offer`;
  - paginer selon le contrat de l'API;
  - ajouter tests fixtures et smoke reel si credentials presents;
  - documenter limites et erreurs courantes.
- Out:
  - scraping du site France Travail;
  - candidature automatique;
  - stockage des secrets;
  - changement du scoring hors ajustements necessaires aux champs France Travail;
  - garantie de volume eleve si les requetes ciblees produisent peu d'offres.

# Configuration target
- `SCRAPPY_FRANCE_TRAVAIL_CLIENT_ID`
- `SCRAPPY_FRANCE_TRAVAIL_CLIENT_SECRET`
- `SCRAPPY_FRANCE_TRAVAIL_SCOPE` si necessaire
- `SCRAPPY_FRANCE_TRAVAIL_LOCATION` par defaut Paris / departement 75 selon contrat API

# Required validation commands
- `python3 -m pytest`
- `python3 -m scrappy run --provider france-travail --target-offers 20 --max-pages 2 --xlsx /tmp/scrappy-france-travail.xlsx`
- `python3 -m scrappy run --provider wttj-public --provider france-travail --target-offers 20 --max-pages 2 --xlsx /tmp/scrappy-wttj-france-travail.xlsx`
- `logics-manager lint --require-status`
- `logics-manager audit --group-by-doc`
- `logics-manager health`

# Companion docs
- Product brief(s): (none yet)
- Architecture decision(s): (none yet)

# References
- API France Travail Offres d'emploi: `https://api.gouv.fr/les-api/api_offresdemplois`
- Data.gouv API Offres d'emploi: `https://www.data.gouv.fr/dataservices/api-offres-demploi`
- Existing multi-provider CLI: `scrappy/cli.py`
- Existing connector contract: `scrappy/connectors/base.py`
- Current storage/deduplication: `scrappy/storage.py`
- Prior Indeed API validation request: `req_004_validate_third_party_indeed_api`

# AI Context
- Summary: Integrate the official France Travail job offers API as a free provider for Scrappy.
- Keywords: france-travail, pole-emploi, jobs-api, oauth, provider, paris, free-api, offres-emploi
- Use when: Implementing or validating France Travail as a Scrappy job source.
- Skip when: Work concerns paid Indeed APIs or WTTJ-only behavior.

# Backlog
- none
- `item_006_integrer_l_api_offres_d_emploi_france_travail`

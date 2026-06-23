## prod_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi - MVP outil local de veille et scoring d'offres d'emploi
> Date: 2026-06-23
> Status: Proposed
> Related request: `req_000_mvp_job_reviewer`
> Related backlog: `item_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi`
> Related task: (none yet)
> Related architecture: `adr_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi`
> Reminder: Update status, linked refs, scope, decisions, success signals, and open questions when you edit this doc.

# Overview
Le produit est un assistant local de veille d'offres d'emploi. Il aide l'utilisateur a concentrer son temps sur les annonces les plus proches de son profil, en memorisant ce qui a deja ete vu et en expliquant les ecarts entre une offre et ses competences, envies et contraintes.

```mermaid
%% logics-kind: product
%% logics-signature: product|mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi|generated
flowchart TD
    Profile[Local profile] --> Score[Explainable scoring]
    Sources[Configured sources] --> Store[SQLite history]
    Store --> Score
    Score --> Top[Ranked shortlist]
```

# Goals
- Reduire le temps passe a relire les memes offres sur plusieurs plateformes.
- Identifier rapidement les offres les plus pertinentes avec des raisons lisibles.
- Conserver un historique local des offres vues, analysees et ignorees.
- Poser une base de donnees exploitable pour une phase ulterieure de CV et lettre adaptes.

# Non-goals
- Postuler automatiquement.
- Se connecter a des comptes personnels ou contourner les limitations des plateformes.
- Generer le CV ou la lettre de motivation dans le MVP.
- Remplacer le jugement utilisateur par une decision automatique.
- Fournir une interface graphique dans la premiere version.

# Scope and guardrails
- In: CLI locale, configuration de sources, profil utilisateur local, base SQLite, deduplication, analyse des nouvelles offres, classement interpretable.
- In: modele de donnees preservant titre, entreprise, localisation, remote, salaire si disponible, description, URL, source, empreinte de contenu, score, raisons et ecarts.
- Out: automatisation de candidature, scraping authentifie, orchestration cloud, synchronisation multi-utilisateur.
- Guardrail: l'outil doit documenter clairement que chaque connecteur depend des conditions et contraintes de la source cible.

# Key product decisions
- Le MVP est local-first: donnees et profil restent sur la machine de l'utilisateur.
- Le premier scoring doit etre interpretable avant d'etre intelligent: une heuristique transparente est acceptable si elle expose ses raisons.
- Les connecteurs de sources sont des modules remplacables, car LinkedIn, Welcome to the Jungle et Indeed changent leurs pages et politiques.
- Les offres deja vues restent visibles dans la base mais ne sont pas reanalysees tant que leur empreinte ne change pas.
- La sortie initiale peut etre console/Markdown/CSV avant toute interface.

# Success signals
- Une execution consecutive sans nouvelle offre ne retraite rien.
- Une nouvelle offre pertinente apparait dans le top avec des raisons comprehensibles.
- Une offre faible est classee bas avec les ecarts principaux visibles.
- Ajouter une nouvelle source ne demande pas de modifier le stockage ni le scoring.
- Les donnees stockees suffisent a alimenter plus tard un brouillon de CV ou lettre.

# Primary user workflow
- L'utilisateur met a jour son profil local.
- L'utilisateur configure ou fournit des sources d'offres.
- L'utilisateur lance la commande de collecte/analyse.
- L'outil enregistre les offres inconnues, ignore les doublons et analyse les nouveautes.
- L'utilisateur consulte le top et decide quelles offres approfondir.

# Open questions
- Quel format de profil initial est le plus pratique: YAML simple, JSON ou import depuis un CV existant?
- Quelle source doit etre supportee en premier pour le MVP: fichier d'URLs, export manuel, flux public, ou connecteur Playwright controle?
- Le scoring doit-il favoriser les competences actuelles, les competences a developper, ou un mix configurable?

# References
- Product back-reference: `item_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi`
- Task back-reference: (none yet)

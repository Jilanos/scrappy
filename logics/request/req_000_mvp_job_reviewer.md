## req_000_mvp_job_reviewer - MVP outil local de veille et scoring d'offres d'emploi
> From version: 1.0.0
> Schema version: 1.0
> Status: Draft
> Understanding: 95
> Confidence: 90
> Complexity: Medium
> Theme: Operator workflow
> Reminder: Update status/understanding/confidence and linked backlog/task references when you edit this doc.

# Needs
- Mettre en place un MVP local qui collecte des offres d'emploi depuis des sources configurees, detecte les offres deja rencontrees, analyse uniquement les nouvelles offres contre le profil utilisateur, puis restitue un classement des opportunites les plus pertinentes.
- Construire la base de donnees et le modele de donnees de facon a preparer une phase ulterieure de generation de CV et lettres de motivation adaptes.

# Context
- Les sources cibles sont LinkedIn, Welcome to the Jungle et Indeed, avec une approche prudente: le MVP doit privilegier une integration API ou des pages publiques autorisees plutot qu'un scraping authentifie fragile.
- Le premier MVP utilisera un seul provider, choisi pour maximiser la facilite d'acces et la stabilite technique. Welcome to the Jungle est le candidat initial a valider, car une API officielle existe mais peut demander token ou partenariat.
- Les exports manuels ne sont pas la source cible du produit. Ils peuvent rester utiles uniquement pour tests locaux ou fixtures de developpement.
- L'outil tourne localement et uniquement a la demande de l'utilisateur.
- La base locale conserve l'historique des offres vues pour eviter de retraiter les memes annonces lors des executions suivantes.
- Le profil utilisateur initial sera derive d'un CV fourni par l'utilisateur, puis encode dans un fichier local declaratif et versionnable afin de pouvoir ajuster competences, niveaux, langues, envies, contraintes et mots-cles sans modifier le code.
- Le scoring doit expliquer pourquoi une offre est proche ou eloignee du profil, pas seulement fournir une note opaque.
- La localisation est un filtre obligatoire: Paris ou full remote. Les offres hors contrainte doivent etre ecartees ou classees comme non eligibles avant le top.
- Le scoring initial doit surtout mesurer skill match et seniority match. Le salaire est optionnel et peu structurant pour le marche francais, car il est rarement indique.
- Le MVP partira d'un panel de base pour construire l'outil. Plus tard, quand le profil et le scoring seront plus precis, l'historique complet devra pouvoir etre rescored.
- La future generation de documents partira aujourd'hui d'un support PPT permettant de former un PDF pour le CV et d'un document Word pour la lettre. Des formats plus modulaires comme HTML, Markdown ou LaTeX restent ouverts si cela simplifie la generation.

# Acceptance criteria
- AC1: Une execution locale peut ingerer des offres nouvelles depuis un provider initial configure, idealement par API officielle ou sinon via pages publiques autorisees, et les enregistrer dans une base SQLite.
- AC2: Une offre deja rencontree est reconnue et n'est pas analysee une seconde fois, sauf si son contenu source a change.
- AC3: Chaque nouvelle offre analysee recoit un score de pertinence, un niveau d'ecart au profil et des raisons lisibles.
- AC4: La sortie presente un top 5 initial des offres avec titre, entreprise, source, URL, score, eligibilite de localisation, points forts, ecarts et prochaine action recommandee.
- AC5: Le MVP documente clairement les limites d'integration avec LinkedIn, Welcome to the Jungle et Indeed, et isole les connecteurs pour pouvoir les remplacer.
- AC6: La generation automatique de CV et lettre de motivation est hors MVP, mais les donnees stockees conservent les elements necessaires pour cette phase.

# Definition of Ready (DoR)
- [x] Problem statement is explicit and user impact is clear.
- [x] Scope boundaries (in/out) are explicit.
- [x] Acceptance criteria are testable.
- [x] Dependencies and known risks are listed.

# Companion docs
- Product brief(s): `prod_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi`
- Architecture decision(s): `adr_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi`

# References
- Product brief: `logics/product/prod_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi.md`
- Architecture decision: `logics/architecture/adr_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi.md`
- Backlog slice: `logics/backlog/item_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi.md`

# AI Context
- Summary: MVP local pour collecter des offres d'emploi, dedupliquer les annonces vues, scorer les nouvelles offres contre un profil utilisateur et proposer un top exploitable.
- Keywords: job-search, local-cli, sqlite, scoring, deduplication, linkedin, welcome-to-the-jungle, indeed, profile-match
- Use when: You need context for the first implementation slice of the job-offer review assistant.
- Skip when: The work concerns later CV or cover-letter generation without touching ingestion, storage, or scoring.

# Backlog
- none
- `item_001_mvp_outil_local_de_veille_et_scoring_d_offres_d_emploi`

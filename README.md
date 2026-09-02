# My English Vocabulary Training

Application web de révision de vocabulaire anglais — développée en Python/Flask et couverte par une stratégie de test complète.

---

## L'application

Application Flask permettant à un utilisateur de :

- Créer un compte, se connecter, gérer son profil
- Ajouter et supprimer des mots anglais avec leur traduction
- Consulter la liste complète de ses mots (recherche, lien définition Larousse)
- Marquer des mots comme "maîtrisés" pour les exclure des révisions
- S'entraîner en mode continu ou 10 vies, en anglais→français, français→anglais ou mixte
- Consulter ses statistiques (mots maîtrisés, taux de réussite)
- Panel administrateur (gestion des utilisateurs, rôles)

**Stack technique :** Python · Flask · SQLite · HTML/CSS/JavaScript

---

## Stratégie de test

Ce projet couvre l'ensemble du cycle de test : gestion, manuel, API, UI automatisé, performance et base de données.

---

## Outils utilisés

### Jira — Gestion de projet Agile

- Création d'un projet Jira en méthode Agile (Scrum)
- 5 Epics couvrant les fonctionnalités principales
- 17 User Stories avec critères d'acceptation détaillés
- Tickets Bug avec reproduction, impact et correction documentés
- 1 Sprint organisé avec priorisation des tickets

**Captures :** `JIRA/`

---

### Xray — Gestion des tests

- Configuration des types de tickets Xray (Test, Test Plan, Test Execution)
- 48 Test Cases rédigés à partir des critères d'acceptation des User Stories
- Scénarios en format Gherkin (Given / When / Then)
- Exécution manuelle des 48 tests — 48 Passed
- 1 Test Plan regroupant l'ensemble des 48 cas de test
- 1 Test Execution avec statut final de chaque test
- Rapport de traçabilité et rapport de couverture générés

**Captures :** `X-RAY/`

---

### Postman — Tests API

Collection de 5 requêtes testant les endpoints REST de l'application :

| Requête | Méthode | Endpoint | Assertion |
|---|---|---|---|
| Connexion | POST | `/login` | Status 200 |
| Liste des mots | GET | `/api/words` | Status 200, réponse tableau JSON |
| Ajouter un mot | POST | `/api/words` | Status 201, mot anglais correct |
| Marquer maîtrisé | PATCH | `/api/words/:id` | Status 200 |
| Supprimer un mot | DELETE | `/api/words/:id` | Status 200 |

- Environnement configuré avec variable `base_url`
- Scripts de test (Post-response) sur statut et structure JSON

**Captures :** `POSTMAN/`

---

### SQL — Vérification base de données

Base SQLite (`vocabulary.db`) avec 2 tables : `users` et `words`.

8 requêtes de vérification rédigées dans `sql_queries.sql` :

- Afficher tous les utilisateurs
- Filtrer par rôle (admin)
- Afficher les mots maîtrisés
- Compter le nombre total de mots
- Jointure users/words pour afficher les mots par utilisateur
- Filtrer les mots non maîtrisés avec le pseudo associé

**Fichier :** `sql_queries.sql` · **Captures :** `SQL/`

---

### Playwright + pytest — Tests E2E automatisés

10 tests end-to-end organisés selon le pattern **Page Object Model**.

**Architecture :**

```
pages/
├── login_page.py
├── register_page.py
├── add_page.py
├── list_page.py
└── training_page.py

tests/
├── test_auth.py       (4 tests)
├── test_add.py        (2 tests)
├── test_list.py       (3 tests)
└── test_training.py   (1 test)

conftest.py            (fixtures partagées)
```

**Fixtures pytest :**
- `login_in_page` — session connectée réutilisable
- `new_word` — création + nettoyage automatique en base (yield/teardown)
- `new_user` — création + nettoyage automatique en base

**Tests couverts :**

| Fichier | Test | Description |
|---|---|---|
| test_auth | `test_connexion` | Connexion avec identifiants valides |
| test_auth | `test_connexion_password_wrong` | Connexion avec mauvais mot de passe |
| test_auth | `test_register_succes` | Inscription avec données valides |
| test_auth | `test_register_with_wrong_confirm` | Inscription avec confirmation incorrecte |
| test_add | `test_add_word` | Ajout d'un mot et vérification du message de succès |
| test_add | `test_delete_word` | Suppression d'un mot via modal de confirmation |
| test_list | `test_search_word` | Recherche d'un mot dans la liste |
| test_list | `test_toggle_mastered` | Cochage d'un mot comme maîtrisé |
| test_list | `test_definition_link` | Vérification du lien vers Larousse |
| test_training | `test_start_training` | Lancement d'une session de training |

**Résultat : 10/10 passed**

**Rapport HTML généré avec pytest-html :** `PLAYWRIGHT/`

Pour lancer les tests :

```bash
cd my-english-vocabulary-training
pytest --headed
```

Pour générer le rapport HTML :

```bash
pytest --html=report.html --self-contained-html
```

---

## CI/CD — GitHub Actions

Un workflow automatique se déclenche à chaque `push` sur `main` :

1. Installation de Python et des dépendances
2. Installation du navigateur Chromium (Playwright)
3. Lancement du serveur Flask en arrière-plan
4. Exécution des 10 tests
5. Sauvegarde du rapport HTML en artifact

**Fichier :** `.github/workflows/tests.yml`

---

### Évolution de `conftest.py` — de local à CI/CD

**Version initiale** (fonctionnelle en local) :

```python
import pytest
import sqlite3
from playwright.sync_api import Page

BASE_URL = "http://127.0.0.1:5002"

@pytest.fixture
def app_url():
    return BASE_URL

@pytest.fixture
def login_in_page(page: Page, app_url):
    page.goto(f"{app_url}/login")
    page.locator("#username").fill("testuser")
    page.locator("#password").fill("test1234!")
    page.get_by_role("button", name="🔑 Se connecter").click()
    return page

@pytest.fixture
def new_user():
    username = "test_register"
    yield username
    conn = sqlite3.connect("app/vocabulary.db")
    conn.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

@pytest.fixture
def new_word():
    word = "testword"
    yield word
    conn = sqlite3.connect("app/vocabulary.db")
    conn.execute("DELETE FROM words WHERE english = ?", (word,))
    conn.commit()
    conn.close()
```

**Problème découvert en CI** : en local, `testuser` existait déjà dans la base. En CI, la base démarre vide — aucun utilisateur. Le fixture `login_in_page` essayait de se connecter avec un compte inexistant.

**Version finale** (compatible CI/CD — améliorée avec aide IA pour la partie `create_test_user`) :

```python
import pytest
import sqlite3
import time
import requests
from playwright.sync_api import Page

BASE_URL = "http://127.0.0.1:5002"

@pytest.fixture(scope="session", autouse=True)
def create_test_user():
    """Crée testuser avant les tests — indispensable en CI où la DB démarre vide."""
    for _ in range(10):
        try:
            requests.post(
                f"{BASE_URL}/register",
                data={
                    "username": "testuser",
                    "email": "testuser@ci.local",
                    "password": "test1234!",
                    "confirm": "test1234!",
                },
                timeout=5,
            )
            break
        except requests.exceptions.ConnectionError:
            time.sleep(2)
```

**Ce qui a changé et pourquoi :**

| Ajout | Raison |
|---|---|
| `scope="session"` | S'exécute une seule fois pour toute la session, pas à chaque test |
| `autouse=True` | Démarre automatiquement sans l'ajouter dans chaque test |
| `requests.post("/register")` | Crée `testuser` via l'API avant que les tests en aient besoin |
| Boucle `for _ in range(10)` | Attend que Flask soit prêt si le serveur démarre lentement en CI |

---

## Déploiement

L'application est déployée sur **PythonAnywhere** :

🔗 [https://choukri.pythonanywhere.com](https://choukri.pythonanywhere.com)

> L'application utilise SQLite avec stockage persistant. Les données sont conservées entre les sessions.

---

### JMeter — Tests de performance

Test de charge simulant 10 utilisateurs simultanés avec ramp-up de 5 secondes et 3 répétitions (90 requêtes au total).

**Endpoints testés :**

| Requête | Chemin | Temps moyen | Erreurs |
|---|---|---|---|
| GET - Liste des mots | `/api/words` | 3 ms | 0% |
| GET - Page liste | `/list` | 2 ms | 0% |
| GET - Page training | `/training` | 1 ms | 0% |

**Résultat : 0% d'erreur · Temps de réponse max 8ms**

**Fichier plan de test :** `jmeter-test-plan.jmx` · **Captures :** `JMETER/`

---

## Structure du projet

```
my-english-vocabulary-training/
├── .github/
│   └── workflows/
│       └── tests.yml   # CI/CD GitHub Actions
├── app/
│   ├── server.py
│   ├── templates/
│   ├── static/
│   └── vocabulary.db
├── pages/              # Page Objects Playwright
├── tests/              # Tests E2E pytest
├── PLAYWRIGHT/         # Rapport pytest-html
├── JIRA/               # Captures Jira
├── X-RAY/              # Captures Xray
├── POSTMAN/            # Captures Postman
├── SQL/                # Captures DB Browser
├── JMETER/             # Captures JMeter
├── conftest.py
├── sql_queries.sql
├── jmeter-test-plan.jmx
└── README.md
```

---

## Compétences démontrées

- Rédaction de cas de test à partir de critères d'acceptation
- Gestion de projet Agile avec Jira (Epics, Stories, Bugs, Sprint)
- Test management avec Xray (traçabilité, couverture, rapports)
- Tests API REST avec Postman (assertions, scripts, variables d'environnement)
- Vérification de données en SQL (SELECT, WHERE, JOIN, COUNT, GROUP BY)
- Automatisation E2E avec Playwright Python et pytest
- Pattern Page Object Model et fixtures avec teardown
- Tests de performance avec JMeter (Thread Group, Listeners, métriques)
- Identification et documentation de bugs (reproduction, impact, correction)
- Utilisation de l'IA (Cursor / Claude) comme outil de travail — débogage assisté, explication de concepts, génération de code commentée et comprise

---

## Utilisation de l'IA dans ce projet

Certaines parties de ce projet ont été réalisées avec l'aide d'un assistant IA (Cursor / Claude), utilisé comme un **Tech Lead virtuel** : explication des concepts, suggestion de structure, débogage des erreurs Playwright, configuration du CI/CD.

Cette approche reflète la réalité du travail en équipe : un junior s'appuie sur les plus expérimentés pour monter en compétence, comprendre les décisions techniques et débloquer les situations complexes. L'objectif n'était pas de déléguer, mais d'apprendre — chaque ligne de code a été lue, comprise et validée.

Maîtriser les outils IA disponibles (GitHub Copilot, Cursor, ChatGPT) fait partie des compétences attendues d'un QA en 2026.

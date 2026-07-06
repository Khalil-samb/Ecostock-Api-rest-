# Eco-Stock API

API REST développée avec **Django** et **Django REST Framework (DRF)** permettant de gérer un réseau d'entrepôts (`Warehouse`) et les produits alimentaires (`Product`) qui y sont stockés. L'API inclut l'authentification par **JWT**, une documentation interactive **Swagger/Redoc** générée automatiquement, ainsi que des règles métier spécifiques (gestion de la péremption, transfert de produits).

---

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Stack technique](#stack-technique)
- [Installation](#installation)
- [Configuration](#configuration)
- [Authentification](#authentification)
- [Modèles de données](#modèles-de-données)
- [Endpoints de l'API](#endpoints-de-lapi)
- [Règles métier](#règles-métier)
- [Documentation interactive](#documentation-interactive)
- [Exemples de requêtes](#exemples-de-requêtes)

---

## Fonctionnalités

- CRUD complet sur les entrepôts (`Warehouse`)
- CRUD complet sur les produits (`Product`)
- Action `audit` : statistiques détaillées sur un entrepôt (quantité totale, répartition par statut, etc.)
- Action `move` : transfert d'un produit vers un autre entrepôt, avec blocage si le produit est périmé
- Synchronisation automatique du statut d'un produit (`disponible` → `perime`) selon sa date de péremption
- Authentification par token JWT (access + refresh)
- Documentation OpenAPI générée automatiquement (Swagger UI et Redoc)

---

## Stack technique

| Composant            | Technologie                          |
|-----------------------|---------------------------------------|
| Langage               | Python                                 |
| Framework web         | Django 6.0.6                           |
| API                   | Django REST Framework (DRF)            |
| Authentification      | rest_framework_simplejwt (JWT)         |
| Documentation API     | drf-spectacular (OpenAPI/Swagger/Redoc)|
| Base de données       | SQLite (par défaut, développement)     |

---

## Installation

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd <nom-du-projet>
```

### 2. Créer et activer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate      # Linux / Mac
venv\Scripts\activate         # Windows
```

### 3. Installer les dépendances

```bash
pip install django djangorestframework djangorestframework-simplejwt drf-spectacular
```

> Si un fichier `requirements.txt` existe dans le projet, préférez plutôt :
> ```bash
> pip install -r requirements.txt
> ```

### 4. Appliquer les migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Créer un superutilisateur (optionnel, pour l'admin Django)

```bash
python manage.py createsuperuser
```

### 6. Lancer le serveur de développement

```bash
python manage.py runserver
```

L'API est alors disponible sur `http://127.0.0.1:8000/`.

---

## Configuration

### Applications installées

Le projet repose sur les apps suivantes (`INSTALLED_APPS`) :

- `rest_framework` — Django REST Framework
- `rest_framework_simplejwt` — Authentification JWT
- `drf_spectacular` — Génération de la documentation OpenAPI
- `inventory` — Application métier (modèles `Warehouse` et `Product`)

### Base de données

Par défaut, le projet utilise **SQLite** (`db.sqlite3`), adapté au développement. Pour la production, il est recommandé de migrer vers PostgreSQL ou un autre SGBD robuste.

### Permissions par défaut

```python
"DEFAULT_PERMISSION_CLASSES": (
    "rest_framework.permissions.IsAuthenticatedOrReadOnly",
)
```

Cela signifie que :
- **Lecture (GET)** : accessible à tous, authentifié ou non.
- **Écriture (POST, PUT, PATCH, DELETE)** : réservée aux utilisateurs authentifiés.

### JWT

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
}
```

- Le token d'accès (`access`) est valide **1 heure**.
- Le token de rafraîchissement (`refresh`) est valide **1 jour**.
- Les refresh tokens ne sont pas régénérés à chaque utilisation (`ROTATE_REFRESH_TOKENS: False`).

---

## Authentification

L'API utilise l'authentification JWT via `rest_framework_simplejwt`.

### Obtenir un token

```
POST /api/token/
```

**Body :**
```json
{
  "username": "khalil",
  "password": "passer123"
}
```

**Réponse :**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Rafraîchir un token

```
POST /api/token/refresh/
```

**Body :**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Utiliser le token

Ajoutez le header suivant à chaque requête nécessitant une authentification :

```
Authorization: Bearer <access_token>
```

---

## Modèles de données

### `Warehouse` (Entrepôt)

| Champ      | Type                  | Description                                      |
|------------|-----------------------|---------------------------------------------------|
| `name`     | CharField (255)        | Nom de l'entrepôt                                  |
| `location` | CharField (255)        | Localisation de l'entrepôt                         |
| `capacity` | PositiveIntegerField   | Capacité maximale (nombre d'unités stockables)     |

Relation : un `Warehouse` peut contenir **plusieurs** `Product` (relation 1-N, accessible via `warehouse.products.all()`).

### `Product` (Produit)

| Champ             | Type               | Description                                             |
|-------------------|--------------------|----------------------------------------------------------|
| `name`            | CharField (255)     | Nom du produit                                            |
| `quantity`        | PositiveIntegerField| Quantité en stock                                         |
| `expiration_date` | DateField           | Date de péremption                                        |
| `status`          | CharField (choix)   | Statut du produit : `disponible`, `reserve`, `perime`     |
| `warehouse`       | ForeignKey          | Entrepôt de rattachement (`on_delete=CASCADE`)             |

**Propriété calculée :**
- `is_expired` (bool) : `True` si `expiration_date` est antérieure à la date du jour.

**Comportement automatique (`save()`) :**
À chaque sauvegarde, si le produit est détecté comme périmé (`is_expired == True`), son `status` est automatiquement forcé à `perime`, indépendamment de la valeur envoyée par le client.

**Choix de statut (`Status`) :**

| Valeur stockée | Libellé    |
|----------------|------------|
| `disponible`   | Disponible |
| `reserve`      | Réservé    |
| `perime`       | Périmé     |

---

## Endpoints de l'API

Toutes les routes sont préfixées par `/api/` et générées automatiquement via un `DefaultRouter` de DRF.

### Entrepôts — `/api/warehouses/`

| Méthode | URL                          | Description                          | Auth requise |
|---------|------------------------------|---------------------------------------|--------------|
| GET     | `/api/warehouses/`            | Liste tous les entrepôts               | Non          |
| POST    | `/api/warehouses/`            | Crée un entrepôt                       | Oui          |
| GET     | `/api/warehouses/{id}/`       | Détail d'un entrepôt (+ ses produits)  | Non          |
| PUT     | `/api/warehouses/{id}/`       | Met à jour un entrepôt (complet)       | Oui          |
| PATCH   | `/api/warehouses/{id}/`       | Met à jour un entrepôt (partiel)       | Oui          |
| DELETE  | `/api/warehouses/{id}/`       | Supprime un entrepôt                   | Oui          |
| GET     | `/api/warehouses/{id}/audit/` | Statistiques d'audit de l'entrepôt     | Non          |

#### Détail — `GET /api/warehouses/{id}/audit/`

Retourne des statistiques détaillées sur un entrepôt donné :

```json
{
  "warehouse": "Entrepôt Nord",
  "capacity": 5000,
  "total_products": 12,
  "total_quantity": 3400,
  "by_status": {
    "disponible": 8,
    "reserve": 2,
    "perime": 2
  }
}
```

### Produits — `/api/products/`

| Méthode | URL                        | Description                           | Auth requise |
|---------|-----------------------------|-----------------------------------------|--------------|
| GET     | `/api/products/`             | Liste tous les produits                  | Non          |
| POST    | `/api/products/`             | Crée un produit                          | Oui          |
| GET     | `/api/products/{id}/`        | Détail d'un produit                      | Non          |
| PUT     | `/api/products/{id}/`        | Met à jour un produit (complet)          | Oui          |
| PATCH   | `/api/products/{id}/`        | Met à jour un produit (partiel)          | Oui          |
| DELETE  | `/api/products/{id}/`        | Supprime un produit                      | Oui          |
| POST    | `/api/products/{id}/move/`   | Transfère un produit vers un autre entrepôt | Oui       |

#### Détail — `POST /api/products/{id}/move/`

**Body attendu :**
```json
{
  "warehouse_id": 3
}
```

**Réponse en cas de succès (200) :** l'objet `Product` mis à jour (nouveau `warehouse`).

**Réponse en cas d'échec (400) — produit périmé :**
```json
{
  "error": "Impossible de transférer un produit périmé."
}
```

**Réponse en cas d'échec (400) — entrepôt inexistant :**
```json
{
  "warehouse_id": ["Cet entrepôt n'existe pas."]
}
```

### Authentification — `/api/token/`

| Méthode | URL                     | Description                     |
|---------|--------------------------|-----------------------------------|
| POST    | `/api/token/`             | Obtenir un access + refresh token |
| POST    | `/api/token/refresh/`     | Rafraîchir un access token         |

### Administration Django

| URL       | Description                     |
|-----------|-----------------------------------|
| `/admin/` | Interface d'administration Django |

---

## Règles métier

1. **Péremption automatique** : à chaque sauvegarde d'un produit, si `expiration_date` est dépassée, le `status` est automatiquement mis à `perime`, quelle que soit la valeur envoyée par le client.
2. **Blocage de transfert** : un produit dont le statut est `perime` (ou dont `is_expired` est vrai) **ne peut pas** être déplacé vers un autre entrepôt. La tentative renvoie une erreur `400 Bad Request`.
3. **Validation de l'entrepôt cible** : lors d'un transfert (`move`), l'identifiant `warehouse_id` fourni doit correspondre à un entrepôt existant, sinon une erreur de validation est renvoyée.
4. **Lecture publique / écriture protégée** : toute personne peut consulter les entrepôts et produits (GET), mais seule une personne authentifiée (JWT) peut créer, modifier ou supprimer des ressources.

---

## Documentation interactive

Le projet utilise **drf-spectacular** pour générer une documentation OpenAPI accessible via :

| URL                          | Description                          |
|-------------------------------|-----------------------------------------|
| `/api/schema/`                 | Schéma OpenAPI brut (JSON/YAML)         |
| `/api/schema/swagger-ui/`      | Interface interactive Swagger UI         |
| `/api/schema/redoc/`           | Interface interactive Redoc              |

---

## Exemples de requêtes

### Créer un entrepôt

```bash
curl -X POST http://127.0.0.1:8000/api/warehouses/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Entrepôt Nord", "location": "Dakar", "capacity": 5000}'
```

### Créer un produit

```bash
curl -X POST http://127.0.0.1:8000/api/products/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Riz", "quantity": 200, "expiration_date": "2026-12-31", "warehouse": 1}'
```

### Consulter l'audit d'un entrepôt

```bash
curl http://127.0.0.1:8000/api/warehouses/1/audit/
```

### Transférer un produit

```bash
curl -X POST http://127.0.0.1:8000/api/products/5/move/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"warehouse_id": 2}'
```

---

## Structure du projet (résumé)

```
config/                  # Configuration Django (settings, urls racine)
├── settings.py
├── urls.py

inventory/                # Application métier
├── models.py             # Modèles Warehouse et Product
├── serializers.py        # Serializers DRF
├── views.py              # ViewSets et actions personnalisées
├── urls.py                # Routes de l'app (via DefaultRouter)
```

---

## Notes de développement

- `DEBUG = True` et `SECRET_KEY` en clair dans `settings.py` : à modifier impérativement avant tout déploiement en production (variables d'environnement, `DEBUG = False`, `ALLOWED_HOSTS` configuré).
- La base de données SQLite convient au développement mais n'est pas recommandée en production à fort trafic.
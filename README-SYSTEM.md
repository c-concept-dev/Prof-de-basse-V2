# 🎸 Prof de Basse V2 - Documentation Système

## 📊 État Actuel du Système

**Date de dernière vérification** : 11 novembre 2025

### ✅ Statut Global
- **Système** : ✅ Opérationnel
- **Synchronisation Git** : ✅ Complète
- **URLs** : ✅ 100% correctes (Prof-de-basse-V2)
- **Index de recherche** : ✅ 1531 ressources

---

## 🗂️ Architecture du Système

```
Prof-de-basse-V2/
├── 📁 Methodes/
│   ├── 70 Funk & Disco bass MP3/    (99 tracks)
│   ├── John Liebman Funk Fusion/
│   └── Paul westwood MP3/
│
├── 📁 Base de connaissances/
│   ├── Methodes/
│   ├── Partitions/
│   └── Theorie/
│
├── 📁 resources/
│   └── complete-resource-map.json
│
├── 📁 .github/
│   ├── workflows/                    (GitHub Actions)
│   └── scripts/
│       └── auto-index-generator.py
│
├── 📄 mega-search-index.json         (1531 ressources)
├── 📄 assets_ocr_index.json
└── 🔧 Scripts de maintenance
    ├── verify-prof-basse.py          (vérification système)
    ├── test-mp3-access.py            (test accessibilité MP3)
    ├── fix-urls.py                   (correction URLs)
    ├── fix-repo-paths.py             (correction chemins)
    └── fusion-all-indexes.py         (fusion indexes)
```

---

## 🔍 Indexes et Ressources

### Mega-search-index.json
**Fonction** : Index unifié de toutes les ressources  
**Contenu** : 1531 ressources  
**Distribution** :
- Images (OCR) : 1525 (99.6%)
- Autres : 6 (0.4%)

**Sources** :
- `assets_ocr_index.json` : 786 ressources (50%)
- `songs_index.json` : 739 ressources (48%)
- `complete-resource-map.json` : 6 ressources (2%)

### Complete-resource-map.json
**Fonction** : Cartographie des méthodes MP3 et PDF  
**Status** : En développement  
**Emplacement** : `resources/complete-resource-map.json`

---

## 🎵 Ressources MP3

### 70s Funk & Disco Bass
- **Tracks** : 99 fichiers (Track 01 à Track 99)
- **Format** : "Track XX.mp3" (espace + 2 chiffres)
- **URL base** : `https://11drumboy11.github.io/Prof-de-basse-V2/Methodes/70%20Funk%20&%20Disco%20bass%20MP3/`
- **Encodage** : Espaces = `%20`, & = non encodé

**Exemple d'URLs** :
```
https://11drumboy11.github.io/Prof-de-basse-V2/Methodes/70%20Funk%20&%20Disco%20bass%20MP3/Track%2001.mp3
https://11drumboy11.github.io/Prof-de-basse-V2/Methodes/70%20Funk%20&%20Disco%20bass%20MP3/Track%2045.mp3
```

### Organisation par niveau
| Tracks | Style | Niveau |
|--------|-------|--------|
| 01-15 | Funk de base | Débutant |
| 16-30 | Ghost notes | Intermédiaire |
| 21-40 | Slap intro | Intermédiaire |
| 61-80 | Disco grooves | Avancé |
| 81-99 | Slap avancé | Avancé |

---

## 🤖 Automatisation

### GitHub Actions
**Workflows actifs** :
- ✅ Auto-update OCR (scan assets + génération index)
- ✅ Auto-update index complet (fusion tous les indexes)

**Déclenchement** :
- Push sur `main` (sauf si `[skip ci]`)
- Ajout/modification de fichiers dans `Base de connaissances/`

### Scripts d'indexation
- `auto-index-generator.py` : Génère les indexes OCR
- `fusion-all-indexes.py` : Fusionne tous les indexes
- `convert-ocr-index.py` : Convertit le format OCR

---

## 🔧 Maintenance

### Scripts de vérification

#### verify-prof-basse.py
**Usage** : `python3 verify-prof-basse.py`  
**Fonction** : Vérifie l'intégrité du système  
**Vérifie** :
- Validité JSON des indexes
- URLs (V2 vs ancien repo)
- Statistiques des ressources
- État général du système

#### test-mp3-access.py
**Usage** : `python3 test-mp3-access.py`  
**Fonction** : Teste l'accessibilité des MP3  
**Teste** :
- Échantillon de 6 tracks MP3
- mega-search-index.json
- Taille des fichiers

### Scripts de correction

#### fix-urls.py
**Usage** : `python3 fix-urls.py`  
**Fonction** : Corrige les URLs pointant vers l'ancien repo

#### fix-repo-paths.py
**Usage** : `python3 fix-repo-paths.py`  
**Fonction** : Corrige tous les chemins dans le repo

---

## 📈 Workflow de Développement

### 1. Ajout de nouvelles ressources

```bash
# 1. Ajouter fichiers dans Base de connaissances/
cp nouvelles_ressources/* Base\ de\ connaissances/Methodes/

# 2. Commit et push
git add .
git commit -m "Add: Nouvelles ressources [méthode X]"
git push origin main

# 3. GitHub Actions s'exécute automatiquement
# → OCR scan
# → Génération indexes
# → Fusion dans mega-search-index.json
```

### 2. Vérification système

```bash
# Après tout changement majeur
python3 verify-prof-basse.py

# Test accessibilité MP3
python3 test-mp3-access.py
```

### 3. Correction URLs (si nécessaire)

```bash
# Si verify-prof-basse.py détecte des URLs obsolètes
python3 fix-urls.py

# Commit
git add .
git commit -m "Fix: URLs vers V2"
git push origin main
```

---

## 🌐 GitHub Pages

### Configuration
- **Repo** : github.com/11drumboy11/Prof-de-basse-V2
- **Branche** : `main`
- **URL** : https://11drumboy11.github.io/Prof-de-basse-V2/

### Endpoints principaux
```
https://11drumboy11.github.io/Prof-de-basse-V2/mega-search-index.json
https://11drumboy11.github.io/Prof-de-basse-V2/resources/complete-resource-map.json
https://11drumboy11.github.io/Prof-de-basse-V2/Methodes/[méthode]/[fichier]
```

---

## 🔐 Sécurité et Conventions

### Commits
- Messages en français
- Format : `Type: Description`
- Types : Add, Fix, Update, Merge, Delete
- `[skip ci]` pour éviter l'exécution des workflows

### Branches
- **main** : Production (GitHub Pages)
- **feature/** : Développement de nouvelles fonctionnalités
- **fix/** : Corrections de bugs

---

## 📊 Métriques Actuelles

| Métrique | Valeur |
|----------|--------|
| Total ressources indexées | 1531 |
| Fichiers MP3 (70s Funk) | 99 |
| Images OCR | 1525 |
| URLs V2 correctes | 100% |
| Méthodes PDF indexées | Multiple |
| Real Books disponibles | Jazz, Funk/Soul, Rock |

---

## 🚀 Roadmap

### Court terme
- [ ] Tester accessibilité complète des MP3
- [ ] Enrichir complete-resource-map.json
- [ ] Documenter toutes les méthodes MP3

### Moyen terme
- [ ] Interface de recherche web
- [ ] Dashboard de monitoring
- [ ] API REST pour accès programmatique

### Long terme
- [ ] Système de recommendation
- [ ] Analytics d'utilisation
- [ ] Intégration avec plateformes d'apprentissage

---

## 📞 Support

**Vérification système** : `python3 verify-prof-basse.py`  
**Documentation** : Ce fichier (README-SYSTEM.md)  
**GitHub** : https://github.com/11drumboy11/Prof-de-basse-V2

---

**Dernière mise à jour** : 11 novembre 2025  
**Version système** : 1.0.0  
**Status** : ✅ Opérationnel

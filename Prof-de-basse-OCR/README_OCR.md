# 🔍 OCR System v2 - Prof de Basse

## 🚀 Démarrage Rapide

### Installation (5 minutes)

```bash
# 1. Installer Tesseract
sudo apt-get install tesseract-ocr tesseract-ocr-fra

# 2. Installer dépendances Python
pip install Pillow pytesseract

# 3. Configurer scripts
# Dans chaque script (.py), modifier :
REPO_PATH = "/path/to/Prof-de-basse"  # Ton chemin local
```

### Utilisation

#### Première fois (scan complet)

```bash
# 1. Tester qualité OCR (5-10 fichiers)
python test_ocr_quality.py

# 2. Si qualité >75%, lancer scan complet
python ocr_scanner_v2.py

# Résultat : search_index_ocr.json créé
```

#### Après ajout nouveaux fichiers (scan incrémental)

```bash
python auto_update_index.py

# Résultat : search_index.json mis à jour
```

## 📊 Les 3 Scripts

| Script | Fonction | Durée | Quand |
|--------|----------|-------|-------|
| **test_ocr_quality.py** | Teste 5 fichiers/dossier | 2-5 min | Avant scan complet |
| **ocr_scanner_v2.py** | Scanne TOUT | 10-30 min | Première fois |
| **auto_update_index.py** | Scan incrémental | 1-5 min | Maintenance |

## ✅ Ce qui est détecté

- ✅ **Titre** (exercice, morceau)
- ✅ **Compositeur** (Miles Davis, Stevie Wonder...)
- ✅ **Techniques** (walking, slap, ghost notes, fingerstyle...)
- ✅ **Tonalité** (C, Dm, F#...)
- ✅ **Tempo** (BPM)
- ✅ **Page/Track** (numéro)

## 📈 Checklist Qualité

Avant de dire "OCR au top" :

- [ ] `test_ocr_quality.py` → Qualité >75%
- [ ] `ocr_scanner_v2.py` → search_index_ocr.json créé
- [ ] Détection titres : >80%
- [ ] Détection compositeurs : >70%
- [ ] Détection techniques : >60%
- [ ] JSON contient 200+ ressources

## 🎯 Exemple Sortie JSON

```json
[
  {
    "file": "Partitions/Jazz/so_what.png",
    "filename": "so_what.png",
    "title": "So What",
    "composer": "Miles Davis",
    "techniques": ["walking"],
    "key": "D",
    "tempo": 132,
    "page_track": 47,
    "directory": "Partitions",
    "ocr_confidence": "high"
  }
]
```

## ⚙️ Améliorer Détection

### Si titres mal détectés

Modifier `TITLE_PATTERNS` dans `ocr_scanner_v2.py`

### Si compositeurs manquants

Ajouter dans `KNOWN_COMPOSERS`

### Si techniques manquantes

Ajouter patterns dans `TECHNIQUE_PATTERNS`

## ⚠️ Troubleshooting

**"tesseract not found"**
```bash
sudo apt-get install tesseract-ocr
```

**OCR extrait peu de texte**
- Images trop petites → resize automatique
- Fond sombre → améliorer preprocessing

**Script lent**
- Utiliser `auto_update_index.py` (incrémental)
- Ne scanner que nouveaux fichiers

## 📚 Documentation Complète

Voir `ocr-system-v2-documentation.html` pour :
- Détails techniques complets
- Paramètres configurables
- Patterns de détection
- Exemples avancés

## 🎸 Étape Suivante : Intégration GPT

Une fois `search_index.json` créé :

1. **Upload sur GitHub** (commit + push)
2. **GitHub Actions** pour auto-update
3. **GPT Function Calling** pour recherche instantanée
4. **Universal Resource Finder** opérationnel !

---

**Version** : 2.0.0  
**Dernière mise à jour** : 6 novembre 2025  
**Status** : ✅ Prêt pour production

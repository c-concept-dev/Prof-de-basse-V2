#!/bin/bash
# ============================================================================
# 🚀 INSTALLATION SYSTÈME OCR AUTOMATIQUE - Prof de Basse
# ============================================================================
# Script d'installation automatique du système OCR Assets Scanner
# Version: 1.0.0
# Date: 09/11/2025
# ============================================================================

set -e  # Arrêter en cas d'erreur

echo ""
echo "============================================================================"
echo "🎸 Prof de Basse - Installation Système OCR Automatique"
echo "============================================================================"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================================================
# ÉTAPE 1 : Vérifier qu'on est dans le bon dossier
# ============================================================================

echo -e "${BLUE}📍 ÉTAPE 1 : Vérification du répertoire...${NC}"
echo ""

CURRENT_DIR=$(pwd)
echo "Répertoire actuel : $CURRENT_DIR"

if [[ ! "$CURRENT_DIR" =~ "Prof-de-basse" ]]; then
    echo -e "${RED}❌ ERREUR : Tu n'es pas dans le dossier Prof-de-basse !${NC}"
    echo ""
    echo "Utilise cette commande pour aller dans le bon dossier :"
    echo "  cd /Users/christophebonnet/Documents/GitHub/Prof-de-basse"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Bon répertoire !${NC}"
echo ""

# ============================================================================
# ÉTAPE 2 : Vérifier les dépendances Python
# ============================================================================

echo -e "${BLUE}📦 ÉTAPE 2 : Vérification des dépendances Python...${NC}"
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 n'est pas installé !${NC}"
    exit 1
fi

echo "Python version : $(python3 --version)"

# Vérifier Tesseract
if ! command -v tesseract &> /dev/null; then
    echo -e "${YELLOW}⚠️  Tesseract OCR n'est pas installé${NC}"
    echo ""
    echo "Installation de Tesseract via Homebrew..."
    brew install tesseract
    echo -e "${GREEN}✅ Tesseract installé !${NC}"
else
    echo "Tesseract version : $(tesseract --version | head -n 1)"
fi

# Installer les bibliothèques Python
echo ""
echo "Installation des bibliothèques Python..."
pip3 install --break-system-packages Pillow pytesseract beautifulsoup4 lxml

echo -e "${GREEN}✅ Dépendances installées !${NC}"
echo ""

# ============================================================================
# ÉTAPE 3 : Copier les fichiers
# ============================================================================

echo -e "${BLUE}📋 ÉTAPE 3 : Copie des fichiers système...${NC}"
echo ""

# Fichiers à copier (tu dois les avoir téléchargés depuis Claude)
FILES=(
    "ocr-assets-scanner.py"
    "fusion-all-indexes-v3.py"
    "ocr-dashboard.html"
    "README-AUTO-OCR.md"
)

echo "Vérifie que tu as bien téléchargé ces fichiers depuis Claude :"
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✅${NC} $file"
    else
        echo -e "  ${RED}❌${NC} $file - MANQUANT !"
    fi
done

echo ""
read -p "Tous les fichiers sont présents ? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ Télécharge d'abord tous les fichiers depuis Claude !${NC}"
    exit 1
fi

# Copier fusion-all-indexes-v3.py → fusion-all-indexes.py
if [ -f "fusion-all-indexes-v3.py" ]; then
    cp fusion-all-indexes-v3.py fusion-all-indexes.py
    echo -e "${GREEN}✅${NC} fusion-all-indexes.py mis à jour"
fi

# Créer le dossier workflows s'il n'existe pas
mkdir -p .github/workflows

# Copier le workflow
if [ -f "auto-ocr-assets.yml" ]; then
    cp auto-ocr-assets.yml .github/workflows/
    echo -e "${GREEN}✅${NC} Workflow copié dans .github/workflows/"
fi

echo -e "${GREEN}✅ Fichiers copiés !${NC}"
echo ""

# ============================================================================
# ÉTAPE 4 : Test du système OCR en local
# ============================================================================

echo -e "${BLUE}🧪 ÉTAPE 4 : Test du système OCR...${NC}"
echo ""

read -p "Veux-tu lancer un scan OCR de test ? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Lancement du scan OCR..."
    python3 ocr-assets-scanner.py --repo . --output assets_ocr_index.json
    
    if [ -f "assets_ocr_index.json" ]; then
        echo -e "${GREEN}✅ assets_ocr_index.json créé !${NC}"
        
        # Afficher les stats
        python3 << EOF
import json
with open('assets_ocr_index.json', 'r') as f:
    data = json.load(f)
    print(f"\n📊 Statistiques :")
    print(f"   Total scannées : {data.get('total_scanned', 0)}")
    print(f"   Nouveaux scans : {data.get('new_scans', 0)}")
EOF
    else
        echo -e "${RED}❌ Erreur lors de la création de l'index OCR${NC}"
    fi
fi

echo ""

# ============================================================================
# ÉTAPE 5 : Fusion des index
# ============================================================================

echo -e "${BLUE}🔄 ÉTAPE 5 : Fusion des index...${NC}"
echo ""

if [ -f "assets_ocr_index.json" ]; then
    echo "Fusion de tous les index..."
    python3 fusion-all-indexes.py --repo . --output mega-search-index.json
    
    if [ -f "mega-search-index.json" ]; then
        echo -e "${GREEN}✅ mega-search-index.json créé !${NC}"
        
        # Afficher les stats
        python3 << EOF
import json
with open('mega-search-index.json', 'r') as f:
    data = json.load(f)
    print(f"\n📊 Statistiques :")
    print(f"   Total ressources : {data.get('total_resources', 0)}")
    print(f"   Avec OCR : {data.get('statistics', {}).get('with_ocr', 0)}")
EOF
    fi
fi

echo ""

# ============================================================================
# ÉTAPE 6 : Commit et Push
# ============================================================================

echo -e "${BLUE}💾 ÉTAPE 6 : Commit et Push vers GitHub...${NC}"
echo ""

echo "Fichiers à committer :"
git status --short

echo ""
read -p "Veux-tu committer et pusher les changements ? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Ajouter les fichiers
    git add ocr-assets-scanner.py
    git add fusion-all-indexes.py
    git add ocr-dashboard.html
    git add README-AUTO-OCR.md
    git add .github/workflows/auto-ocr-assets.yml
    
    # Si les index existent, les ajouter aussi
    [ -f "assets_ocr_index.json" ] && git add assets_ocr_index.json
    [ -f "mega-search-index.json" ] && git add mega-search-index.json
    
    # Commit
    git commit -m "🤖 Auto OCR System v1.0 - Scan automatique des images assets

- ✅ Script OCR pour extraction métadonnées (titre, compositeur, tonalité)
- ✅ Workflow GitHub Actions automatique
- ✅ Fusion intelligente avec mega-search-index
- ✅ Dashboard de monitoring
- ✅ Documentation complète"
    
    # Push
    echo ""
    echo "Push vers GitHub..."
    git push
    
    echo -e "${GREEN}✅ Changements pushés !${NC}"
else
    echo -e "${YELLOW}⚠️  Utilise GitHub Desktop pour committer manuellement${NC}"
fi

echo ""

# ============================================================================
# ÉTAPE 7 : Instructions finales
# ============================================================================

echo -e "${GREEN}============================================================================${NC}"
echo -e "${GREEN}✅ INSTALLATION TERMINÉE !${NC}"
echo -e "${GREEN}============================================================================${NC}"
echo ""

echo "📝 PROCHAINES ÉTAPES :"
echo ""
echo "1. 🔍 Vérifie le workflow sur GitHub :"
echo "   https://github.com/11drumboy11/Prof-de-basse-V2/actions"
echo ""
echo "2. ⏱️  Attends 5-10 minutes que le premier scan se termine"
echo ""
echo "3. 📥 Pull les changements dans GitHub Desktop pour récupérer :"
echo "   - assets_ocr_index.json (mis à jour)"
echo "   - mega-search-index.json (mis à jour)"
echo ""
echo "4. 📊 Ouvre le dashboard OCR :"
echo "   https://11drumboy11.github.io/Prof-de-basse-V2/ocr-dashboard.html"
echo ""
echo "5. 🔍 Teste la recherche avec les nouveaux titres :"
echo "   https://11drumboy11.github.io/Prof-de-basse-V2/"
echo ""
echo "============================================================================"
echo ""
echo "💡 TIPS :"
echo "  - Chaque upload d'image déclenche l'OCR automatiquement"
echo "  - Scan quotidien à 3h du matin (UTC)"
echo "  - Dashboard mis à jour toutes les 30 secondes"
echo ""
echo "📖 Documentation complète : README-AUTO-OCR.md"
echo ""
echo "🎸 Keep groovin'!"
echo ""

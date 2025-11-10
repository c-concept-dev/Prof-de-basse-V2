#!/bin/bash

# ============================================================================
# Setup Script - OCR System v2
# Prof de Basse - Installation et configuration automatique
# ============================================================================

echo "🎸 Prof de Basse - OCR System v2"
echo "=================================================="
echo "Script d'installation et configuration automatique"
echo ""

# ============================================================================
# Détection OS
# ============================================================================

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo "✅ OS détecté : Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
    echo "✅ OS détecté : macOS"
else
    echo "⚠️ OS non supporté : $OSTYPE"
    echo "Ce script supporte Linux et macOS uniquement"
    exit 1
fi

echo ""

# ============================================================================
# Installation Tesseract
# ============================================================================

echo "📦 Vérification Tesseract OCR..."

if command -v tesseract &> /dev/null; then
    TESSERACT_VERSION=$(tesseract --version | head -n 1)
    echo "✅ Tesseract déjà installé : $TESSERACT_VERSION"
else
    echo "⚠️ Tesseract non trouvé, installation..."
    
    if [ "$OS" == "linux" ]; then
        echo "   Installation via apt-get..."
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-fra
    elif [ "$OS" == "mac" ]; then
        echo "   Installation via Homebrew..."
        if ! command -v brew &> /dev/null; then
            echo "❌ Homebrew non installé"
            echo "   Installer Homebrew : /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
        brew install tesseract tesseract-lang
    fi
    
    # Vérification
    if command -v tesseract &> /dev/null; then
        echo "✅ Tesseract installé avec succès"
    else
        echo "❌ Échec installation Tesseract"
        exit 1
    fi
fi

echo ""

# ============================================================================
# Installation dépendances Python
# ============================================================================

echo "🐍 Installation dépendances Python..."

if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo "❌ pip non trouvé. Installer Python 3 et pip"
    exit 1
fi

echo "   Utilisation de : $PIP_CMD"

# Installer Pillow et pytesseract
$PIP_CMD install Pillow pytesseract --quiet

if [ $? -eq 0 ]; then
    echo "✅ Dépendances Python installées"
else
    echo "❌ Échec installation dépendances Python"
    exit 1
fi

echo ""

# ============================================================================
# Configuration REPO_PATH
# ============================================================================

echo "⚙️ Configuration REPO_PATH..."
echo ""
echo "Entrer le chemin COMPLET vers ton repository Prof-de-basse :"
echo "Exemple : /Users/toi/Documents/Prof-de-basse"
read -p "Chemin : " REPO_PATH

# Valider chemin
if [ ! -d "$REPO_PATH" ]; then
    echo "⚠️ Dossier non trouvé : $REPO_PATH"
    read -p "Créer le dossier ? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mkdir -p "$REPO_PATH"
        echo "✅ Dossier créé : $REPO_PATH"
    else
        echo "❌ Configuration annulée"
        exit 1
    fi
fi

echo "✅ REPO_PATH configuré : $REPO_PATH"
echo ""

# ============================================================================
# Modification scripts Python
# ============================================================================

echo "📝 Mise à jour des scripts Python..."

# Liste des scripts à modifier
SCRIPTS=("ocr_scanner_v2.py" "auto_update_index.py" "test_ocr_quality.py")

for SCRIPT in "${SCRIPTS[@]}"; do
    if [ -f "$SCRIPT" ]; then
        # Remplacer REPO_PATH
        sed -i.bak "s|REPO_PATH = \"/path/to/Prof-de-basse\"|REPO_PATH = \"$REPO_PATH\"|g" "$SCRIPT"
        
        if [ $? -eq 0 ]; then
            echo "   ✅ $SCRIPT configuré"
            rm "${SCRIPT}.bak"  # Supprimer backup
        else
            echo "   ⚠️ Erreur configuration $SCRIPT"
        fi
    else
        echo "   ⚠️ $SCRIPT non trouvé"
    fi
done

echo ""

# ============================================================================
# Création dossiers nécessaires
# ============================================================================

echo "📁 Création structure dossiers..."

REQUIRED_DIRS=(
    "$REPO_PATH/Methodes"
    "$REPO_PATH/Partitions"
    "$REPO_PATH/Real_Books"
    "$REPO_PATH/Exercises"
)

for DIR in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$DIR" ]; then
        mkdir -p "$DIR"
        echo "   ✅ Créé : $DIR"
    else
        echo "   ✓ Existe : $DIR"
    fi
done

echo ""

# ============================================================================
# Test rapide
# ============================================================================

echo "🧪 Test rapide du système..."
echo ""

# Créer fichier test simple
TEST_IMG="$REPO_PATH/test_image.png"

# Si ImageMagick disponible, créer image test
if command -v convert &> /dev/null; then
    convert -size 800x200 xc:white \
            -pointsize 30 -fill black \
            -gravity center -annotate +0+0 "Exercise 1 - Test OCR" \
            "$TEST_IMG" 2>/dev/null
    
    if [ -f "$TEST_IMG" ]; then
        echo "✅ Image test créée : $TEST_IMG"
        
        # Tester Tesseract
        TEST_TEXT=$(tesseract "$TEST_IMG" - 2>/dev/null)
        
        if [[ "$TEST_TEXT" == *"Exercise"* ]] || [[ "$TEST_TEXT" == *"Test"* ]]; then
            echo "✅ Test OCR réussi : Tesseract fonctionne !"
        else
            echo "⚠️ Test OCR : résultats imprévus"
            echo "   Texte détecté : $TEST_TEXT"
        fi
        
        # Nettoyer
        rm "$TEST_IMG"
    fi
else
    echo "ℹ️ ImageMagick non installé, skip test image"
    echo "   (optionnel, pas nécessaire pour OCR)"
fi

echo ""

# ============================================================================
# Résumé final
# ============================================================================

echo "=================================================="
echo "✅ INSTALLATION TERMINÉE"
echo "=================================================="
echo ""
echo "📊 Résumé :"
echo "   ✅ Tesseract OCR installé"
echo "   ✅ Dépendances Python installées"
echo "   ✅ REPO_PATH configuré : $REPO_PATH"
echo "   ✅ Scripts Python configurés"
echo "   ✅ Structure dossiers créée"
echo ""
echo "🚀 Prochaines étapes :"
echo ""
echo "1. Ajouter des fichiers images dans :"
echo "   - $REPO_PATH/Methodes/"
echo "   - $REPO_PATH/Partitions/"
echo "   - $REPO_PATH/Real_Books/"
echo ""
echo "2. Tester qualité OCR :"
echo "   python test_ocr_quality.py"
echo ""
echo "3. Si qualité >75%, lancer scan complet :"
echo "   python ocr_scanner_v2.py"
echo ""
echo "4. Pour mises à jour incrémentales :"
echo "   python auto_update_index.py"
echo ""
echo "📚 Documentation complète : ocr-system-v2-documentation.html"
echo "📖 Guide rapide : README_OCR.md"
echo ""
echo "🎸 Happy scanning!"
echo ""

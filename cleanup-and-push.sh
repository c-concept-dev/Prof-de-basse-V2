#!/bin/bash

# Script de nettoyage et mise à jour forcée
# Prof de Basse v2.0

echo "🧹 Nettoyage des anciens fichiers..."

# Supprimer les anciens JSON
rm -f mega-search-index.json
rm -f mega-search-index-v2.json
rm -f search-index-compatible.json
rm -f assets_ocr_index.json

echo "✅ Anciens fichiers supprimés"

# Vérifier que megasearch.json existe
if [ -f "megasearch.json" ]; then
    SIZE=$(du -h megasearch.json | cut -f1)
    echo "✅ megasearch.json présent ($SIZE)"
else
    echo "❌ megasearch.json ABSENT !"
    echo "   Lance: python3 update-site.py"
    exit 1
fi

# Commit et push
echo ""
echo "📤 Push sur GitHub..."
git add .
git commit -m "🧹 Nettoyage: suppression anciens index JSON + force rebuild"
git push origin main

echo ""
echo "✅ Terminé !"
echo ""
echo "⏰ Attends 2-3 minutes puis vérifie:"
echo "   https://11drumboy11.github.io/Prof-de-basse-V2/"

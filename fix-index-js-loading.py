#!/usr/bin/env python3
"""
Fix index.html JavaScript loading
Le problème : Le JS charge data.tree au lieu de data.resources
"""

import re

print("=" * 70)
print("🔧 CORRECTION JAVASCRIPT INDEX.HTML")
print("=" * 70)

# Lire index.html
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

original_content = content

# Corrections à appliquer
corrections = 0

# 1. Corriger le chargement des ressources (data.tree → data.resources)
if 'data.tree' in content:
    content = content.replace('data.tree', 'data.resources')
    corrections += 1
    print("✅ Correction 1 : data.tree → data.resources")

# 2. Vérifier qu'on utilise bien data.resources
if 'allResources = data.resources' not in content:
    # Chercher où allResources est assigné
    pattern = r'allResources\s*=\s*data\.\w+\s*\|\|\s*\[\]'
    if re.search(pattern, content):
        content = re.sub(
            pattern,
            'allResources = data.resources || []',
            content
        )
        corrections += 1
        print("✅ Correction 2 : allResources utilise data.resources")

# 3. S'assurer que les URLs sont bien utilisées
# Chercher les patterns où url pourrait être vide
patterns_to_fix = [
    (r'resource\.url\s*\|\|\s*resource\.page_url\s*\|\|\s*""', 
     'resource.url || resource.page_url || resource.file_path || ""'),
    (r'r\.url\s*\|\|\s*r\.page_url\s*\|\|\s*""',
     'r.url || r.page_url || r.file_path || ""'),
]

for old_pattern, new_pattern in patterns_to_fix:
    if re.search(old_pattern, content):
        content = re.sub(old_pattern, new_pattern, content)
        corrections += 1
        print(f"✅ Correction : Ajout fallback file_path")

# Sauvegarder si des corrections ont été faites
if corrections > 0:
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n💾 Fichier sauvegardé avec {corrections} correction(s)")
    
    # Montrer un extrait de ce qui a changé
    print("\n🔍 Vérification des changements:")
    
    # Chercher la ligne avec allResources
    for i, line in enumerate(content.split('\n')):
        if 'allResources = data.' in line:
            print(f"   Ligne {i+1}: {line.strip()}")
            break
else:
    print("\n⚠️  Aucune correction nécessaire")

print("\n" + "=" * 70)
print("✅ CORRECTION TERMINÉE")
print("=" * 70)
print("\n🔧 Commandes Git :")
print("   git add index.html")
print("   git commit -m 'Fix: Chargement correct data.resources dans index.html'")
print("   git push origin main")

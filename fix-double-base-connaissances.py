#!/usr/bin/env python3
"""
Retire le double "Base de connaissances" dans les URLs du mega-search-index.json
"""
import json
import re

def fix_double_path():
    print("="*70)
    print("🔧 CORRECTION DES URLS DOUBLÉES")
    print("="*70 + "\n")
    
    # Charger le fichier
    with open('mega-search-index.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    resources = data.get('resources', [])
    print(f"📊 Total ressources: {len(resources)}\n")
    
    # Patterns à corriger
    patterns = [
        (
            r'/Base%20de%20connaissances/Base%20de%20connaissances/',
            r'/Base%20de%20connaissances/'
        ),
        (
            r'/Base de connaissances/Base de connaissances/',
            r'/Base de connaissances/'
        )
    ]
    
    fixed_count = 0
    
    for resource in resources:
        url = resource.get('url', '')
        original_url = url
        
        # Appliquer les corrections
        for pattern, replacement in patterns:
            url = re.sub(pattern, replacement, url)
        
        # Si l'URL a changé, la mettre à jour
        if url != original_url:
            resource['url'] = url
            fixed_count += 1
    
    print(f"✅ URLs corrigées: {fixed_count}/{len(resources)}\n")
    
    # Montrer quelques exemples
    if fixed_count > 0:
        print("📝 Exemples de corrections:\n")
        count = 0
        for r in resources:
            if '/Base%20de%20connaissances/' in r.get('url', ''):
                if count < 3:
                    print(f"Titre: {r.get('title', 'N/A')[:50]}")
                    print(f"URL:   {r.get('url', 'N/A')[:100]}...")
                    print()
                    count += 1
                else:
                    break
    
    # Sauvegarder
    with open('mega-search-index.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("💾 Fichier sauvegardé!\n")
    
    # Vérifier qu'il n'y a plus de doublons
    remaining = sum(1 for r in resources if '/Base%20de%20connaissances/Base%20de%20connaissances/' in r.get('url', ''))
    
    if remaining == 0:
        print("="*70)
        print("✅ CORRECTION RÉUSSIE - Plus de doublons!")
        print("="*70)
    else:
        print(f"⚠️  {remaining} doublons restants")
    
    print()

if __name__ == '__main__':
    fix_double_path()

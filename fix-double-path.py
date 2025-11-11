#!/usr/bin/env python3
import json
import urllib.parse

BASE_URL = 'https://11drumboy11.github.io/Prof-de-basse-V2/'

with open('megasearch.json', 'r') as f:
    data = json.load(f)

print("🔧 Correction des chemins doublés...")
fixed = 0

for resource in data['resources']:
    path = resource.get('path', '')
    
    # Enlever "Base de connaissances/Base de connaissances/" 
    # et remplacer par juste "Base de connaissances/"
    if 'Base de connaissances/Base de connaissances/' in path:
        new_path = path.replace('Base de connaissances/Base de connaissances/', 'Base de connaissances/')
        resource['path'] = new_path
        
        # Régénérer l'URL
        parts = new_path.split('/')
        encoded_parts = [urllib.parse.quote(part, safe='') for part in parts]
        resource['url'] = BASE_URL + '/'.join(encoded_parts)
        
        fixed += 1
        if fixed <= 3:
            print(f"   ✅ [{fixed}] {resource['title'][:40]}")
            print(f"       Ancien: ...Base de connaissances/Base de connaissances/...")
            print(f"       Nouveau: ...Base de connaissances/...")

print(f"\n📊 {fixed} URLs corrigées")

with open('megasearch.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ megasearch.json mis à jour")

# Afficher exemple d'URL corrigée
if data['resources']:
    print("\n🔍 Exemple d'URL corrigée:")
    print(data['resources'][0]['url'])

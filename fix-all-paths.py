#!/usr/bin/env python3
import json
import urllib.parse

BASE_URL = 'https://11drumboy11.github.io/Prof-de-basse-V2/'

print("🔧 Correction complète des chemins...")

# 1. Corriger assets_ocr_index.json
print("\n1️⃣ Correction de assets_ocr_index.json...")
with open('assets_ocr_index.json', 'r') as f:
    assets_data = json.load(f)

resources_dict = assets_data.get('resources', {})
new_resources = {}

for old_key, resource_data in resources_dict.items():
    old_file = resource_data.get('file', '')
    
    # Enlever le doublon
    new_file = old_file.replace('Base%20de%20connaissances/Base%20de%20connaissances/', 'Base%20de%20connaissances/')
    new_key = new_file
    
    resource_data['file'] = new_file
    new_resources[new_key] = resource_data

assets_data['resources'] = new_resources

with open('assets_ocr_index.json', 'w') as f:
    json.dump(assets_data, f, ensure_ascii=False, indent=2)

print(f"   ✅ {len(new_resources)} clés corrigées")

# 2. Régénérer megasearch.json
print("\n2️⃣ Régénération de megasearch.json...")
resources_array = []

for resource_id, resource_data in new_resources.items():
    file_path = resource_data.get('file', '')
    decoded_path = urllib.parse.unquote(file_path)
    
    parts = decoded_path.split('/')
    encoded_parts = [urllib.parse.quote(part, safe='') for part in parts]
    url = BASE_URL + '/'.join(encoded_parts)
    
    metadata = resource_data.get('metadata', {})
    search_parts = [
        resource_data.get('title', ''),
        metadata.get('ocr_text', ''),
        metadata.get('composer', ''),
        metadata.get('key', '')
    ]
    search_text = ' '.join(filter(None, search_parts)).lower()
    
    resource = {
        'id': resource_id,
        'type': resource_data.get('type', 'image'),
        'title': resource_data.get('title', 'Sans titre'),
        'path': decoded_path,
        'url': url,
        'filename': decoded_path.split('/')[-1],
        'metadata': metadata,
        'searchText': search_text
    }
    
    resources_array.append(resource)

megasearch = {
    'metadata': {
        'version': '3.0.3',
        'stats': {
            'total_resources': len(resources_array)
        }
    },
    'resources': resources_array
}

with open('megasearch.json', 'w') as f:
    json.dump(megasearch, f, ensure_ascii=False, indent=2)

print(f"   ✅ {len(resources_array)} ressources générées")

# 3. Vérification
print("\n3️⃣ Vérification...")
for r in resources_array:
    if 'aebersold' in r['path']:
        print(f"   Titre: {r['title'][:50]}")
        print(f"   Path: {r['path']}")
        print(f"   URL: {r['url']}")
        has_double = 'Base%20de%20connaissances/Base%20de%20connaissances' in r['url']
        print(f"   ✅ Pas de doublon" if not has_double else "   ❌ Doublon présent")
        break

print("\n✅ CORRECTION TERMINÉE")

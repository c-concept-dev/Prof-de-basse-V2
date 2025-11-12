import json

# Lire
with open('megasearch.json', 'r') as f:
    data = json.load(f)

# Compter
corrected = 0
for r in data['resources']:
    if 'url' in r and 'Prof-de-basse-V2/Prof-de-basse-V2/' in r['url']:
        r['url'] = r['url'].replace(
            'Prof-de-basse-V2/Prof-de-basse-V2/',
            'Prof-de-basse-V2/'
        )
        corrected += 1

# Sauvegarder
with open('megasearch.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'✅ {corrected} URLs corrigées!')
print(f'Total ressources: {len(data["resources"])}')

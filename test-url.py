import json

with open('megasearch.json', 'r') as f:
    data = json.load(f)

print('\n🔗 Première URL à tester:\n')
print(data['resources'][0]['url'])

print('\n\n🔗 URL Arpèges (si disponible):\n')
arpeges = [r for r in data['resources'] if 'Arpeges' in r.get('path', '')]
if arpeges:
    print(arpeges[0]['url'])
else:
    print('Aucune ressource Arpèges trouvée')

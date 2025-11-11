#!/usr/bin/env python3
"""
Rebuild mega-search-index.json from scratch
Fusionne tous les songs_index.json avec URLs complètes
"""

import json
from pathlib import Path
from datetime import datetime
from urllib.parse import quote

print("=" * 70)
print("🔨 RECONSTRUCTION MEGA-SEARCH-INDEX.JSON")
print("=" * 70)

BASE_URL = "https://11drumboy11.github.io/Prof-de-basse-V2"

mega_index = {
    "version": "4.0.0-REBUILD",
    "generated_at": datetime.now().isoformat(),
    "total_resources": 0,
    "sources": [],
    "resources": [],
    "metadata": {
        "stats": {
            "total_mp3": 0,
            "total_pdf": 0,
            "total_images": 0
        }
    }
}

# Trouver tous les songs_index.json
base_path = Path("Base de connaissances")
songs_indexes = list(base_path.glob("**/songs_index.json"))

print(f"\n📂 Trouvé {len(songs_indexes)} fichiers songs_index.json\n")

for songs_file in sorted(songs_indexes):
    try:
        # Chemin relatif depuis la racine du repo
        relative_path = songs_file.parent.relative_to(Path.cwd())
        
        print(f"   📄 {relative_path}/")
        
        with open(songs_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        songs = data.get('songs', [])
        
        for song in songs:
            # Construire l'URL complète
            page_url = song.get('page_url', '')
            
            if page_url:
                # Convertir le chemin relatif en URL complète
                # page_url est comme: "assets/pages/page_001.png"
                full_url = f"{BASE_URL}/{relative_path}/{page_url}".replace(' ', '%20')
                
                # Créer la ressource
                resource = {
                    "id": song.get('id', song.get('page', 'unknown')),
                    "title": song.get('title', f"Page {song.get('page', '?')}"),
                    "type": "image",
                    "url": full_url,
                    "source": str(relative_path / "songs_index.json"),
                    "metadata": song.get('metadata', {}),
                    "search_text": song.get('title', '') + " " + str(song.get('metadata', {}))
                }
                
                # Ajouter la page si disponible
                if 'page' in song:
                    resource['metadata']['page'] = song['page']
                
                mega_index['resources'].append(resource)
                mega_index['metadata']['stats']['total_images'] += 1
        
        mega_index['sources'].append(str(relative_path / "songs_index.json"))
        print(f"      ✓ {len(songs)} ressources ajoutées")
        
    except Exception as e:
        print(f"      ✗ Erreur: {e}")

# Mettre à jour le total
mega_index['total_resources'] = len(mega_index['resources'])

# Sauvegarder
output_file = "mega-search-index.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(mega_index, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 70)
print(f"✅ MEGA-INDEX RECONSTRUIT")
print("=" * 70)
print(f"\n📊 Statistiques:")
print(f"   • Total ressources: {mega_index['total_resources']}")
print(f"   • Total images: {mega_index['metadata']['stats']['total_images']}")
print(f"   • Sources: {len(mega_index['sources'])}")
print(f"\n💾 Fichier sauvegardé: {output_file}")
print(f"   Taille: {Path(output_file).stat().st_size / 1024 / 1024:.2f} MB")

# Vérifier quelques URLs
print(f"\n🔍 Vérification des URLs (3 exemples):")
for i, r in enumerate(mega_index['resources'][:3]):
    print(f"   {i+1}. {r['title']}")
    print(f"      {r['url']}")

print("\n🔧 Commandes Git:")
print("   git add mega-search-index.json")
print("   git commit -m 'Rebuild: mega-search-index.json from scratch'")
print("   git push origin main")

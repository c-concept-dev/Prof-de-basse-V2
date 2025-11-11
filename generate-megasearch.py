#!/usr/bin/env python3
"""
Generate megasearch.json - Prof de Basse V3.0
Convertit assets_ocr_index.json en format compatible avec le nouveau moteur de recherche
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def load_assets_ocr_index(file_path='assets_ocr_index.json'):
    """Charge le fichier assets_ocr_index.json"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Fichier {file_path} introuvable")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Erreur JSON: {e}")
        return None

def convert_resources(assets_data):
    """Convertit le format resources dict en array avec URLs complètes"""
    
    BASE_URL = 'https://11drumboy11.github.io/Prof-de-basse-V2/'
    resources_dict = assets_data.get('resources', {})
    resources_array = []
    
    for resource_id, resource_data in resources_dict.items():
        # Extraire le path
        file_path = resource_data.get('file', '')
        
        # Décoder les %20 pour avoir le vrai path
        import urllib.parse
        decoded_path = urllib.parse.unquote(file_path)
        
        # Construire l'URL complète
        url = BASE_URL + decoded_path if decoded_path else ''
        
        # Créer le texte de recherche
        metadata = resource_data.get('metadata', {})
        search_text_parts = [
            resource_data.get('title', ''),
            metadata.get('ocr_text', ''),
            metadata.get('composer', ''),
            metadata.get('key', ''),
        ]
        
        # Ajouter techniques si présentes
        techniques = metadata.get('techniques', [])
        if techniques:
            search_text_parts.extend(techniques)
        
        search_text = ' '.join(filter(None, search_text_parts))
        
        # Créer la ressource
        resource = {
            'id': resource_id,
            'type': resource_data.get('type', 'image'),
            'title': resource_data.get('title', 'Sans titre'),
            'path': decoded_path,
            'url': url,
            'filename': decoded_path.split('/')[-1] if '/' in decoded_path else decoded_path,
            'metadata': metadata,
            'searchText': search_text.lower()
        }
        
        resources_array.append(resource)
    
    return resources_array

def generate_megasearch(output_file='megasearch.json'):
    """Génère le fichier megasearch.json"""
    
    print("🎸 Génération de megasearch.json...")
    
    # Charger assets_ocr_index.json
    print("📂 Chargement de assets_ocr_index.json...")
    assets_data = load_assets_ocr_index()
    
    if not assets_data:
        print("❌ Impossible de charger les données")
        sys.exit(1)
    
    # Convertir les ressources
    print("🔄 Conversion des ressources...")
    resources = convert_resources(assets_data)
    
    print(f"✅ {len(resources)} ressources converties")
    
    # Calculer les stats
    print("📊 Calcul des statistiques...")
    stats = {
        'total_resources': len(resources),
        'by_type': {}
    }
    
    # Compter par type
    for resource in resources:
        resource_type = resource['type']
        stats['by_type'][resource_type] = stats['by_type'].get(resource_type, 0) + 1
    
    # Compter les méthodes uniques
    methods = set()
    for resource in resources:
        path = resource['path']
        if 'Methodes/' in path:
            parts = path.split('Methodes/')[1].split('/')[0]
            methods.add(parts)
    
    stats['unique_methods'] = len(methods)
    
    # Créer la structure finale
    megasearch_data = {
        'metadata': {
            'version': '3.0.0',
            'generated_at': datetime.now().isoformat(),
            'source': 'assets_ocr_index.json',
            'stats': stats
        },
        'resources': resources
    }
    
    # Sauvegarder
    print(f"💾 Sauvegarde dans {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(megasearch_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ MEGASEARCH.JSON CRÉÉ !")
    print(f"\n📊 STATISTIQUES:")
    print(f"   Total ressources : {stats['total_resources']}")
    print(f"   Méthodes uniques : {stats['unique_methods']}")
    print(f"\n📈 Par type:")
    for resource_type, count in sorted(stats['by_type'].items()):
        print(f"   {resource_type}: {count}")
    print(f"\n🔗 Fichier généré : {output_file}")
    print(f"📦 Taille : {Path(output_file).stat().st_size / 1024:.1f} KB")

if __name__ == '__main__':
    generate_megasearch()

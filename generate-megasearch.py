#!/usr/bin/env python3
"""
Generate megasearch.json V2 - Prof de Basse V3.0
Version améliorée avec nettoyage des URLs
"""

import json
import sys
import re
from datetime import datetime
from pathlib import Path
import urllib.parse

def clean_url(url):
    """Nettoie les URLs en enlevant les caractères de contrôle"""
    # Enlever les caractères de contrôle (0x00-0x1F et 0x7F)
    url = ''.join(char for char in url if ord(char) >= 32 and ord(char) != 127)
    # Enlever les sauts de ligne et espaces en trop
    url = url.replace('\n', '').replace('\r', '').strip()
    return url

def encode_url_path(path):
    """Encode correctement un chemin d'URL"""
    # Séparer le chemin en parties
    parts = path.split('/')
    # Encoder chaque partie
    encoded_parts = [urllib.parse.quote(part, safe='') for part in parts]
    # Rejoindre avec /
    return '/'.join(encoded_parts)

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

def clean_search_text(text):
    """Nettoie le texte de recherche"""
    if not text:
        return ''
    # Enlever les caractères de contrôle
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    # Remplacer les sauts de ligne multiples par un espace
    text = re.sub(r'\s+', ' ', text)
    # Enlever les espaces en début/fin
    text = text.strip()
    return text

def convert_resources(assets_data):
    """Convertit le format resources dict en array avec URLs complètes et propres"""
    
    BASE_URL = 'https://11drumboy11.github.io/Prof-de-basse-V2/'
    resources_dict = assets_data.get('resources', {})
    resources_array = []
    
    for resource_id, resource_data in resources_dict.items():
        # Extraire le path
        file_path = resource_data.get('file', '')
        
        # Décoder les %20 pour avoir le vrai path
        decoded_path = urllib.parse.unquote(file_path)
        
        # Nettoyer le path
        decoded_path = clean_url(decoded_path)
        
        # Encoder proprement pour l'URL
        encoded_path = encode_url_path(decoded_path)
        
        # Construire l'URL complète
        url = BASE_URL + encoded_path if encoded_path else ''
        
        # Nettoyer l'URL finale
        url = clean_url(url)
        
        # Créer le texte de recherche
        metadata = resource_data.get('metadata', {})
        
        # Nettoyer chaque composant
        title = clean_search_text(resource_data.get('title', ''))
        ocr_text = clean_search_text(metadata.get('ocr_text', ''))
        composer = clean_search_text(metadata.get('composer', ''))
        key = clean_search_text(metadata.get('key', ''))
        
        search_text_parts = [title, ocr_text, composer, key]
        
        # Ajouter techniques si présentes
        techniques = metadata.get('techniques', [])
        if techniques:
            search_text_parts.extend([clean_search_text(str(t)) for t in techniques])
        
        search_text = ' '.join(filter(None, search_text_parts))
        search_text = clean_search_text(search_text)
        
        # Créer la ressource
        resource = {
            'id': resource_id,
            'type': resource_data.get('type', 'image'),
            'title': title or 'Sans titre',
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
    
    print("🎸 Génération de megasearch.json V2...")
    
    # Charger assets_ocr_index.json
    print("📂 Chargement de assets_ocr_index.json...")
    assets_data = load_assets_ocr_index()
    
    if not assets_data:
        print("❌ Impossible de charger les données")
        sys.exit(1)
    
    # Convertir les ressources
    print("🔄 Conversion et nettoyage des ressources...")
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
            'version': '3.0.1',
            'generated_at': datetime.now().isoformat(),
            'source': 'assets_ocr_index.json',
            'note': 'URLs cleaned and properly encoded',
            'stats': stats
        },
        'resources': resources
    }
    
    # Sauvegarder
    print(f"💾 Sauvegarde dans {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(megasearch_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ MEGASEARCH.JSON V2 CRÉÉ !")
    print(f"\n📊 STATISTIQUES:")
    print(f"   Total ressources : {stats['total_resources']}")
    print(f"   Méthodes uniques : {stats['unique_methods']}")
    print(f"\n📈 Par type:")
    for resource_type, count in sorted(stats['by_type'].items()):
        print(f"   {resource_type}: {count}")
    print(f"\n🔗 Fichier généré : {output_file}")
    
    file_size = Path(output_file).stat().st_size / 1024
    print(f"📦 Taille : {file_size:.1f} KB")
    
    # Vérifier quelques URLs
    print(f"\n🔍 Vérification échantillon d'URLs:")
    for i, resource in enumerate(resources[:3], 1):
        url = resource['url']
        title = resource['title'][:40]
        # Vérifier pas de caractères de contrôle
        has_control = any(ord(c) < 32 or ord(c) == 127 for c in url)
        status = "❌ CONTRÔLE" if has_control else "✅ PROPRE"
        print(f"   [{i}] {status} - {title}")
        if i == 1:
            print(f"       URL: {url[:80]}...")

if __name__ == '__main__':
    generate_megasearch()

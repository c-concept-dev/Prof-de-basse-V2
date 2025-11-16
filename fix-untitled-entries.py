#!/usr/bin/env python3
"""
🔧 Fix "Sans titre" entries in mega-search-index.json
"""

import json
import re
from pathlib import Path

def fix_untitled_entries(index_file='mega-search-index.json'):
    """Corrige les entrées sans titre"""
    print("🔧 Fixing untitled entries...")
    
    with open(index_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    fixed_count = 0
    
    for resource in data.get('resources', []):
        if resource.get('title') == 'Sans titre':
            # Extraire info du path
            path = resource.get('url', '')
            
            # Cas 1: Fichier de page
            if 'page_' in path and '.png' in path:
                page_match = re.search(r'page_(\d+)', path)
                if page_match:
                    page_num = int(page_match.group(1))
                    resource['title'] = f'Page {page_num}'
                    resource['search_text'] = f'page {page_num}'
                    fixed_count += 1
            
            # Cas 2: Métadonnées
            elif path.endswith('/metadata'):
                method_match = re.search(r'/([^/]+)_v\d+\.\d+/', path)
                if method_match:
                    method = method_match.group(1).replace('-', ' ').replace('_', ' ')
                    resource['title'] = f'{method} - Métadonnées'
                    resource['search_text'] = f'{method.lower()} métadonnées'
                    fixed_count += 1
            
            # Cas 3: Content
            elif path.endswith('/content'):
                method_match = re.search(r'/([^/]+)_v\d+\.\d+/', path)
                if method_match:
                    method = method_match.group(1).replace('-', ' ').replace('_', ' ')
                    resource['title'] = f'{method} - Contenu'
                    resource['search_text'] = f'{method.lower()} contenu'
                    fixed_count += 1
    
    # Sauvegarder
    output_file = 'mega-search-index-FIXED.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {fixed_count} entrées corrigées")
    print(f"💾 Sauvegardé: {output_file}")

if __name__ == '__main__':
    fix_untitled_entries()

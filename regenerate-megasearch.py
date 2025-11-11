#!/usr/bin/env python3
"""
Régénère megasearch.json en scannant la structure RÉELLE des fichiers
"""

import json
from pathlib import Path
from datetime import datetime

def scan_real_structure(base_path="Base de connaissances"):
    """Scanne la structure réelle et génère l'index"""
    
    print("=" * 80)
    print("  📂 SCAN DE LA STRUCTURE RÉELLE")
    print("=" * 80)
    print()
    
    base = Path(base_path)
    
    if not base.exists():
        print(f"❌ Dossier non trouvé: {base_path}")
        return None
    
    resources = []
    base_url = "https://11drumboy11.github.io/Prof-de-basse-V2/Prof-de-basse-V2/"
    
    # Extensions à scanner
    extensions = ['.png', '.jpg', '.jpeg', '.pdf', '.mp3']
    
    print("🔍 Recherche des fichiers...\n")
    
    # Scanner tous les fichiers
    for ext in extensions:
        files = list(base.rglob(f'*{ext}'))
        print(f"   {ext}: {len(files)} fichiers")
        
        for filepath in files:
            # Chemin relatif depuis la racine
            rel_path = filepath.relative_to(Path('.'))
            path_str = str(rel_path)
            
            # URL
            url = base_url + path_str.replace(' ', '%20')
            
            # Type
            file_type = "audio" if ext == '.mp3' else "image" if ext in ['.png', '.jpg', '.jpeg'] else "document"
            
            # Créer la ressource
            resource = {
                "id": path_str.replace(' ', '%20'),
                "path": path_str,
                "url": url,
                "type": file_type,
                "title": filepath.stem,
                "filename": filepath.name,
                "size": filepath.stat().st_size,
                "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
            }
            
            resources.append(resource)
    
    print(f"\n✅ Total ressources trouvées: {len(resources)}")
    
    # Créer l'index
    index = {
        "version": "2.0.0",
        "generated_at": datetime.now().isoformat(),
        "total": len(resources),
        "resources": resources
    }
    
    return index

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Régénérer megasearch.json')
    parser.add_argument('--base', default='Base de connaissances', help='Dossier de base')
    parser.add_argument('--output', default='megasearch-NEW.json', help='Fichier de sortie')
    
    args = parser.parse_args()
    
    print("\n🚀 RÉGÉNÉRATION DE L'INDEX\n")
    
    index = scan_real_structure(args.base)
    
    if index:
        # Sauvegarder
        output_path = Path(args.output)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ INDEX CRÉÉ: {output_path}")
        print(f"   Total: {index['total']} ressources")
        
        # Exemples
        print("\n📋 EXEMPLES DE CHEMINS:")
        for r in index['resources'][:5]:
            print(f"   {r['path']}")
        
        print("\n" + "=" * 80)
        print("📝 PROCHAINES ÉTAPES")
        print("=" * 80)
        print("""
1. Vérifier que les chemins sont corrects:
   
   python3 -c "
   import json
   d = json.load(open('megasearch-NEW.json'))
   print('Premier chemin:')
   print(d['resources'][0]['path'])
   "

2. Si correct, remplacer l'ancien:
   
   cp megasearch.json megasearch.json.OLD
   cp megasearch-NEW.json megasearch.json

3. Tester:
   
   python3 test-url.py

4. Commit:
   
   git add megasearch.json
   git commit -m "Fix: Index régénéré depuis structure réelle"
   git push origin main
        """)
    else:
        print("\n❌ ÉCHEC")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Convertit assets_ocr_index.json au format attendu par index.html
"""

import json
from pathlib import Path

def convert_ocr_index_to_compatible_format(input_file="assets_ocr_index.json"):
    """Convertit l'index OCR au format compatible"""
    
    print("🔧 Conversion de l'index OCR...\n")
    
    # Lire l'index OCR
    with open(input_file, 'r', encoding='utf-8') as f:
        ocr_data = json.load(f)
    
    print(f"📊 Index OCR chargé:")
    print(f"   Version: {ocr_data.get('version')}")
    print(f"   Total scanné: {ocr_data.get('total_scanned')}")
    print(f"   Succès: {ocr_data.get('successful')}")
    print(f"   Échecs: {ocr_data.get('failed')}")
    
    # Convertir resources (dict → array)
    resources_dict = ocr_data.get('resources', {})
    resources_array = []
    
    for filename, resource_data in resources_dict.items():
        # Créer une ressource compatible
        resource = {
            "type": resource_data.get('type', 'unknown'),
            "title": resource_data.get('title', filename),
            "description": resource_data.get('description', ''),
            "url": resource_data.get('url', ''),
            "path": resource_data.get('path', filename),
            "filename": filename
        }
        
        # Ajouter les métadonnées OCR si disponibles
        if 'ocr_text' in resource_data:
            resource['ocr_text'] = resource_data['ocr_text']
        
        if 'metadata' in resource_data:
            resource['metadata'] = resource_data['metadata']
        
        resources_array.append(resource)
    
    print(f"   Ressources: {len(resources_array)}\n")
    
    # Compter par type
    type_counts = {}
    for r in resources_array:
        rtype = r.get('type', 'unknown')
        type_counts[rtype] = type_counts.get(rtype, 0) + 1
    
    # Créer le nouvel index au format attendu
    compatible_index = {
        "metadata": {
            "version": ocr_data.get('version', '1.0.0'),
            "generated": ocr_data.get('generated_at', ''),
            "stats": {
                "total_resources": len(resources_array),
                "mp3_count": type_counts.get('mp3', 0),
                "pdf_count": type_counts.get('pdf', 0),
                "html_count": type_counts.get('html', 0),
                "image_count": type_counts.get('image', 0) + type_counts.get('png', 0),
                "total_scanned": ocr_data.get('total_scanned', 0),
                "successful": ocr_data.get('successful', 0),
                "failed": ocr_data.get('failed', 0)
            }
        },
        "resources": resources_array
    }
    
    # Sauvegarder
    output_file = "search-index-compatible.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(compatible_index, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Index compatible créé : {output_file}")
    print(f"\n📊 Statistiques:")
    stats = compatible_index['metadata']['stats']
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Afficher un aperçu des ressources
    print(f"\n📋 Aperçu des ressources:")
    for i, resource in enumerate(resources_array[:3]):
        print(f"\n   Ressource {i+1}:")
        print(f"      Type: {resource.get('type')}")
        print(f"      Titre: {resource.get('title')}")
        print(f"      URL: {resource.get('url', 'N/A')[:70]}...")
    
    if len(resources_array) > 3:
        print(f"\n   ... et {len(resources_array) - 3} autres ressources")
    
    return output_file

if __name__ == "__main__":
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║     🔄 CONVERTISSEUR D'INDEX OCR - PROF DE BASSE 🎸     ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")
    
    try:
        output = convert_ocr_index_to_compatible_format()
        
        print("\n" + "="*60)
        print("📋 PROCHAINES ÉTAPES:")
        print("="*60)
        print("1. Modifier index.html:")
        print("   sed -i.backup3 \"s/assets_ocr_index.json/search-index-compatible.json/g\" index.html")
        print("\n2. Vérifier:")
        print("   grep 'INDEX_URL' index.html")
        print("\n3. Commit et push:")
        print("   git add search-index-compatible.json index.html")
        print("   git commit -m 'Convert OCR index to compatible format'")
        print("   git push origin main")
        print("="*60)
        
    except FileNotFoundError:
        print("❌ Fichier assets_ocr_index.json non trouvé!")
        print("   Assure-toi d'être dans le bon répertoire.")
    except Exception as e:
        print(f"❌ Erreur: {e}")

#!/usr/bin/env python3
"""
Test Prof de Basse System - V3.0
Vérifie l'intégrité du système de recherche
"""

import json
import sys
from pathlib import Path
import urllib.request
import urllib.error

# Configuration
BASE_URL = 'https://11drumboy11.github.io/Prof-de-basse-V2/'
REQUIRED_FILES = ['megasearch.json', 'index.html', 'assets_ocr_index.json']

def test_file_exists(filename):
    """Vérifie qu'un fichier existe"""
    if Path(filename).exists():
        print(f"✅ {filename} existe")
        return True
    else:
        print(f"❌ {filename} MANQUANT")
        return False

def test_json_valid(filename):
    """Vérifie qu'un JSON est valide"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ {filename} est un JSON valide")
        return True, data
    except json.JSONDecodeError as e:
        print(f"❌ {filename} JSON INVALIDE: {e}")
        return False, None
    except Exception as e:
        print(f"❌ Erreur lecture {filename}: {e}")
        return False, None

def test_megasearch_structure(data):
    """Vérifie la structure de megasearch.json"""
    print("\n📊 Vérification structure megasearch.json...")
    
    errors = []
    
    # Vérifier métadonnées
    if 'metadata' not in data:
        errors.append("Clé 'metadata' manquante")
    else:
        if 'stats' not in data['metadata']:
            errors.append("metadata.stats manquant")
        if 'version' not in data['metadata']:
            errors.append("metadata.version manquant")
    
    # Vérifier ressources
    if 'resources' not in data:
        errors.append("Clé 'resources' manquante")
    elif not isinstance(data['resources'], list):
        errors.append("'resources' devrait être un array, pas un dict")
    elif len(data['resources']) == 0:
        errors.append("'resources' est vide")
    else:
        # Vérifier structure des ressources
        sample = data['resources'][0]
        required_keys = ['id', 'type', 'title', 'url', 'searchText']
        
        for key in required_keys:
            if key not in sample:
                errors.append(f"Clé '{key}' manquante dans les ressources")
    
    if errors:
        print(f"❌ {len(errors)} erreur(s) trouvée(s):")
        for error in errors:
            print(f"   - {error}")
        return False
    else:
        print("✅ Structure megasearch.json correcte")
        return True

def test_urls_format(data, sample_size=5):
    """Vérifie le format des URLs"""
    print(f"\n🔗 Vérification URLs (échantillon de {sample_size})...")
    
    resources = data.get('resources', [])
    if len(resources) == 0:
        print("❌ Aucune ressource à tester")
        return False
    
    sample = resources[:sample_size]
    errors = 0
    
    for i, resource in enumerate(sample, 1):
        url = resource.get('url', '')
        
        if not url:
            print(f"❌ [{i}] URL vide pour: {resource.get('title', 'Sans titre')}")
            errors += 1
        elif not url.startswith('https://'):
            print(f"❌ [{i}] URL invalide (pas https): {url[:50]}...")
            errors += 1
        elif BASE_URL not in url:
            print(f"⚠️  [{i}] URL ne contient pas BASE_URL: {url[:50]}...")
        else:
            print(f"✅ [{i}] {resource.get('title', 'Sans titre')[:40]}")
    
    if errors > 0:
        print(f"\n❌ {errors} erreur(s) d'URL trouvée(s)")
        return False
    else:
        print(f"\n✅ Toutes les URLs sont bien formatées")
        return True

def test_search_text(data, sample_size=5):
    """Vérifie que searchText n'est pas vide"""
    print(f"\n🔍 Vérification searchText (échantillon de {sample_size})...")
    
    resources = data.get('resources', [])
    sample = resources[:sample_size]
    empty_count = 0
    
    for resource in sample:
        search_text = resource.get('searchText', '')
        title = resource.get('title', 'Sans titre')
        
        if not search_text or search_text.strip() == '':
            print(f"⚠️  searchText vide pour: {title}")
            empty_count += 1
        else:
            preview = search_text[:60] + '...' if len(search_text) > 60 else search_text
            print(f"✅ {title[:30]}: {preview}")
    
    if empty_count > 0:
        print(f"\n⚠️  {empty_count} ressource(s) avec searchText vide")
    else:
        print(f"\n✅ Tous les searchText sont remplis")
    
    return True

def test_stats(data):
    """Affiche les statistiques"""
    print("\n📈 Statistiques du système:")
    
    metadata = data.get('metadata', {})
    stats = metadata.get('stats', {})
    
    print(f"   Total ressources : {stats.get('total_resources', 0)}")
    print(f"   Images           : {stats.get('image_count', 0)}")
    print(f"   MP3              : {stats.get('mp3_count', 0)}")
    print(f"   PDF              : {stats.get('pdf_count', 0)}")
    print(f"   Méthodes uniques : {stats.get('unique_methods', 0)}")
    
    return True

def test_url_accessibility(data, sample_size=3):
    """Teste l'accessibilité de quelques URLs (optionnel - prend du temps)"""
    print(f"\n🌐 Test d'accessibilité URLs (échantillon de {sample_size})...")
    print("   (Ce test peut prendre quelques secondes...)")
    
    resources = data.get('resources', [])
    sample = resources[:sample_size]
    
    for i, resource in enumerate(sample, 1):
        url = resource.get('url', '')
        title = resource.get('title', 'Sans titre')
        
        if not url:
            continue
        
        try:
            req = urllib.request.Request(url, method='HEAD')
            urllib.request.urlopen(req, timeout=5)
            print(f"✅ [{i}] Accessible: {title[:40]}")
        except urllib.error.HTTPError as e:
            print(f"❌ [{i}] HTTP {e.code}: {title[:40]}")
        except urllib.error.URLError as e:
            print(f"❌ [{i}] Erreur réseau: {title[:40]}")
        except Exception as e:
            print(f"⚠️  [{i}] Erreur: {title[:40]} - {str(e)[:30]}")
    
    return True

def main():
    print("🎸 Prof de Basse - Test du système V3.0")
    print("=" * 60)
    
    all_passed = True
    
    # Test 1 : Fichiers requis
    print("\n1️⃣  Vérification des fichiers requis...")
    for filename in REQUIRED_FILES:
        if not test_file_exists(filename):
            all_passed = False
    
    # Test 2 : JSON valide
    print("\n2️⃣  Vérification JSON...")
    valid, megasearch_data = test_json_valid('megasearch.json')
    if not valid:
        print("\n❌ ERREUR CRITIQUE: megasearch.json invalide")
        sys.exit(1)
    
    # Test 3 : Structure
    if not test_megasearch_structure(megasearch_data):
        all_passed = False
    
    # Test 4 : URLs
    if not test_urls_format(megasearch_data):
        all_passed = False
    
    # Test 5 : SearchText
    test_search_text(megasearch_data)
    
    # Test 6 : Stats
    test_stats(megasearch_data)
    
    # Test 7 : Accessibilité (optionnel)
    print("\n7️⃣  Test accessibilité des URLs:")
    choice = input("   Tester l'accessibilité ? (peut être lent) [o/N]: ").lower()
    if choice == 'o':
        test_url_accessibility(megasearch_data)
    else:
        print("   ⏭️  Test d'accessibilité ignoré")
    
    # Résumé final
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ TOUS LES TESTS SONT PASSÉS !")
        print("\n🚀 Le système est prêt à être déployé")
        print("\nProchaines étapes:")
        print("  1. git add megasearch.json index.html")
        print("  2. git commit -m '🔧 Fix: Système de recherche réparé'")
        print("  3. git push origin main")
        print("  4. Attendre 2-3 min et tester sur GitHub Pages")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("\nVeuillez corriger les erreurs avant de déployer")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

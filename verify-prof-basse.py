#!/usr/bin/env python3
"""
Script de vérification du système Prof de Basse V2
"""
import json
import sys

def verify_mega_search_index():
    """Vérifie l'intégrité du mega-search-index.json"""
    print("🔍 Vérification du mega-search-index.json")
    print("=" * 60)
    
    try:
        with open('mega-search-index.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("✅ Fichier JSON valide")
        
        # Stats générales
        resources = data.get('resources', [])
        metadata = data.get('metadata', {})
        
        print(f"\n📊 Statistiques générales:")
        print(f"   • Total ressources: {len(resources)}")
        print(f"   • Version: {metadata.get('version', 'N/A')}")
        print(f"   • Dernière mise à jour: {metadata.get('last_updated', 'N/A')}")
        
        # Compter par type
        types_count = {}
        sources_count = {}
        repo_urls = set()
        
        for resource in resources:
            # Types
            res_type = resource.get('type', 'unknown')
            types_count[res_type] = types_count.get(res_type, 0) + 1
            
            # Sources
            source = resource.get('source', 'unknown')
            sources_count[source] = sources_count.get(source, 0) + 1
            
            # URLs (vérifier le repo)
            url = resource.get('url', '')
            if 'github.io' in url:
                if 'Prof-de-basse-V2' in url:
                    repo_urls.add('Prof-de-basse-V2')
                elif 'Prof-de-basse' in url and 'V2' not in url:
                    repo_urls.add('Prof-de-basse (ancien)')
        
        print(f"\n📁 Ressources par type:")
        for rtype, count in sorted(types_count.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {rtype}: {count}")
        
        print(f"\n📚 Ressources par source (top 10):")
        for source, count in sorted(sources_count.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   • {source}: {count}")
        
        print(f"\n🔗 Repositories détectés dans les URLs:")
        for repo in sorted(repo_urls):
            print(f"   • {repo}")
        
        # Vérifier les URLs
        v2_count = sum(1 for r in resources if 'Prof-de-basse-V2' in r.get('url', ''))
        old_count = sum(1 for r in resources if 'Prof-de-basse/' in r.get('url', '') and 'V2' not in r.get('url', ''))
        
        print(f"\n🎯 Vérification des chemins:")
        print(f"   • URLs avec Prof-de-basse-V2: {v2_count}")
        print(f"   • URLs avec ancien repo: {old_count}")
        
        if old_count > 0:
            print(f"\n⚠️  ATTENTION: {old_count} ressources pointent encore vers l'ancien repo!")
            print("   Exécute fix-urls.py pour corriger")
        else:
            print(f"\n✅ Tous les chemins pointent vers le bon repo (V2)")
        
        return True
        
    except FileNotFoundError:
        print("❌ Fichier mega-search-index.json non trouvé")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def verify_complete_resource_map():
    """Vérifie complete-resource-map.json"""
    print("\n\n🗺️  Vérification du complete-resource-map.json")
    print("=" * 60)
    
    try:
        with open('resources/complete-resource-map.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("✅ Fichier JSON valide")
        
        mp3_methods = data.get('mp3_methods', [])
        pdf_methods = data.get('pdf_methods', [])
        
        print(f"\n📊 Contenu:")
        print(f"   • Méthodes MP3: {len(mp3_methods)}")
        print(f"   • Méthodes PDF: {len(pdf_methods)}")
        
        # Vérifier les URLs
        all_urls = []
        for method in mp3_methods + pdf_methods:
            base_url = method.get('base_url', '')
            if base_url:
                all_urls.append(base_url)
        
        v2_urls = [url for url in all_urls if 'Prof-de-basse-V2' in url]
        old_urls = [url for url in all_urls if 'Prof-de-basse/' in url and 'V2' not in url]
        
        print(f"\n🔗 URLs:")
        print(f"   • Prof-de-basse-V2: {len(v2_urls)}")
        print(f"   • Ancien repo: {len(old_urls)}")
        
        if old_urls:
            print(f"\n⚠️  {len(old_urls)} URLs à corriger")
        else:
            print(f"\n✅ Toutes les URLs sont correctes")
        
        return True
        
    except FileNotFoundError:
        print("❌ Fichier resources/complete-resource-map.json non trouvé")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🎸 VÉRIFICATION SYSTÈME PROF DE BASSE V2")
    print("="*60 + "\n")
    
    result1 = verify_mega_search_index()
    result2 = verify_complete_resource_map()
    
    print("\n" + "="*60)
    if result1 and result2:
        print("✅ SYSTÈME OPÉRATIONNEL")
    else:
        print("⚠️  ATTENTION: Certaines vérifications ont échoué")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()

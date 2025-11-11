#!/usr/bin/env python3
"""
Test d'accessibilité des fichiers MP3 du système Prof de Basse V2
"""
import urllib.request
import urllib.error
import sys

def test_url(url, name):
    """Teste si une URL est accessible"""
    try:
        req = urllib.request.Request(url, method='HEAD')
        response = urllib.request.urlopen(req, timeout=10)
        status = response.status
        
        if status == 200:
            content_length = response.headers.get('Content-Length', 'Unknown')
            if content_length != 'Unknown':
                size_mb = int(content_length) / (1024 * 1024)
                print(f"✅ {name}: {status} ({size_mb:.2f} MB)")
            else:
                print(f"✅ {name}: {status}")
            return True
        else:
            print(f"⚠️  {name}: {status}")
            return False
            
    except urllib.error.HTTPError as e:
        print(f"❌ {name}: HTTP {e.code}")
        return False
    except urllib.error.URLError as e:
        print(f"❌ {name}: {e.reason}")
        return False
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
        return False

def main():
    print("\n" + "="*60)
    print("🎵 TEST D'ACCESSIBILITÉ DES MP3")
    print("="*60 + "\n")
    
    base_url = "https://11drumboy11.github.io/Prof-de-basse-V2/Methodes/70%20Funk%20&%20Disco%20bass%20MP3"
    
    # Tests sur échantillon représentatif
    test_tracks = [
        ("Track 01", f"{base_url}/Track%2001.mp3"),
        ("Track 05", f"{base_url}/Track%2005.mp3"),
        ("Track 12", f"{base_url}/Track%2012.mp3"),
        ("Track 20", f"{base_url}/Track%2020.mp3"),
        ("Track 45", f"{base_url}/Track%2045.mp3"),
        ("Track 99", f"{base_url}/Track%2099.mp3"),
    ]
    
    print("🔍 Test des MP3 - 70s Funk & Disco:")
    print("-" * 60)
    
    success_count = 0
    for name, url in test_tracks:
        if test_url(url, name):
            success_count += 1
    
    print("\n" + "="*60)
    print(f"📊 Résultat: {success_count}/{len(test_tracks)} URLs accessibles")
    
    if success_count == len(test_tracks):
        print("✅ TOUS LES MP3 TESTÉS SONT ACCESSIBLES")
    elif success_count > 0:
        print("⚠️  CERTAINS MP3 NE SONT PAS ACCESSIBLES")
    else:
        print("❌ AUCUN MP3 ACCESSIBLE - Vérifier GitHub Pages")
    
    print("="*60 + "\n")
    
    # Test du mega-search-index
    print("\n🔍 Test du mega-search-index.json:")
    print("-" * 60)
    
    if test_url(
        "https://11drumboy11.github.io/Prof-de-basse-V2/mega-search-index.json",
        "mega-search-index.json"
    ):
        print("\n✅ Index de recherche accessible")
    else:
        print("\n❌ Index de recherche non accessible")
    
    print()

if __name__ == '__main__':
    main()

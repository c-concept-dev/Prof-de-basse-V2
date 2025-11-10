#!/usr/bin/env python3
"""
Test OCR Quality - Prof de Basse
Teste l'OCR sur échantillon pour valider avant scan complet
"""

import os
import json
from pathlib import Path
from ocr_scanner_v2 import (
    extract_text_from_image,
    detect_title, detect_composer, detect_techniques,
    detect_key, detect_tempo, detect_page_track,
    IMAGE_EXTENSIONS, SCAN_DIRECTORIES
)

# ============================================================================
# CONFIGURATION
# ============================================================================

REPO_PATH = "/Users/christophebonnet/Documents/GitHub/Prof-de-basse"  # À MODIFIER
TEST_SAMPLES = 5  # Nombre de fichiers à tester par dossier

# Tests de référence (résultats attendus pour validation)
REFERENCE_TESTS = [
    {
        'pattern': 'so_what',
        'expected_title': 'So What',
        'expected_composer': 'Miles Davis',
        'expected_key': 'D'
    },
    {
        'pattern': 'superstition',
        'expected_title': 'Superstition',
        'expected_composer': 'Stevie Wonder'
    },
    {
        'pattern': 'walking',
        'expected_techniques': ['walking']
    }
]

# ============================================================================
# TEST ÉCHANTILLON
# ============================================================================

def test_sample_files(base_path, num_samples=5):
    """
    Teste OCR sur un échantillon de fichiers de chaque dossier
    """
    base_path = Path(base_path)
    test_results = []
    
    print("🧪 TEST OCR - Échantillon de fichiers\n")
    print("="*80)
    
    for scan_dir in SCAN_DIRECTORIES:
        dir_path = base_path / scan_dir
        if not dir_path.exists():
            print(f"\n⚠️ Dossier non trouvé: {scan_dir}")
            continue
        
        print(f"\n📂 Testing {scan_dir}")
        print("-"*80)
        
        # Récupérer fichiers images
        image_files = []
        for ext in IMAGE_EXTENSIONS:
            image_files.extend(list(dir_path.rglob(f'*{ext}')))
        
        # Limiter au nombre d'échantillons
        sample_files = image_files[:num_samples]
        
        if not sample_files:
            print("  ⚠️ Aucun fichier image trouvé")
            continue
        
        print(f"  📊 {len(sample_files)} fichiers testés")
        
        # Tester chaque fichier
        for image_file in sample_files:
            result = test_single_file(image_file, base_path)
            test_results.append(result)
    
    return test_results

def test_single_file(image_path, base_path):
    """Teste OCR sur un seul fichier et affiche résultats détaillés"""
    image_path = Path(image_path)
    
    print(f"\n  📄 {image_path.name}")
    print(f"      Path: {image_path.relative_to(base_path)}")
    
    # Extraction OCR
    text_full = extract_text_from_image(str(image_path), region='full')
    text_top = extract_text_from_image(str(image_path), region='top')
    
    if not text_full:
        print("      ❌ OCR échoué (pas de texte extrait)")
        return {
            'file': str(image_path.name),
            'success': False,
            'error': 'No text extracted'
        }
    
    # Détection métadonnées
    title = detect_title(text_top)
    composer = detect_composer(text_full)
    techniques = detect_techniques(text_full)
    key = detect_key(text_full)
    tempo = detect_tempo(text_full)
    page_track = detect_page_track(text_full, image_path.name)
    
    # Affichage résultats
    print(f"      ✅ Texte extrait: {len(text_full)} caractères")
    print(f"      📝 Title    : {title or '❌ Non détecté'}")
    print(f"      🎵 Composer : {composer or '❌ Non détecté'}")
    print(f"      🎸 Techniques: {', '.join(techniques) if techniques else '❌ Non détecté'}")
    print(f"      🔑 Key      : {key or '❌ Non détecté'}")
    print(f"      ⏱️ Tempo    : {tempo or '❌ Non détecté'} BPM")
    print(f"      📖 Page/Track: {page_track or '❌ Non détecté'}")
    
    # Score de qualité
    quality_score = 0
    if title and title != "Unknown": quality_score += 25
    if composer: quality_score += 20
    if techniques: quality_score += 20
    if key: quality_score += 15
    if tempo: quality_score += 10
    if page_track: quality_score += 10
    
    quality_level = (
        "🟢 Excellent" if quality_score >= 75 else
        "🟡 Bon" if quality_score >= 50 else
        "🟠 Moyen" if quality_score >= 25 else
        "🔴 Faible"
    )
    
    print(f"      📊 Qualité  : {quality_level} ({quality_score}/100)")
    
    return {
        'file': str(image_path.name),
        'success': True,
        'title': title,
        'composer': composer,
        'techniques': techniques,
        'key': key,
        'tempo': tempo,
        'page_track': page_track,
        'text_length': len(text_full),
        'quality_score': quality_score
    }

# ============================================================================
# VALIDATION AVEC RÉFÉRENCES
# ============================================================================

def validate_with_references(test_results):
    """
    Valide les résultats OCR contre des références connues
    """
    print("\n" + "="*80)
    print("🎯 VALIDATION AVEC RÉFÉRENCES")
    print("="*80)
    
    validated = 0
    
    for ref in REFERENCE_TESTS:
        print(f"\n🔍 Recherche : {ref['pattern']}")
        
        # Trouver résultat correspondant
        matching_result = None
        for result in test_results:
            if ref['pattern'].lower() in result['file'].lower():
                matching_result = result
                break
        
        if not matching_result:
            print(f"   ⚠️ Fichier non trouvé dans les tests")
            continue
        
        # Vérifier titre
        if 'expected_title' in ref:
            detected = matching_result.get('title', '')
            expected = ref['expected_title']
            match = expected.lower() in detected.lower()
            status = "✅" if match else "❌"
            print(f"   {status} Title: {detected} (attendu: {expected})")
            if match: validated += 1
        
        # Vérifier compositeur
        if 'expected_composer' in ref:
            detected = matching_result.get('composer', '')
            expected = ref['expected_composer']
            match = detected and expected.lower() in detected.lower()
            status = "✅" if match else "❌"
            print(f"   {status} Composer: {detected or 'None'} (attendu: {expected})")
            if match: validated += 1
        
        # Vérifier techniques
        if 'expected_techniques' in ref:
            detected = matching_result.get('techniques', [])
            expected = ref['expected_techniques']
            match = any(exp in detected for exp in expected)
            status = "✅" if match else "❌"
            print(f"   {status} Techniques: {detected} (attendu: {expected})")
            if match: validated += 1
    
    total_checks = sum(
        len([k for k in ref.keys() if k.startswith('expected_')])
        for ref in REFERENCE_TESTS
    )
    
    if total_checks > 0:
        success_rate = validated / total_checks * 100
        print(f"\n📊 Taux de réussite : {validated}/{total_checks} ({success_rate:.1f}%)")
        
        if success_rate >= 75:
            print("🟢 Excellent ! OCR prêt pour scan complet")
        elif success_rate >= 50:
            print("🟡 Bon, mais peut être amélioré")
        else:
            print("🔴 Qualité insuffisante, ajustements nécessaires")

# ============================================================================
# STATISTIQUES GLOBALES
# ============================================================================

def print_global_statistics(test_results):
    """Affiche statistiques globales des tests"""
    successful = [r for r in test_results if r['success']]
    total = len(test_results)
    
    if total == 0:
        print("\n⚠️ Aucun résultat à analyser")
        return
    
    print("\n" + "="*80)
    print("📊 STATISTIQUES GLOBALES")
    print("="*80)
    
    # Taux de succès
    success_rate = len(successful) / total * 100
    print(f"\n✅ Fichiers traités avec succès : {len(successful)}/{total} ({success_rate:.1f}%)")
    
    # Détection par champ
    with_title = sum(1 for r in successful if r.get('title') and r['title'] != "Unknown")
    with_composer = sum(1 for r in successful if r.get('composer'))
    with_techniques = sum(1 for r in successful if r.get('techniques'))
    with_key = sum(1 for r in successful if r.get('key'))
    with_tempo = sum(1 for r in successful if r.get('tempo'))
    with_page = sum(1 for r in successful if r.get('page_track'))
    
    print(f"\n📈 Détection par champ :")
    print(f"   Title      : {with_title}/{len(successful)} ({with_title/len(successful)*100:.1f}%)")
    print(f"   Composer   : {with_composer}/{len(successful)} ({with_composer/len(successful)*100:.1f}%)")
    print(f"   Techniques : {with_techniques}/{len(successful)} ({with_techniques/len(successful)*100:.1f}%)")
    print(f"   Key        : {with_key}/{len(successful)} ({with_key/len(successful)*100:.1f}%)")
    print(f"   Tempo      : {with_tempo}/{len(successful)} ({with_tempo/len(successful)*100:.1f}%)")
    print(f"   Page/Track : {with_page}/{len(successful)} ({with_page/len(successful)*100:.1f}%)")
    
    # Score de qualité moyen
    avg_quality = sum(r['quality_score'] for r in successful) / len(successful)
    print(f"\n🎯 Score de qualité moyen : {avg_quality:.1f}/100")
    
    # Distribution qualité
    excellent = sum(1 for r in successful if r['quality_score'] >= 75)
    good = sum(1 for r in successful if 50 <= r['quality_score'] < 75)
    medium = sum(1 for r in successful if 25 <= r['quality_score'] < 50)
    poor = sum(1 for r in successful if r['quality_score'] < 25)
    
    print(f"\n📊 Distribution qualité :")
    print(f"   🟢 Excellent (75-100) : {excellent}")
    print(f"   🟡 Bon (50-74)        : {good}")
    print(f"   🟠 Moyen (25-49)      : {medium}")
    print(f"   🔴 Faible (0-24)      : {poor}")
    
    print("\n" + "="*80)

# ============================================================================
# RECOMMANDATIONS
# ============================================================================

def provide_recommendations(test_results):
    """Fournit recommandations basées sur résultats"""
    successful = [r for r in test_results if r['success']]
    
    if not successful:
        print("\n⚠️ Pas assez de résultats pour recommandations")
        return
    
    print("\n💡 RECOMMANDATIONS")
    print("="*80)
    
    # Analyse des faiblesses
    with_title = sum(1 for r in successful if r.get('title') and r['title'] != "Unknown")
    with_composer = sum(1 for r in successful if r.get('composer'))
    with_techniques = sum(1 for r in successful if r.get('techniques'))
    
    title_rate = with_title / len(successful)
    composer_rate = with_composer / len(successful)
    technique_rate = with_techniques / len(successful)
    
    if title_rate < 0.8:
        print("\n⚠️ Détection titres faible (<80%)")
        print("   💡 Suggestion : Améliorer patterns TITLE_PATTERNS")
        print("   💡 Vérifier si preprocessing images aide")
    
    if composer_rate < 0.5:
        print("\n⚠️ Détection compositeurs faible (<50%)")
        print("   💡 Suggestion : Enrichir KNOWN_COMPOSERS")
        print("   💡 Améliorer patterns COMPOSER_PATTERNS")
    
    if technique_rate < 0.6:
        print("\n⚠️ Détection techniques faible (<60%)")
        print("   💡 Suggestion : Ajouter patterns dans TECHNIQUE_PATTERNS")
    
    # Recommandation générale
    avg_quality = sum(r['quality_score'] for r in successful) / len(successful)
    
    if avg_quality >= 75:
        print("\n🟢 Qualité globale excellente")
        print("   ✅ OCR prêt pour scan complet du repository")
        print("   🚀 Lancer: python ocr_scanner_v2.py")
    elif avg_quality >= 50:
        print("\n🟡 Qualité globale correcte")
        print("   ⚠️ Améliorations recommandées avant scan complet")
        print("   💡 Ajuster patterns puis relancer test")
    else:
        print("\n🔴 Qualité globale insuffisante")
        print("   ❌ Ajustements nécessaires avant scan complet")
        print("   💡 Vérifier configuration Tesseract")
        print("   💡 Tester preprocessing images")

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("🎸 Prof de Basse - Test OCR Quality")
    print("="*80)
    print(f"📂 Repository: {REPO_PATH}")
    print(f"🧪 Samples per directory: {TEST_SAMPLES}")
    print()
    
    # Tests échantillons
    test_results = test_sample_files(REPO_PATH, TEST_SAMPLES)
    
    # Validation avec références
    if test_results:
        validate_with_references(test_results)
    
    # Statistiques
    print_global_statistics(test_results)
    
    # Recommandations
    provide_recommendations(test_results)
    
    # Sauvegarde résultats
    output_file = "test_ocr_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Résultats sauvegardés : {output_file}")
    print("\n✅ Test terminé !")

if __name__ == "__main__":
    main()

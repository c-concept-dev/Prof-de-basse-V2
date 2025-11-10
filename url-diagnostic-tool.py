#!/usr/bin/env python3
"""
URL Fixer & Diagnostic Tool - Prof de Basse
Scanne le repo, vérifie les URLs, corrige les liens morts
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import re

class URLDiagnosticTool:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.base_url = "https://11drumboy11.github.io/Prof-de-basse/"
        self.issues = []
        self.stats = {
            "total_images": 0,
            "images_in_index": 0,
            "broken_urls": 0,
            "fixed_urls": 0,
            "missing_from_index": 0
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Log avec couleurs"""
        colors = {
            "INFO": "\033[94m",
            "SUCCESS": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m",
            "RESET": "\033[0m"
        }
        color = colors.get(level, colors["RESET"])
        reset = colors["RESET"]
        print(f"{color}{message}{reset}")
    
    def find_all_images(self) -> Dict[str, Path]:
        """Trouve toutes les images dans le repo"""
        self.log("\n🔍 SCAN DU REPO...", "INFO")
        
        images = {}
        patterns = ["**/*.jpg", "**/*.jpeg", "**/*.png"]
        
        for pattern in patterns:
            for img_path in self.repo_path.glob(pattern):
                # Exclure certains dossiers
                if any(ex in str(img_path) for ex in [".git", "node_modules", "__pycache__"]):
                    continue
                
                # Calculer le chemin relatif
                rel_path = img_path.relative_to(self.repo_path)
                images[str(rel_path)] = img_path
        
        self.stats["total_images"] = len(images)
        self.log(f"   ✅ {len(images)} images trouvées", "SUCCESS")
        return images
    
    def build_correct_url(self, file_path: str) -> str:
        """Construit l'URL correcte pour un fichier"""
        # Nettoyer le chemin
        path = str(file_path).lstrip("./")
        
        # Encoder les caractères spéciaux
        parts = path.split("/")
        encoded_parts = []
        for part in parts:
            # Encoder les espaces et & mais PAS les apostrophes
            encoded = part.replace(" ", "%20").replace("&", "%26")
            encoded_parts.append(encoded)
        
        encoded_path = "/".join(encoded_parts)
        
        return self.base_url + encoded_path
    
    def load_mega_index(self) -> Dict:
        """Charge le mega-search-index.json"""
        index_path = self.repo_path / "mega-search-index.json"
        
        if not index_path.exists():
            self.log("\n⚠️  mega-search-index.json n'existe pas encore", "WARNING")
            return {"resources": []}
        
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.log(f"\n✅ mega-search-index.json chargé ({len(data.get('resources', []))} ressources)", "SUCCESS")
                return data
        except Exception as e:
            self.log(f"\n❌ Erreur chargement mega-index: {e}", "ERROR")
            return {"resources": []}
    
    def verify_urls(self, mega_index: Dict, all_images: Dict[str, Path]) -> List[Dict]:
        """Vérifie toutes les URLs du mega-index"""
        self.log("\n🔍 VÉRIFICATION DES URLs...", "INFO")
        
        broken_urls = []
        resources = mega_index.get("resources", [])
        
        for resource in resources:
            if resource.get("type") != "image":
                continue
            
            self.stats["images_in_index"] += 1
            
            current_url = resource.get("url", "")
            resource_id = resource.get("id", "")
            
            # Extraire le chemin depuis l'URL
            if current_url.startswith(self.base_url):
                url_path = current_url[len(self.base_url):]
                # Décoder les caractères
                url_path = url_path.replace("%20", " ").replace("%26", "&").replace("%27", "'")
            else:
                url_path = resource_id
            
            # Chercher si le fichier existe
            file_exists = False
            correct_path = None
            
            # Chercher dans toutes les images
            for img_path, img_full_path in all_images.items():
                # Comparer les noms de fichiers
                if img_path.endswith(url_path) or url_path.endswith(img_path.split('/')[-1]):
                    file_exists = True
                    correct_path = img_path
                    break
            
            if not file_exists:
                # Fichier introuvable
                self.stats["broken_urls"] += 1
                broken_urls.append({
                    "resource_id": resource_id,
                    "title": resource.get("title", ""),
                    "current_url": current_url,
                    "issue": "FILE_NOT_FOUND",
                    "suggested_fix": None
                })
            elif correct_path:
                # Vérifier si l'URL est correcte
                correct_url = self.build_correct_url(correct_path)
                
                if current_url != correct_url:
                    # URL incorrecte
                    self.stats["broken_urls"] += 1
                    broken_urls.append({
                        "resource_id": resource_id,
                        "title": resource.get("title", ""),
                        "current_url": current_url,
                        "correct_url": correct_url,
                        "correct_path": correct_path,
                        "issue": "WRONG_URL"
                    })
        
        self.log(f"   ⚠️  {len(broken_urls)} URLs problématiques trouvées", "WARNING")
        return broken_urls
    
    def find_missing_images(self, mega_index: Dict, all_images: Dict[str, Path]) -> List[Dict]:
        """Trouve les images qui ne sont pas dans l'index"""
        self.log("\n🔍 RECHERCHE DES IMAGES MANQUANTES...", "INFO")
        
        indexed_files = set()
        for resource in mega_index.get("resources", []):
            if resource.get("type") == "image":
                resource_id = resource.get("id", "")
                indexed_files.add(resource_id.split("/")[-1])  # Juste le nom de fichier
        
        missing = []
        for img_path in all_images.keys():
            filename = img_path.split("/")[-1]
            if filename not in indexed_files:
                missing.append({
                    "path": img_path,
                    "url": self.build_correct_url(img_path)
                })
        
        self.stats["missing_from_index"] = len(missing)
        self.log(f"   📋 {len(missing)} images non indexées", "INFO")
        return missing
    
    def fix_mega_index(self, mega_index: Dict, broken_urls: List[Dict]) -> Dict:
        """Corrige le mega-index"""
        self.log("\n🔧 CORRECTION DU MEGA-INDEX...", "INFO")
        
        fixed_count = 0
        resources = mega_index.get("resources", [])
        
        # Créer un mapping pour les corrections
        corrections = {}
        for broken in broken_urls:
            if broken["issue"] == "WRONG_URL" and broken.get("correct_url"):
                corrections[broken["resource_id"]] = broken["correct_url"]
        
        # Appliquer les corrections
        for resource in resources:
            resource_id = resource.get("id", "")
            if resource_id in corrections:
                resource["url"] = corrections[resource_id]
                fixed_count += 1
        
        self.stats["fixed_urls"] = fixed_count
        self.log(f"   ✅ {fixed_count} URLs corrigées", "SUCCESS")
        
        return mega_index
    
    def save_corrected_index(self, mega_index: Dict, output_path: str = "mega-search-index-fixed.json"):
        """Sauvegarde le mega-index corrigé"""
        output = self.repo_path / output_path
        
        try:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(mega_index, f, ensure_ascii=False, indent=2)
            
            self.log(f"\n✅ Index corrigé sauvegardé: {output}", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"\n❌ Erreur sauvegarde: {e}", "ERROR")
            return False
    
    def generate_report(self, broken_urls: List[Dict], missing_images: List[Dict]) -> str:
        """Génère un rapport détaillé"""
        report = []
        report.append("\n" + "="*80)
        report.append("📊 RAPPORT DE DIAGNOSTIC - Prof de Basse")
        report.append("="*80)
        report.append(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Stats
        report.append("\n📈 STATISTIQUES:")
        report.append(f"   Total images dans le repo: {self.stats['total_images']}")
        report.append(f"   Images dans le mega-index: {self.stats['images_in_index']}")
        report.append(f"   URLs cassées/incorrectes: {self.stats['broken_urls']}")
        report.append(f"   URLs corrigées: {self.stats['fixed_urls']}")
        report.append(f"   Images non indexées: {self.stats['missing_from_index']}")
        
        # URLs cassées
        if broken_urls:
            report.append("\n❌ URLs PROBLÉMATIQUES:")
            for i, broken in enumerate(broken_urls[:20], 1):  # Max 20
                report.append(f"\n   {i}. {broken['title']}")
                report.append(f"      Problème: {broken['issue']}")
                report.append(f"      URL actuelle: {broken['current_url']}")
                if broken.get('correct_url'):
                    report.append(f"      URL correcte: {broken['correct_url']}")
            
            if len(broken_urls) > 20:
                report.append(f"\n   ... et {len(broken_urls) - 20} autres")
        
        # Images manquantes
        if missing_images:
            report.append(f"\n📋 IMAGES NON INDEXÉES: (premiers 10)")
            for i, missing in enumerate(missing_images[:10], 1):
                report.append(f"   {i}. {missing['path']}")
        
        report.append("\n" + "="*80)
        
        return "\n".join(report)
    
    def run_full_diagnostic(self):
        """Lance le diagnostic complet"""
        self.log("\n🚀 DIAGNOSTIC COMPLET DU REPO", "INFO")
        
        # 1. Scanner les images
        all_images = self.find_all_images()
        
        # 2. Charger le mega-index
        mega_index = self.load_mega_index()
        
        # 3. Vérifier les URLs
        broken_urls = self.verify_urls(mega_index, all_images)
        
        # 4. Trouver les images manquantes
        missing_images = self.find_missing_images(mega_index, all_images)
        
        # 5. Générer le rapport
        report = self.generate_report(broken_urls, missing_images)
        print(report)
        
        # 6. Proposer la correction
        if broken_urls:
            print("\n🔧 CORRECTION DISPONIBLE")
            response = input("\nVoulez-vous corriger automatiquement les URLs ? (o/n): ")
            
            if response.lower() == 'o':
                # Corriger
                corrected_index = self.fix_mega_index(mega_index, broken_urls)
                
                # Sauvegarder
                self.save_corrected_index(corrected_index, "mega-search-index.json")
                
                self.log("\n✅ CORRECTION TERMINÉE !", "SUCCESS")
                self.log("   Vous pouvez maintenant commit et push les changements", "INFO")
        
        return {
            "all_images": all_images,
            "broken_urls": broken_urls,
            "missing_images": missing_images,
            "stats": self.stats
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='URL Diagnostic & Fix Tool')
    parser.add_argument('--repo', default='.', help='Chemin du repo')
    parser.add_argument('--fix', action='store_true', help='Corriger automatiquement sans demander')
    args = parser.parse_args()
    
    tool = URLDiagnosticTool(args.repo)
    results = tool.run_full_diagnostic()
    
    # Auto-fix si demandé
    if args.fix and results['broken_urls']:
        mega_index = tool.load_mega_index()
        corrected = tool.fix_mega_index(mega_index, results['broken_urls'])
        tool.save_corrected_index(corrected, "mega-search-index.json")


if __name__ == "__main__":
    main()

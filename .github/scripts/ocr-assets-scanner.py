#!/usr/bin/env python3
"""
OCR Assets Scanner V1 - Prof de Basse
Scanner automatique pour extraire les métadonnées des images de partitions
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import hashlib

try:
    from PIL import Image
    import pytesseract
except ImportError:
    print("❌ ERREUR: Bibliothèques manquantes")
    print("   Installer avec: pip install Pillow pytesseract --break-system-packages")
    exit(1)


class OCRAssetsScanner:
    """Scanner OCR pour images de partitions musicales"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.ocr_index = {
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "total_scanned": 0,
            "successful": 0,
            "failed": 0,
            "resources": {}
        }
        self.processed_hashes = set()
        self.stats = {
            "title_found": 0,
            "composer_found": 0,
            "key_found": 0,
            "technique_found": 0
        }
        
        # Patterns de détection musicale
        self.musical_patterns = {
            "keys": [
                # Majeur
                r'\b([CDEFGAB])\s*(?:maj(?:or)?|M|Maj)\b',
                # Mineur
                r'\b([CDEFGAB])\s*(?:min(?:or)?|m|-)\b',
                # Altérations
                r'\b([CDEFGAB][#b♯♭]?)\s*(?:maj|min|m|M)?\b'
            ],
            "techniques": {
                "slap": ["slap", "thumb", "pop", "percussive"],
                "walking": ["walking", "walk", "swing"],
                "ghost notes": ["ghost", "dead note", "muted"],
                "hammer-on": ["hammer", "pull-off", "legato"],
                "tapping": ["tap", "tapping", "two-hand"],
                "fingerstyle": ["fingerstyle", "finger", "pizz"],
                "pick": ["pick", "plectrum", "médiator"],
                "funk": ["funk", "funky", "groove"],
                "jazz": ["jazz", "bebop", "swing"],
                "rock": ["rock", "heavy", "metal"],
                "latin": ["latin", "bossa", "samba", "salsa"],
                "blues": ["blues", "shuffle"],
                "modal": ["modal", "dorian", "phrygian", "lydian", "mixolydian"]
            },
            "composers": [
                # Jazz
                "Miles Davis", "John Coltrane", "Bill Evans", "Charlie Parker",
                "Thelonious Monk", "Wayne Shorter", "Herbie Hancock", "Chick Corea",
                # Funk/Soul
                "James Brown", "Stevie Wonder", "Parliament", "Tower of Power",
                "Earth Wind & Fire", "Bootsy Collins", "George Clinton",
                # Classique basse
                "Victor Wooten", "Jaco Pastorius", "Marcus Miller", "Stanley Clarke"
            ]
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
    
    def find_asset_images(self) -> List[Path]:
        """Trouve toutes les images dans les dossiers assets"""
        self.log("\n🔍 RECHERCHE DES IMAGES DANS LES DOSSIERS ASSETS...", "INFO")
        
        images = []
        patterns = ["**/*assets*/*.png", "**/*assets*/*.jpg", "**/*assets*/*.jpeg"]
        
        for pattern in patterns:
            found = list(self.repo_path.glob(pattern))
            images.extend(found)
        
        # Dédupliquer
        images = list(set(images))
        
        # Exclure certains dossiers
        exclude = [".git", "node_modules", "__pycache__", ".github"]
        images = [img for img in images if not any(ex in str(img) for ex in exclude)]
        
        self.log(f"   ✅ {len(images)} images trouvées dans les dossiers assets", "SUCCESS")
        return images
    
    def get_file_hash(self, filepath: Path) -> str:
        """Calcule le MD5 hash d'un fichier"""
        md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                md5.update(chunk)
        return md5.hexdigest()
    
    def load_existing_index(self, index_path: str = "assets_ocr_index.json") -> Dict:
        """Charge l'index OCR existant pour éviter de rescanner"""
        try:
            if Path(index_path).exists():
                with open(index_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Charger les hashes déjà traités
                    for resource_id, resource in data.get("resources", {}).items():
                        if "file_hash" in resource:
                            self.processed_hashes.add(resource["file_hash"])
                    self.log(f"   ✅ Index existant chargé: {len(data.get('resources', {}))} ressources", "SUCCESS")
                    return data
        except Exception as e:
            self.log(f"   ⚠️  Erreur chargement index: {e}", "WARNING")
        
        return {
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "resources": {}
        }
    
    def extract_zone(self, image: Image.Image, zone: str) -> Image.Image:
        """Extrait une zone spécifique de l'image"""
        width, height = image.size
        
        zones = {
            "top": (0, 0, width, int(height * 0.20)),        # 20% supérieur (titre)
            "middle": (0, int(height * 0.20), width, int(height * 0.80)),
            "bottom": (0, int(height * 0.90), width, height)  # 10% inférieur (page)
        }
        
        if zone not in zones:
            return image
        
        return image.crop(zones[zone])
    
    def ocr_image_zone(self, image: Image.Image, zone: str = "full", lang: str = "eng") -> str:
        """Effectue OCR sur une zone d'image"""
        try:
            if zone != "full":
                image = self.extract_zone(image, zone)
            
            # Configuration Tesseract
            config = '--psm 6 --oem 3'  # PSM 6 = bloc de texte uniforme
            
            text = pytesseract.image_to_string(image, lang=lang, config=config)
            return text.strip()
        except Exception as e:
            self.log(f"      ❌ Erreur OCR: {e}", "ERROR")
            return ""
    
    def extract_title(self, text: str) -> Optional[str]:
        """Extrait le titre du texte OCR"""
        if not text:
            return None
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if not lines:
            return None
        
        # Première ligne non vide = titre probable
        title = lines[0]
        
        # Nettoyer
        title = re.sub(r'[^\w\s\-\'",.()\[\]#&]', '', title)
        
        # Valider longueur
        if len(title) < 3 or len(title) > 100:
            return None
        
        return title
    
    def extract_composer(self, text: str) -> Optional[str]:
        """Extrait le compositeur du texte"""
        text_lower = text.lower()
        
        # Chercher les compositeurs connus
        for composer in self.musical_patterns["composers"]:
            if composer.lower() in text_lower:
                return composer
        
        # Patterns génériques
        patterns = [
            r'by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'composed?\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'music\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def extract_key(self, text: str) -> Optional[str]:
        """Extrait la tonalité du texte"""
        for pattern in self.musical_patterns["keys"]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return None
    
    def extract_techniques(self, text: str) -> List[str]:
        """Extrait les techniques du texte"""
        text_lower = text.lower()
        found_techniques = []
        
        for technique, keywords in self.musical_patterns["techniques"].items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_techniques.append(technique)
                    break
        
        return list(set(found_techniques))
    
    def extract_page_number(self, text: str) -> Optional[int]:
        """Extrait le numéro de page"""
        patterns = [
            r'p\.?\s*(\d+)',
            r'page\s*(\d+)',
            r'^(\d+)$',
            r'\b(\d{1,3})\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    page = int(match.group(1))
                    if 1 <= page <= 9999:
                        return page
                except ValueError:
                    pass
        
        return None
    
    def extract_track_number(self, filename: str, text: str) -> Optional[str]:
        """Extrait le numéro de track depuis le nom de fichier ou le texte"""
        # Depuis le nom de fichier
        patterns = [
            r'[Tt]rack[_\s]*(\d+)',
            r'[Pp]age[_\s]*(\d+)',
            r'(\d{3,4})',  # 3-4 chiffres
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                return match.group(1)
        
        # Depuis le texte
        track_match = re.search(r'[Tt]rack\s*[:#]?\s*(\d+)', text)
        if track_match:
            return track_match.group(1)
        
        return None
    
    def process_image(self, image_path: Path) -> Optional[Dict]:
        """Traite une image et extrait les métadonnées"""
        # Vérifier si déjà traité
        file_hash = self.get_file_hash(image_path)
        if file_hash in self.processed_hashes:
            return None  # Skip, déjà traité
        
        try:
            # Ouvrir l'image
            image = Image.open(image_path)
            
            # OCR zones ciblées
            top_text = self.ocr_image_zone(image, "top", "eng")
            middle_text = self.ocr_image_zone(image, "middle", "eng")
            bottom_text = self.ocr_image_zone(image, "bottom", "eng")
            
            # Combiner
            full_text = f"{top_text}\n{middle_text}\n{bottom_text}"
            
            # Extraire métadonnées
            title = self.extract_title(top_text)
            composer = self.extract_composer(full_text)
            key = self.extract_key(full_text)
            techniques = self.extract_techniques(full_text)
            page = self.extract_page_number(bottom_text)
            track = self.extract_track_number(image_path.name, full_text)
            
            # Calculer confiance
            confidence = 0
            if title: confidence += 40
            if composer: confidence += 20
            if key: confidence += 15
            if techniques: confidence += 15
            if page: confidence += 10
            
            # Stats
            if title: self.stats["title_found"] += 1
            if composer: self.stats["composer_found"] += 1
            if key: self.stats["key_found"] += 1
            if techniques: self.stats["technique_found"] += 1
            
            # Construire résultat
            result = {
                "file": str(image_path.relative_to(self.repo_path)),
                "file_hash": file_hash,
                "title": title or f"Page {page}" if page else image_path.stem,
                "type": "image",
                "metadata": {
                    "ocr_confidence": confidence,
                    "ocr_date": datetime.now().isoformat(),
                    "ocr_text": full_text[:500]  # Premiers 500 chars
                }
            }
            
            if composer:
                result["metadata"]["composer"] = composer
            if key:
                result["metadata"]["key"] = key
            if techniques:
                result["metadata"]["techniques"] = techniques
            if page:
                result["metadata"]["page"] = page
            if track:
                result["metadata"]["track"] = track
            
            self.processed_hashes.add(file_hash)
            return result
            
        except Exception as e:
            self.log(f"      ❌ Erreur traitement {image_path.name}: {e}", "ERROR")
            return None
    
    def scan_all_images(self, images: List[Path]) -> Dict:
        """Scanne toutes les images"""
        self.log("\n🎯 SCAN OCR EN COURS...", "INFO")
        
        # Charger index existant
        existing_index = self.load_existing_index()
        resources = existing_index.get("resources", {})
        
        total = len(images)
        processed = 0
        new_scans = 0
        
        for i, image_path in enumerate(images, 1):
            self.log(f"\n   [{i}/{total}] {image_path.name}", "INFO")
            
            result = self.process_image(image_path)
            
            if result:
                # Nouvelle ressource
                resource_id = result["file"]
                resources[resource_id] = result
                new_scans += 1
                processed += 1
                
                self.log(f"      ✅ {result['title'][:50]}", "SUCCESS")
                self.log(f"         Confiance: {result['metadata']['ocr_confidence']}%", "INFO")
            else:
                # Déjà traité
                self.log(f"      ⏭️  Déjà traité (skip)", "INFO")
        
        # Mettre à jour l'index
        self.ocr_index["resources"] = resources
        self.ocr_index["total_scanned"] = len(resources)
        self.ocr_index["new_scans"] = new_scans
        self.ocr_index["successful"] = processed
        self.ocr_index["generated_at"] = datetime.now().isoformat()
        
        return self.ocr_index
    
    def save_index(self, output_path: str = "assets_ocr_index.json"):
        """Sauvegarde l'index OCR"""
        try:
            output = Path(output_path)
            
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(self.ocr_index, f, ensure_ascii=False, indent=2)
            
            self.log(f"\n✅ INDEX OCR CRÉÉ: {output}", "SUCCESS")
            self.log(f"   📊 Total ressources: {self.ocr_index['total_scanned']}", "INFO")
            self.log(f"   🆕 Nouveaux scans: {self.ocr_index.get('new_scans', 0)}", "INFO")
            
            # Stats détaillées
            self.log(f"\n📈 STATISTIQUES:", "INFO")
            self.log(f"   Titres trouvés: {self.stats['title_found']}", "INFO")
            self.log(f"   Compositeurs: {self.stats['composer_found']}", "INFO")
            self.log(f"   Tonalités: {self.stats['key_found']}", "INFO")
            self.log(f"   Techniques: {self.stats['technique_found']}", "INFO")
            
            return True
            
        except Exception as e:
            self.log(f"\n❌ ERREUR SAUVEGARDE: {e}", "ERROR")
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='OCR Assets Scanner')
    parser.add_argument('--repo', default='.', help='Chemin du repo')
    parser.add_argument('--output', default='assets_ocr_index.json', help='Fichier de sortie')
    parser.add_argument('--force', action='store_true', help='Forcer le rescan de tout')
    args = parser.parse_args()
    
    scanner = OCRAssetsScanner(args.repo)
    
    if args.force:
        scanner.processed_hashes.clear()
        scanner.log("⚠️  Mode FORCE: Rescan de toutes les images", "WARNING")
    
    images = scanner.find_asset_images()
    
    if not images:
        scanner.log("\n⚠️  Aucune image trouvée!", "WARNING")
        return
    
    scanner.scan_all_images(images)
    success = scanner.save_index(args.output)
    
    if success:
        scanner.log("\n✅ SCAN OCR TERMINÉ!", "SUCCESS")
    else:
        scanner.log("\n❌ SCAN ÉCHOUÉ!", "ERROR")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Fusion Script V3 - Prof de Basse (Version finale avec OCR Assets)
Fusionne TOUS les index JSON incluant l'OCR des assets
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import sys

class MegaIndexFusionV3:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.mega_index = {
            "version": "3.0.0-MEGA-V3-OCR",
            "generated_at": datetime.now().isoformat(),
            "total_resources": 0,
            "sources": [],
            "resources": []
        }
        self.errors = []
        
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
        
    def find_all_json_files(self) -> List[Path]:
        """Trouve TOUS les fichiers JSON pertinents"""
        self.log("\n🔍 RECHERCHE DES INDEX JSON...", "INFO")
        
        json_files = []
        
        # Patterns de recherche (AJOUTER assets_ocr_index.json)
        patterns = [
            "**/search_index*.json",
            "**/resources_index.json",
            "**/complete-resource-map.json",
            "**/songs_index.json",
            "**/master_index.json",
            "assets_ocr_index.json",  # ← NOUVEAU
        ]
        
        for pattern in patterns:
            try:
                found = list(self.repo_path.glob(pattern))
                
                # Exclure le dossier search_system (ancien système)
                found = [f for f in found if "search_system" not in str(f)]
                
                if found:
                    self.log(f"   ✓ Pattern '{pattern}': {len(found)} fichiers", "SUCCESS")
                    json_files.extend(found)
                else:
                    self.log(f"   ○ Pattern '{pattern}': 0 fichiers", "WARNING")
            except Exception as e:
                self.log(f"   ✗ Erreur pattern '{pattern}': {e}", "ERROR")
        
        # Dédupliquer
        json_files = list(set(json_files))
        
        if json_files:
            self.log(f"\n📊 Total JSON trouvés: {len(json_files)}", "SUCCESS")
        else:
            self.log(f"\n⚠️  AUCUN fichier JSON trouvé!", "WARNING")
            self.log(f"   Cherché dans: {self.repo_path.absolute()}", "INFO")
            
        return json_files
    
    def load_json_safe(self, filepath: Path) -> Dict:
        """Charge un JSON en sécurité avec gestion d'erreurs"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.log(f"   ✓ {filepath.name}", "SUCCESS")
                return data
        except json.JSONDecodeError as e:
            error_msg = f"JSON invalide dans {filepath.name}: {e}"
            self.log(f"   ✗ {error_msg}", "ERROR")
            self.errors.append(error_msg)
            return {}
        except Exception as e:
            error_msg = f"Erreur lecture {filepath.name}: {e}"
            self.log(f"   ✗ {error_msg}", "ERROR")
            self.errors.append(error_msg)
            return {}
    
    def normalize_resource(self, resource: Dict, source: str, source_path: Path = None) -> Dict:
        """Normalise une ressource au format standard"""
        
        # Extraire l'ID
        resource_id = resource.get("id", resource.get("file", resource.get("path", "")))
        
        if not resource_id:
            # Générer un ID temporaire
            resource_id = f"unknown_{hash(str(resource))}"
        
        # Format standard
        normalized = {
            "id": str(resource_id),
            "title": str(resource.get("title", resource.get("name", "Sans titre"))),
            "type": self.detect_type(resource),
            "url": self.build_url(resource, source_path),
            "source": source,
            "metadata": {}
        }
        
        # Ajouter métadonnées
        metadata_fields = [
            "techniques", "styles", "level", "tempo", "key", "composer",
            "page", "track", "pattern", "duration", "tags", "description",
            "ocr_text", "excerpt", "content", "path", "size",
            "ocr_confidence", "ocr_date", "file_hash"  # ← NOUVEAU pour OCR
        ]
        
        for field in metadata_fields:
            if field in resource and resource[field]:
                normalized["metadata"][field] = resource[field]
            # Chercher aussi dans resource.metadata
            elif "metadata" in resource and field in resource["metadata"]:
                if resource["metadata"][field]:
                    normalized["metadata"][field] = resource["metadata"][field]
        
        # Texte de recherche
        search_parts = [
            normalized["title"],
            normalized.get("metadata", {}).get("composer", ""),
            normalized.get("metadata", {}).get("ocr_text", ""),
            normalized.get("metadata", {}).get("content", ""),
            normalized.get("metadata", {}).get("description", ""),
        ]
        
        # Ajouter styles et techniques
        if normalized.get("metadata", {}).get("styles"):
            search_parts.extend(normalized["metadata"]["styles"])
        if normalized.get("metadata", {}).get("techniques"):
            search_parts.extend(normalized["metadata"]["techniques"])
        
        normalized["search_text"] = " ".join(
            str(part).lower() for part in search_parts if part
        )
        
        return normalized
    
    def detect_type(self, resource: Dict) -> str:
        """Détecte le type de ressource"""
        # Essayer plusieurs clés
        file = str(resource.get("file", resource.get("path", resource.get("id", ""))))
        resource_type = resource.get("type", "")
        
        # Si type déjà défini, l'utiliser
        if resource_type:
            return resource_type
        
        # Sinon détecter depuis le fichier
        file_lower = file.lower()
        if ".mp3" in file_lower:
            return "mp3"
        elif ".pdf" in file_lower:
            return "pdf"
        elif ".png" in file_lower or ".jpg" in file_lower or ".jpeg" in file_lower:
            return "image"
        elif ".html" in file_lower:
            return "html"
        elif ".json" in file_lower:
            return "data"
        else:
            return "other"
    
    def build_url(self, resource: Dict, source_path: Path = None) -> str:
        """Construit l'URL complète GitHub Pages"""
        base_url = "https://11drumboy11.github.io/Prof-de-basse-V2/"
        
        # Chercher le chemin - essayer plusieurs clés
        path = resource.get("url", "")
        if not path:
            path = resource.get("file", "")
        if not path:
            path = resource.get("path", "")
        if not path:
            path = resource.get("id", "")
        
        if not path:
            return base_url
        
        # Si déjà une URL complète, la retourner
        if str(path).startswith("http"):
            return str(path)
        
        # Nettoyer le chemin
        path = str(path)
        
        # Enlever les préfixes relatifs
        path = path.lstrip("/").lstrip("./")
        
        # CORRECTION INTELLIGENTE : Si le chemin semble incomplet
        if source_path is not None and "/" not in path:
            source_dir = source_path.parent
            
            # Chercher un dossier "assets" ou utiliser le dossier parent
            assets_dir = source_dir / "assets"
            if assets_dir.exists():
                full_path = assets_dir / path
            else:
                full_path = source_dir / path
            
            # Convertir en chemin relatif depuis la racine du repo
            try:
                rel_path = full_path.relative_to(self.repo_path)
                path = str(rel_path)
            except ValueError:
                pass
        
        # Encoder les espaces et caractères spéciaux pour URL
        # NOTE: Ne pas encoder ' car GitHub Pages l'accepte tel quel
        parts = path.split("/")
        encoded_parts = []
        for part in parts:
            encoded_part = part.replace(" ", "%20").replace("&", "%26")
            encoded_parts.append(encoded_part)
        
        path = "/".join(encoded_parts)
        
        return base_url + path
    
    def merge_resources(self, json_files: List[Path]) -> List[Dict]:
        """Fusionne toutes les ressources"""
        self.log("\n🔥 FUSION DES RESSOURCES...", "INFO")
        
        all_resources = []
        seen_ids = set()
        
        for json_file in json_files:
            data = self.load_json_safe(json_file)
            
            if not data:
                continue
            
            source_name = json_file.name
            self.mega_index["sources"].append(str(json_file))
            
            # Extraire les ressources selon le format
            resources = []
            
            if "resources" in data:
                resources = data["resources"]
                # Si c'est un dict, le convertir en liste
                if isinstance(resources, dict):
                    resources = list(resources.values())
            elif "songs" in data:
                # Format du convertisseur V4 (songs_index.json)
                self.log(f"   🎵 Format convertisseur V4 détecté", "INFO")
                for song in data.get("songs", []):
                    # Convertir le format V4 vers format standard
                    normalized_song = {
                        "id": song.get("page_url", "").split("/")[-1],  # Extraire nom fichier
                        "file": song.get("page_url", ""),
                        "title": song.get("title", ""),
                        "type": "image",
                        "metadata": {
                            "key": song.get("tonalite"),
                            "composer": song.get("composer"),
                            "track": song.get("track_number"),
                            "page": song.get("page_number"),
                            "techniques": song.get("techniques", []),
                            "ocr_text": song.get("ocr_raw", ""),
                            "ocr_confidence": song.get("confidence"),
                            "zones": song.get("zones", {})
                        }
                    }
                    # Ajouter URL MP3 si présent
                    if song.get("mp3_url"):
                        normalized_song["metadata"]["mp3_url"] = song.get("mp3_url")
                    
                    resources.append(normalized_song)
            elif isinstance(data, list):
                resources = data
            elif isinstance(data, dict):
                # Peut-être un songs_index ou assets_ocr_index
                for key, value in data.items():
                    if isinstance(value, dict):
                        if "id" not in value:
                            value["id"] = key
                        resources.append(value)
            
            # Normaliser chaque ressource
            for resource in resources:
                try:
                    if isinstance(resource, dict):
                        normalized = self.normalize_resource(resource, source_name, json_file)
                        
                        # Éviter doublons (utiliser file_hash si disponible, sinon id)
                        resource_hash = normalized.get("metadata", {}).get("file_hash")
                        resource_id = resource_hash if resource_hash else normalized["id"]
                        
                        if resource_id not in seen_ids:
                            all_resources.append(normalized)
                            seen_ids.add(resource_id)
                        else:
                            # Doublon détecté, mais si l'OCR a plus d'infos, mettre à jour
                            if source_name == "assets_ocr_index.json":
                                # Trouver la ressource existante
                                for i, existing in enumerate(all_resources):
                                    if existing["id"] == normalized["id"]:
                                        # Fusionner les métadonnées
                                        existing["metadata"].update(normalized["metadata"])
                                        if normalized.get("title") and normalized["title"] != "Sans titre":
                                            existing["title"] = normalized["title"]
                                        break
                                
                except Exception as e:
                    error_msg = f"Erreur normalisation ressource dans {source_name}: {e}"
                    self.log(f"   ⚠  {error_msg}", "WARNING")
                    self.errors.append(error_msg)
        
        return all_resources
    
    def create_mega_index(self) -> Dict:
        """Crée le MEGA index complet"""
        self.log("\n" + "="*60, "INFO")
        self.log("🚀 MEGA INDEX FUSION V3 (avec OCR) - Prof de Basse", "INFO")
        self.log("="*60, "INFO")
        
        json_files = self.find_all_json_files()
        
        if not json_files:
            self.log("\n❌ ERREUR: Aucun fichier JSON trouvé!", "ERROR")
            return self.mega_index
        
        resources = self.merge_resources(json_files)
        
        self.mega_index["resources"] = resources
        self.mega_index["total_resources"] = len(resources)
        
        # Statistiques
        types_count = {}
        ocr_count = 0
        
        for r in resources:
            t = r["type"]
            types_count[t] = types_count.get(t, 0) + 1
            
            # Compter ressources avec OCR
            if r.get("metadata", {}).get("ocr_confidence"):
                ocr_count += 1
        
        self.mega_index["statistics"] = {
            "by_type": types_count,
            "sources_merged": len(self.mega_index["sources"]),
            "with_ocr": ocr_count
        }
        
        return self.mega_index
    
    def save_mega_index(self, output_path: str = "mega-search-index.json"):
        """Sauvegarde le MEGA index"""
        try:
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(self.mega_index, f, ensure_ascii=False, indent=2)
            
            self.log(f"\n✅ MEGA INDEX CRÉÉ: {output}", "SUCCESS")
            self.log(f"   📊 Total: {self.mega_index['total_resources']} ressources", "INFO")
            self.log(f"   📚 Sources: {self.mega_index['statistics']['sources_merged']} fichiers", "INFO")
            self.log(f"   🔍 Avec OCR: {self.mega_index['statistics']['with_ocr']} ressources", "SUCCESS")
            
            if self.mega_index["statistics"]["by_type"]:
                self.log(f"\n📈 Par type:", "INFO")
                for type_name, count in sorted(self.mega_index["statistics"]["by_type"].items()):
                    self.log(f"   {type_name}: {count}", "INFO")
            
            # Afficher les erreurs si présentes
            if self.errors:
                self.log(f"\n⚠️  {len(self.errors)} avertissements:", "WARNING")
                for error in self.errors[:5]:
                    self.log(f"   - {error}", "WARNING")
                if len(self.errors) > 5:
                    self.log(f"   ... et {len(self.errors) - 5} autres", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"\n❌ ERREUR SAUVEGARDE: {e}", "ERROR")
            return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fusion MEGA Index V3 (avec OCR)')
    parser.add_argument('--repo', default='.', help='Chemin du repo')
    parser.add_argument('--output', default='mega-search-index.json', help='Fichier de sortie')
    args = parser.parse_args()
    
    fusion = MegaIndexFusionV3(args.repo)
    fusion.create_mega_index()
    success = fusion.save_mega_index(args.output)
    
    if success:
        fusion.log("\n✅ FUSION TERMINÉE!", "SUCCESS")
        sys.exit(0)
    else:
        fusion.log("\n❌ FUSION ÉCHOUÉE!", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()#!/usr/bin/env python3
"""
Fusion Script V3 - Prof de Basse (Version finale avec OCR Assets)
Fusionne TOUS les index JSON incluant l'OCR des assets
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import sys

class MegaIndexFusionV3:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.mega_index = {
            "version": "3.0.0-MEGA-V3-OCR",
            "generated_at": datetime.now().isoformat(),
            "total_resources": 0,
            "sources": [],
            "resources": []
        }
        self.errors = []
        
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
        
    def find_all_json_files(self) -> List[Path]:
        """Trouve TOUS les fichiers JSON pertinents"""
        self.log("\n🔍 RECHERCHE DES INDEX JSON...", "INFO")
        
        json_files = []
        
        # Patterns de recherche (AJOUTER assets_ocr_index.json)
        patterns = [
            "**/search_index*.json",
            "**/resources_index.json",
            "**/complete-resource-map.json",
            "**/songs_index.json",
            "**/master_index.json",
            "assets_ocr_index.json",  # ← NOUVEAU
        ]
        
        for pattern in patterns:
            try:
                found = list(self.repo_path.glob(pattern))
                
                # Exclure le dossier search_system (ancien système)
                found = [f for f in found if "search_system" not in str(f)]
                
                if found:
                    self.log(f"   ✓ Pattern '{pattern}': {len(found)} fichiers", "SUCCESS")
                    json_files.extend(found)
                else:
                    self.log(f"   ○ Pattern '{pattern}': 0 fichiers", "WARNING")
            except Exception as e:
                self.log(f"   ✗ Erreur pattern '{pattern}': {e}", "ERROR")
        
        # Dédupliquer
        json_files = list(set(json_files))
        
        if json_files:
            self.log(f"\n📊 Total JSON trouvés: {len(json_files)}", "SUCCESS")
        else:
            self.log(f"\n⚠️  AUCUN fichier JSON trouvé!", "WARNING")
            self.log(f"   Cherché dans: {self.repo_path.absolute()}", "INFO")
            
        return json_files
    
    def load_json_safe(self, filepath: Path) -> Dict:
        """Charge un JSON en sécurité avec gestion d'erreurs"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.log(f"   ✓ {filepath.name}", "SUCCESS")
                return data
        except json.JSONDecodeError as e:
            error_msg = f"JSON invalide dans {filepath.name}: {e}"
            self.log(f"   ✗ {error_msg}", "ERROR")
            self.errors.append(error_msg)
            return {}
        except Exception as e:
            error_msg = f"Erreur lecture {filepath.name}: {e}"
            self.log(f"   ✗ {error_msg}", "ERROR")
            self.errors.append(error_msg)
            return {}
    
    def normalize_resource(self, resource: Dict, source: str, source_path: Path = None) -> Dict:
        """Normalise une ressource au format standard"""
        
        # Extraire l'ID
        resource_id = resource.get("id", resource.get("file", resource.get("path", "")))
        
        if not resource_id:
            # Générer un ID temporaire
            resource_id = f"unknown_{hash(str(resource))}"
        
        # Format standard
        normalized = {
            "id": str(resource_id),
            "title": str(resource.get("title", resource.get("name", "Sans titre"))),
            "type": self.detect_type(resource),
            "url": self.build_url(resource, source_path),
            "source": source,
            "metadata": {}
        }
        
        # Ajouter métadonnées
        metadata_fields = [
            "techniques", "styles", "level", "tempo", "key", "composer",
            "page", "track", "pattern", "duration", "tags", "description",
            "ocr_text", "excerpt", "content", "path", "size",
            "ocr_confidence", "ocr_date", "file_hash"  # ← NOUVEAU pour OCR
        ]
        
        for field in metadata_fields:
            if field in resource and resource[field]:
                normalized["metadata"][field] = resource[field]
            # Chercher aussi dans resource.metadata
            elif "metadata" in resource and field in resource["metadata"]:
                if resource["metadata"][field]:
                    normalized["metadata"][field] = resource["metadata"][field]
        
        # Texte de recherche
        search_parts = [
            normalized["title"],
            normalized.get("metadata", {}).get("composer", ""),
            normalized.get("metadata", {}).get("ocr_text", ""),
            normalized.get("metadata", {}).get("content", ""),
            normalized.get("metadata", {}).get("description", ""),
        ]
        
        # Ajouter styles et techniques
        if normalized.get("metadata", {}).get("styles"):
            search_parts.extend(normalized["metadata"]["styles"])
        if normalized.get("metadata", {}).get("techniques"):
            search_parts.extend(normalized["metadata"]["techniques"])
        
        normalized["search_text"] = " ".join(
            str(part).lower() for part in search_parts if part
        )
        
        return normalized
    
    def detect_type(self, resource: Dict) -> str:
        """Détecte le type de ressource"""
        # Essayer plusieurs clés
        file = str(resource.get("file", resource.get("path", resource.get("id", ""))))
        resource_type = resource.get("type", "")
        
        # Si type déjà défini, l'utiliser
        if resource_type:
            return resource_type
        
        # Sinon détecter depuis le fichier
        file_lower = file.lower()
        if ".mp3" in file_lower:
            return "mp3"
        elif ".pdf" in file_lower:
            return "pdf"
        elif ".png" in file_lower or ".jpg" in file_lower or ".jpeg" in file_lower:
            return "image"
        elif ".html" in file_lower:
            return "html"
        elif ".json" in file_lower:
            return "data"
        else:
            return "other"
    
    def build_url(self, resource: Dict, source_path: Path = None) -> str:
        """Construit l'URL complète GitHub Pages"""
        base_url = "https://11drumboy11.github.io/Prof-de-basse-V2/"
        
        # Chercher le chemin - essayer plusieurs clés
        path = resource.get("url", "")
        if not path:
            path = resource.get("file", "")
        if not path:
            path = resource.get("path", "")
        if not path:
            path = resource.get("id", "")
        
        if not path:
            return base_url
        
        # Si déjà une URL complète, la retourner
        if str(path).startswith("http"):
            return str(path)
        
        # Nettoyer le chemin
        path = str(path)
        
        # Enlever les préfixes relatifs
        path = path.lstrip("/").lstrip("./")
        
        # CORRECTION INTELLIGENTE : Si le chemin semble incomplet
        if source_path is not None and "/" not in path:
            source_dir = source_path.parent
            
            # Chercher un dossier "assets" ou utiliser le dossier parent
            assets_dir = source_dir / "assets"
            if assets_dir.exists():
                full_path = assets_dir / path
            else:
                full_path = source_dir / path
            
            # Convertir en chemin relatif depuis la racine du repo
            try:
                rel_path = full_path.relative_to(self.repo_path)
                path = str(rel_path)
            except ValueError:
                pass
        
        # Encoder les espaces et caractères spéciaux pour URL
        # NOTE: Ne pas encoder ' car GitHub Pages l'accepte tel quel
        parts = path.split("/")
        encoded_parts = []
        for part in parts:
            encoded_part = part.replace(" ", "%20").replace("&", "%26")
            encoded_parts.append(encoded_part)
        
        path = "/".join(encoded_parts)
        
        return base_url + path
    
    def merge_resources(self, json_files: List[Path]) -> List[Dict]:
        """Fusionne toutes les ressources"""
        self.log("\n🔥 FUSION DES RESSOURCES...", "INFO")
        
        all_resources = []
        seen_ids = set()
        
        for json_file in json_files:
            data = self.load_json_safe(json_file)
            
            if not data:
                continue
            
            source_name = json_file.name
            self.mega_index["sources"].append(str(json_file))
            
            # Extraire les ressources selon le format
            resources = []
            
            if "resources" in data:
                resources = data["resources"]
                # Si c'est un dict, le convertir en liste
                if isinstance(resources, dict):
                    resources = list(resources.values())
            elif "songs" in data:
                # Format du convertisseur V4 (songs_index.json)
                self.log(f"   🎵 Format convertisseur V4 détecté", "INFO")
                for song in data.get("songs", []):
                    # Convertir le format V4 vers format standard
                    normalized_song = {
                        "id": song.get("page_url", "").split("/")[-1],  # Extraire nom fichier
                        "file": song.get("page_url", ""),
                        "title": song.get("title", ""),
                        "type": "image",
                        "metadata": {
                            "key": song.get("tonalite"),
                            "composer": song.get("composer"),
                            "track": song.get("track_number"),
                            "page": song.get("page_number"),
                            "techniques": song.get("techniques", []),
                            "ocr_text": song.get("ocr_raw", ""),
                            "ocr_confidence": song.get("confidence"),
                            "zones": song.get("zones", {})
                        }
                    }
                    # Ajouter URL MP3 si présent
                    if song.get("mp3_url"):
                        normalized_song["metadata"]["mp3_url"] = song.get("mp3_url")
                    
                    resources.append(normalized_song)
            elif isinstance(data, list):
                resources = data
            elif isinstance(data, dict):
                # Peut-être un songs_index ou assets_ocr_index
                for key, value in data.items():
                    if isinstance(value, dict):
                        if "id" not in value:
                            value["id"] = key
                        resources.append(value)
            
            # Normaliser chaque ressource
            for resource in resources:
                try:
                    if isinstance(resource, dict):
                        normalized = self.normalize_resource(resource, source_name, json_file)
                        
                        # Éviter doublons (utiliser file_hash si disponible, sinon id)
                        resource_hash = normalized.get("metadata", {}).get("file_hash")
                        resource_id = resource_hash if resource_hash else normalized["id"]
                        
                        if resource_id not in seen_ids:
                            all_resources.append(normalized)
                            seen_ids.add(resource_id)
                        else:
                            # Doublon détecté, mais si l'OCR a plus d'infos, mettre à jour
                            if source_name == "assets_ocr_index.json":
                                # Trouver la ressource existante
                                for i, existing in enumerate(all_resources):
                                    if existing["id"] == normalized["id"]:
                                        # Fusionner les métadonnées
                                        existing["metadata"].update(normalized["metadata"])
                                        if normalized.get("title") and normalized["title"] != "Sans titre":
                                            existing["title"] = normalized["title"]
                                        break
                                
                except Exception as e:
                    error_msg = f"Erreur normalisation ressource dans {source_name}: {e}"
                    self.log(f"   ⚠  {error_msg}", "WARNING")
                    self.errors.append(error_msg)
        
        return all_resources
    
    def create_mega_index(self) -> Dict:
        """Crée le MEGA index complet"""
        self.log("\n" + "="*60, "INFO")
        self.log("🚀 MEGA INDEX FUSION V3 (avec OCR) - Prof de Basse", "INFO")
        self.log("="*60, "INFO")
        
        json_files = self.find_all_json_files()
        
        if not json_files:
            self.log("\n❌ ERREUR: Aucun fichier JSON trouvé!", "ERROR")
            return self.mega_index
        
        resources = self.merge_resources(json_files)
        
        self.mega_index["resources"] = resources
        self.mega_index["total_resources"] = len(resources)
        
        # Statistiques
        types_count = {}
        ocr_count = 0
        
        for r in resources:
            t = r["type"]
            types_count[t] = types_count.get(t, 0) + 1
            
            # Compter ressources avec OCR
            if r.get("metadata", {}).get("ocr_confidence"):
                ocr_count += 1
        
        self.mega_index["statistics"] = {
            "by_type": types_count,
            "sources_merged": len(self.mega_index["sources"]),
            "with_ocr": ocr_count
        }
        
        return self.mega_index
    
    def save_mega_index(self, output_path: str = "mega-search-index.json"):
        """Sauvegarde le MEGA index"""
        try:
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(self.mega_index, f, ensure_ascii=False, indent=2)
            
            self.log(f"\n✅ MEGA INDEX CRÉÉ: {output}", "SUCCESS")
            self.log(f"   📊 Total: {self.mega_index['total_resources']} ressources", "INFO")
            self.log(f"   📚 Sources: {self.mega_index['statistics']['sources_merged']} fichiers", "INFO")
            self.log(f"   🔍 Avec OCR: {self.mega_index['statistics']['with_ocr']} ressources", "SUCCESS")
            
            if self.mega_index["statistics"]["by_type"]:
                self.log(f"\n📈 Par type:", "INFO")
                for type_name, count in sorted(self.mega_index["statistics"]["by_type"].items()):
                    self.log(f"   {type_name}: {count}", "INFO")
            
            # Afficher les erreurs si présentes
            if self.errors:
                self.log(f"\n⚠️  {len(self.errors)} avertissements:", "WARNING")
                for error in self.errors[:5]:
                    self.log(f"   - {error}", "WARNING")
                if len(self.errors) > 5:
                    self.log(f"   ... et {len(self.errors) - 5} autres", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"\n❌ ERREUR SAUVEGARDE: {e}", "ERROR")
            return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fusion MEGA Index V3 (avec OCR)')
    parser.add_argument('--repo', default='.', help='Chemin du repo')
    parser.add_argument('--output', default='mega-search-index.json', help='Fichier de sortie')
    args = parser.parse_args()
    
    fusion = MegaIndexFusionV3(args.repo)
    fusion.create_mega_index()
    success = fusion.save_mega_index(args.output)
    
    if success:
        fusion.log("\n✅ FUSION TERMINÉE!", "SUCCESS")
        sys.exit(0)
    else:
        fusion.log("\n❌ FUSION ÉCHOUÉE!", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()

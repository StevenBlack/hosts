#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hosts Generator
Generador de archivos hosts personalizados con descarga de diferentes fuentes.
"""

import os
import sys
import json
import requests
import webview
import threading
import time
import concurrent.futures
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

class HostsGenerator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "data"
        self.output_dir = self.data_dir / "output"
        self.sources_dir = self.data_dir / "hosts_sources"
        self.lang_dir = self.base_dir / "lang"
        
        # URLs de fuentes de hosts (directas desde GitHub)
        self.sources = {
            "base": {
                "url": "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",
                "description": "Base hosts (adware + malware)"
            },
            "fakenews": {
                "url": "https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews/hosts",
                "description": "Fake news sites"
            },
            "gambling": {
                "url": "https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/gambling/hosts",
                "description": "Gambling sites"
            },
            "porn": {
                "url": "https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/porn/hosts",
                "description": "Adult content sites"
            },
            "social": {
                "url": "https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/social/hosts",
                "description": "Social media sites"
            }
        }
        
        # Estado de descarga
        self.download_status = {
            "downloading": False,
            "progress": 0,
            "current_source": "",
            "message": ""
        }
        
        # Crear directorios necesarios
        self.ensure_directories()
    
    def ensure_directories(self):
        """Crear directorios necesarios"""
        self.data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        self.sources_dir.mkdir(exist_ok=True)
        self.lang_dir.mkdir(exist_ok=True)
    
    def get_download_status(self):
        """Obtener estado de descarga"""
        return self.download_status
    
    def check_sources_exist(self):
        """Verificar qué fuentes existen localmente"""
        existing = []
        missing = []
        
        for name in self.sources.keys():
            file_path = self.sources_dir / f"{name}.txt"
            if file_path.exists():
                existing.append(name)
            else:
                missing.append(name)
        
        return {
            "existing": len(existing),
            "total": len(self.sources),
            "missing": missing,
            "all_exist": len(missing) == 0
        }
    
    def download_sources_async(self):
        """Descargar fuentes en hilo separado"""
        thread = threading.Thread(target=self.download_sources)
        thread.daemon = True
        thread.start()
        return {"success": True, "message": "Descarga iniciada"}
    
    def download_sources(self):
        """Descargar todas las fuentes faltantes"""
        try:
            self.download_status["downloading"] = True
            self.download_status["progress"] = 0
            self.download_status["message"] = "Iniciando descarga..."
            
            # Verificar qué fuentes faltan
            status = self.check_sources_exist()
            if status["all_exist"]:
                self.download_status["message"] = "Todas las fuentes ya están disponibles"
                self.download_status["progress"] = 100
                return
            
            # Descargar solo las fuentes faltantes
            sources_to_download = [(name, info) for name, info in self.sources.items() 
                                 if name in status["missing"]]
            self._download_sources_list(sources_to_download)
            
        except Exception as e:
            self.download_status["message"] = f"Error general: {str(e)}"
        
        finally:
            self.download_status["downloading"] = False
    
    def get_available_extensions(self):
        """Obtener extensiones disponibles (incluyendo base)"""
        extensions = []
        for name, info in self.sources.items():
            file_path = self.sources_dir / f"{name}.txt"
            extensions.append({
                "name": name,
                "description": info["description"],
                "available": file_path.exists(),
                "size": file_path.stat().st_size if file_path.exists() else 0,
                "is_base": name == "base"
            })
        
        return extensions
    
    def get_available_languages(self):
        """Obtener idiomas disponibles"""
        languages = []
        if self.lang_dir.exists():
            for lang_file in self.lang_dir.glob("*.json"):
                lang_code = lang_file.stem
                languages.append({
                    "code": lang_code,
                    "name": "Español" if lang_code == "es" else "English" if lang_code == "en" else lang_code.upper()
                })
        return languages
    
    def get_language_strings(self, lang_code="es"):
        """Obtener strings de idioma"""
        lang_file = self.lang_dir / f"{lang_code}.json"
        if lang_file.exists():
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error cargando idioma {lang_code}: {e}")
        
        # Fallback a español si no se encuentra el idioma
        fallback_file = self.lang_dir / "es.json"
        if fallback_file.exists():
            try:
                with open(fallback_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Fallback hardcoded si no hay archivos de idioma
        return {
            "app_title": "🛡️ Generador de Hosts",
            "app_subtitle": "Generador de archivos hosts personalizados",
            "error": "Error"
        }

    def update_sources_async(self):
        """Actualizar fuentes existentes en hilo separado"""
        thread = threading.Thread(target=self.update_sources)
        thread.daemon = True
        thread.start()
        return {"success": True, "message": "Actualización iniciada"}
    
    def update_sources(self):
        """Actualizar todas las fuentes existentes"""
        try:
            self.download_status["downloading"] = True
            self.download_status["progress"] = 0
            self.download_status["message"] = "Iniciando actualización..."
            
            # Descargar todas las fuentes (actualizar)
            sources_to_download = list(self.sources.items())
            self._download_sources_list(sources_to_download)
            
        except Exception as e:
            self.download_status["message"] = f"Error general: {str(e)}"
        
        finally:
            self.download_status["downloading"] = False
    
    def _download_sources_list(self, sources_to_download):
        """Método auxiliar para descargar una lista de fuentes"""
        total_sources = len(sources_to_download)
        completed = 0
        
        def download_single_source(source_data):
            nonlocal completed
            name, source_info = source_data
            
            try:
                self.download_status["current_source"] = f"Descargando {name}..."
                print(f"Descargando {name} desde {source_info['url']}")
                
                # Configuración optimizada para requests
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                response = session.get(
                    source_info['url'], 
                    timeout=45,
                    stream=True,  # Para archivos grandes
                    allow_redirects=True
                )
                response.raise_for_status()
                
                file_path = self.sources_dir / f"{name}.txt"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                completed += 1
                progress = int((completed / total_sources) * 100)
                self.download_status["progress"] = progress
                
                print(f"✓ {name} descargado exitosamente ({completed}/{total_sources})")
                return True
                
            except Exception as e:
                print(f"✗ Error descargando {name}: {e}")
                self.download_status["message"] = f"Error en {name}: {str(e)}"
                return False
        
        # Descargas concurrentes (máximo 5 simultáneas)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(download_single_source, source) for source in sources_to_download]
            
            # Esperar a que todas terminen
            concurrent.futures.wait(futures)
        
        self.download_status["progress"] = 100
        self.download_status["current_source"] = "Descarga completada"
        self.download_status["message"] = f"Descargadas {completed}/{total_sources} fuentes exitosamente"
    
    def generate_hosts_file(self, extensions):
        """Generar archivo hosts personalizado"""
        try:
            # Verificar que la base existe
            base_file = self.sources_dir / "base.txt"
            if not base_file.exists():
                return {
                    "success": False,
                    "message": "Archivo base no encontrado. Descarga las fuentes primero."
                }
            
            # Generar nombre único
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if extensions:
                ext_suffix = "_" + "_".join(sorted(extensions))
            else:
                ext_suffix = "_base"
            
            output_filename = f"hosts_{timestamp}{ext_suffix}"
            output_path = self.output_dir / output_filename
            
            # Leer archivo base
            print(f"Leyendo archivo base: {base_file}")
            with open(base_file, 'r', encoding='utf-8') as f:
                base_content = f.read()
            
            # Combinar con extensiones
            combined_content = base_content
            extension_stats = []
            
            for ext in extensions:
                if ext == "base":  # Skip base ya que siempre se incluye
                    continue
                    
                ext_file = self.sources_dir / f"{ext}.txt"
                if ext_file.exists():
                    print(f"Agregando extensión: {ext}")
                    with open(ext_file, 'r', encoding='utf-8') as f:
                        ext_content = f.read()
                    
                    # Agregar separador y contenido
                    combined_content += f"\n\n# === {ext.upper()} EXTENSION ===\n"
                    combined_content += ext_content
                    
                    # Estadísticas
                    ext_lines = len(ext_content.splitlines())
                    extension_stats.append(f"{ext}: {ext_lines:,} líneas")
                else:
                    print(f"Advertencia: Extensión {ext} no encontrada")
            
            # Escribir archivo final
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(combined_content)
            
            # Estadísticas finales
            file_size = output_path.stat().st_size
            total_lines = len(combined_content.splitlines())
            
            stats_message = f"Archivo generado exitosamente\n"
            stats_message += f"Nombre: {output_filename}\n"
            stats_message += f"Tamaño: {file_size:,} bytes\n"
            stats_message += f"Líneas totales: {total_lines:,}\n"
            if extension_stats:
                stats_message += f"Extensiones: {', '.join(extension_stats)}"
            else:
                stats_message += "Extensiones: Solo base (adware + malware)"
            
            return {
                "success": True,
                "message": stats_message,
                "filename": output_filename,
                "path": str(output_path),
                "size": file_size,
                "lines": total_lines
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error generando archivo: {str(e)}"
            }
    
    def open_output_folder(self):
        """Abrir carpeta de salida"""
        try:
            if sys.platform == "win32":
                os.startfile(self.output_dir)
            elif sys.platform == "darwin":
                os.system(f"open '{self.output_dir}'")
            else:
                os.system(f"xdg-open '{self.output_dir}'")
            return {"success": True, "message": "Carpeta abierta"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_output_files(self):
        """Obtener lista de archivos generados"""
        files = []
        if self.output_dir.exists():
            for file_path in self.output_dir.glob("hosts_*"):
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        "name": file_path.name,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    })
        
        return sorted(files, key=lambda x: x["modified"], reverse=True)

def main():
    """Función principal"""
    print("🛡️ Iniciando Hosts Generator...")
    
    # Crear instancia de la aplicación
    app = HostsGenerator()
    
    # Verificar archivo HTML
    html_path = app.base_dir / "ui.html"
    if not html_path.exists():
        print(f"Error: No se encontró ui.html en {html_path}")
        input("Presiona Enter para salir...")
        return
    
    print(f"📁 Directorio base: {app.base_dir}")
    print(f"📁 Directorio de datos: {app.data_dir}")
    print(f"📁 Directorio de salida: {app.output_dir}")
    
    # Verificar estado de fuentes
    sources_status = app.check_sources_exist()
    if sources_status["all_exist"]:
        print(f"✅ Todas las fuentes están disponibles ({sources_status['existing']}/{sources_status['total']})")
    else:
        print(f"⚠️ Faltan {len(sources_status['missing'])} fuentes de {sources_status['total']}")
        print(f"   Faltantes: {', '.join(sources_status['missing'])}")
    
    # Crear ventana de la aplicación
    print("🚀 Iniciando interfaz web...")
    
    webview.create_window(
        title="🛡️ Hosts Generator",
        url=str(html_path),
        js_api=app,
        width=1024,      # Cambia este valor para el ancho (actualmente 1024)
        height=900,      # Cambia este valor para el alto (actualmente 750)
        min_size=(800, 600),  # Tamaño mínimo (actualmente 700x500)
        resizable=True
    )
    
    webview.start(debug=False)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Aplicación cerrada por el usuario")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        input("Presiona Enter para salir...")
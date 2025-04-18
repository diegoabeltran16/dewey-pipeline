# main.py

"""
Script principal del Dewey Pipeline 🧠📘
Procesa todos los archivos PDF dentro de /input/** y genera salidas en /output
"""

import os
from pathlib import Path

from src.parser import extract_text
from src.cleaner import limpiar_texto_completo
from src.classifier import clasificar_documento
from src.exporter import exportar_archivos
from src.logger import log_evento
from src.validator import validar_documento

# Forzar idioma visual en consola
os.environ["LANG"] = "es"

INPUT_DIR = "input"

def main():
    print("🚀 Iniciando Dewey Pipeline...")

    archivos_pdf = list(Path(INPUT_DIR).rglob("*.pdf"))
    if not archivos_pdf:
        print("⚠️  No se encontraron archivos PDF en la carpeta 'input/'")
        return

    print(f"🔍 Se encontraron {len(archivos_pdf)} archivos para procesar.")

    resumen = {
        "procesados": 0,
        "omitidos": 0,
        "errores": 0
    }

    for archivo in archivos_pdf:
        ruta = str(archivo)
        nombre_archivo = archivo.stem
        tipo = Path(archivo).parent.name  # Carpeta como tipo (Book, Essay, etc.)

        try:
            # 1️⃣ Extraer texto
            texto_crudo = extract_text(ruta)
            log_evento("procesar", archivo=ruta)

            # 2️⃣ Limpiar texto
            texto_limpio = limpiar_texto_completo(texto_crudo, modo_md=True)

            # 3️⃣ Clasificar
            resultado = clasificar_documento(texto_limpio)
            categoria = resultado.get("categoria")
            dewey = resultado.get("dewey")
            titulo = resultado.get("titulo")
            autor = resultado.get("autor")

            # 4️⃣ Validar documento completo
            es_valido, info = validar_documento(texto_limpio, titulo, autor)
            if not es_valido:
                log_evento("warning_meta", archivo=ruta, nivel="WARNING")
                print(f"⚠️  Documento omitido: {info.get('razones', [])}")
                resumen["omitidos"] += 1
                continue

            # 5️⃣ Exportar
            exportar_archivos(tipo, titulo, texto_limpio, categoria, dewey, autor)

            # 6️⃣ Logging visual + estructurado
            log_evento("clasificado", archivo=ruta, categoria=categoria, dewey=dewey)
            log_evento("export_ok", archivo=ruta, categoria=categoria, dewey=dewey)
            resumen["procesados"] += 1

        except Exception as e:
            log_evento("error_parse", archivo=ruta, nivel="ERROR")
            print(f"❌ Error procesando {ruta}: {e}")
            resumen["errores"] += 1

    print(f"""
    Resumen del Pipeline:
          ✔️ Procesados: {resumen['procesados']}
          ⚠️ Omitidos: {resumen['omitidos']}
          ❌ Errores: {resumen['errores']}
""")

if __name__ == "__main__":
    main()

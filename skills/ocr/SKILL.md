---
name: OCR Vision
description: Habilidad para extraer texto de imágenes usando Tesseract OCR.
version: 1.0.0
author: Antigravity (Nova Core)
---

# Skill: OCR Vision (Percepción)

Esta habilidad permite a Nova "ver" y transcribir texto desde archivos de imagen locales (PNG, JPG, JPEG, BMP).

## Cómo Usar
Para activar esta habilidad, el usuario debe mencionar una imagen o pedir realizar un OCR.
Ejemplos:
- "Lee el texto de la imagen factura.png"
- "Hazle un OCR a captura.jpg"
- "¿Qué dice esta foto? imagen.png"

## Requisitos
- Tesseract OCR instalado en el sistema (C:\Program Files\Tesseract-OCR).
- Librerías `pytesseract` y `pillow` instaladas en el entorno virtual.

## Detalles Técnicos
- Utiliza `VisionEngine` como motor subyacente.
- Soporta procesamiento recursivo de carpetas para encontrar imágenes.

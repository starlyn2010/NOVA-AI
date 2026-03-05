import os

SKILLS = {
    # Programación y Agencia (20)
    "refactor_pro": "Habilidad para limpiar y optimizar código sucio o ineficiente.",
    "api_mocker": "Crea servidores de prueba (mock APIs) para desarrollo frontend.",
    "vuln_scan": "Busca fallos de seguridad comunes en código Python y JS.",
    "docker_master": "Genera archivos Dockerfile y docker-compose para despliegue.",
    "perf_profiler": "Analiza cuellos de botella en el rendimiento del código.",
    "unittest_gen": "Escribe pruebas unitarias automáticas para funciones.",
    "sql_architect": "Diseña esquemas de bases de datos y consultas complejas.",
    "git_companion": "Ayuda con comandos de Git, resolución de conflictos y commits.",
    "regex_lab": "Genera y explica expresiones regulares para búsqueda de texto.",
    "autodoc": "Crea documentación técnica y archivos README automáticamente.",
    "dependency_mgr": "Gestiona archivos requirements.txt y actualizaciones de librerías.",
    "css_styler": "Genera estilos CSS modernos y responsivos para componentes.",
    "js_logic": "Implementa lógica compleja en Javascript para aplicaciones web.",
    "bash_hero": "Escribe scripts de terminal para automatización en Windows/Linux.",
    "json_parser": "Valida y transforma estructuras de datos JSON complejas.",
    "xml_to_json": "Convierte datos de formato XML a JSON de manera estructurada.",
    "cli_builder": "Ayuda a crear interfaces de línea de comandos profesionales.",
    "env_config": "Gestiona variables de entorno y archivos .env de forma segura.",
    "readme_specialist": "Mejora visualmente los archivos README con tablas y badges.",
    "bug_hunter": "Técnicas avanzadas de depuración y rastreo de errores.",

    # Productividad y Creatividad (20)
    "excel_wizard": "Manipulación avanzada de hojas de cálculo y reportes.",
    "pdf_intelligence": "Extracción de información clave de documentos PDF.",
    "mail_drafter": "Redacción de correos profesionales y persuasivos.",
    "agenda_master": "Gestión de tareas y prioridades en el sistema.",
    "note_summarizer": "Resúmenes ejecutivos de textos largos o artículos.",
    "pc_cleaner": "Identificación de archivos basura y limpieza de disco.",
    "media_converter": "Conversión de formatos de imagen, audio y video.",
    "content_creator": "Guiones para videos, hilos de redes sociales y blogs.",
    "personal_tutor": "Explicación didáctica de conceptos académicos complejos.",
    "polyglot": "Traducción técnica avanzada manteniendo el contexto.",
    "roleplay_engine": "Simulación de personalidades para práctica de entrevistas.",
    "brainstormer": "Generación masiva de ideas para proyectos o problemas.",
    "startup_mentor": "Guía para validación de ideas de negocio y modelos Canvas.",
    "joke_factory": "Creación de chistes, humor técnico y sarcasmo inteligente.",
    "poetry_soul": "Escritura de poemas, verso libre y sonetos en español.",
    "novel_writer": "Desarrollo de tramas, capítulos y arcos de personajes.",
    "legal_simplifier": "Explicación sencilla de términos y condiciones legales.",
    "health_coach": "Consejos de ergonomía y bienestar para programadores.",
    "travel_planner": "Planificación detallada de rutas y presupuestos de viaje.",
    "cooking_agent": "Recetas creativas basadas en ingredientes disponibles."
}

base_dir = r"C:\Users\DELL\Desktop\inventos\Nova\skills"
os.makedirs(base_dir, exist_ok=True)

for name, desc in SKILLS.items():
    skill_dir = os.path.join(base_dir, name)
    os.makedirs(skill_dir, exist_ok=True)
    
    skill_md = os.path.join(skill_dir, "SKILL.md")
    content = f"""---
name: {name.replace('_', ' ').title()}
description: {desc}
version: 1.0.0
author: Antigravity (Nova Core)
---

# Skill: {name.replace('_', ' ').title()}

{desc}

## Cómo usar
Pide a Nova que realice una tarea relacionada con {name.replace('_', ' ')}.

## Detalles
Esta es una habilidad modular cargada en el sistema de Nova.
"""
    with open(skill_md, "w", encoding="utf-8") as f:
        f.write(content)

print(f"DONE: Se han creado {len(SKILLS)} habilidades en {base_dir}")

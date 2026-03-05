
import os

skills = [
    ("bio_informatic", "Genética, análisis de ADN y proteínas."),
    ("game_economy", "Equilibrio de economía y sistemas en videojuegos."),
    ("sound_engineer", "Ecualización, mezcla y masterización profesional."),
    ("real_time_comm", "WebRTC, Sockets y chat en tiempo real."),
    ("smart_contracts_audit", "Seguridad en Solidity, Vyper y auditoría de Web3."),
    ("fpga_designer", "VHDL, Verilog y diseño de hardware lógico."),
    ("rust_systems", "Programación de bajo nivel y segura con Rust."),
    ("golang_microservices", "Escalabilidad y arquitectura con Go."),
    ("blockchain_forensics", "Rastreo de transacciones cripto e inteligencia on-chain."),
    ("cloud_finops", "Optimización de costos y finanzas en la nube."),
    ("edge_computing", "Lógica en dispositivos periféricos y baja latencia."),
    ("serverless_arch", "Lambda, Functions y arquitectura dirigida por eventos."),
    ("ddos_protection", "Mitigación de ataques de red y capas de transporte."),
    ("malconf_audit", "Auditoría de configuraciones de servidor y hardening."),
    ("zero_trust_security", "Implementación de arquitectura de seguridad Zero Trust."),
    ("oauth2_flow_expert", "Gestión avanzada de identidades, flujos y accesos."),
    ("kafka_streaming", "Procesamiento de eventos a gran escala y pipelines de datos."),
    ("graphql_federation", "Arquitecturas de supergrafos y subgrafos federados."),
    ("spatial_data_analyst", "SIG, mapas, geoprocesamiento y análisis espacial."),
    ("ar_vr_logic", "Desarrollo para Unity y Unreal aplicado a AR/VR."),
    ("3d_modeler_logic", "Flujos de trabajo para Blender, Maya y renderizado."),
    ("pwa_specialist", "Apps web progresivas, service workers y offline mode."),
    ("mobile_ios_swift", "Desarrollo nativo para el ecosistema Apple."),
    ("mobile_android_kotlin", "Desarrollo nativo moderno para Android."),
    ("flutter_cross_platform", "Creación de apps multiplataforma con Flutter."),
    ("react_native_app", "Apps móviles basadas en JavaScript y React."),
    ("electron_desktop", "Apps de escritorio multiplataforma con tecnologías web."),
    ("chrome_extension_dev", "Desarrollo de complementos y extensiones de navegador."),
    ("shopify_themer", "Ecommerce, plantillas Liquid y personalización avanzada."),
    ("wordpress_hardener", "Seguridad avanzada, WAF y optimización de WordPress."),
    ("data_lakehouse", "Arquitecturas modernas que unen Data Lake y Warehouse."),
    ("sparked_big_data", "Analítica distribuida masiva con Apache Spark."),
    ("airflow_orchestrator", "Pipelines de datos complejos y orquestación de tareas."),
    ("dbt_transformer", "Transformación de datos profesional dentro del almacén."),
    ("snowflake_analyst", "Consultas, gestión y optimización en Snowflake."),
    ("elasticsearch_pro", "Búsqueda avanzada, indexación y análisis de logs."),
    ("devsecops_pipeline", "Integración de seguridad continua en ciclos CI/CD."),
    ("azure_devops_mgr", "Gestión del ciclo de vida de software con Azure DevOps."),
    ("gitlab_runner_expert", "Pipelines avanzados y runners en GitLab."),
    ("bitbucket_pipelines", "Automatización de despliegue en Bitbucket."),
    ("bug_bounty_hunter", "Metodologías de reconocimiento y caza de vulnerabilidades."),
    ("red_teaming_ops", "Simulación de adversarios avanzados y persistentes."),
    ("blue_teaming_def", "Defensa proactiva, monitoreo de red y respuesta a incidentes."),
    ("cryptanalysis", "Análisis criptográfico teórico y ataques a algoritmos."),
    ("quantum_algorithms", "Implementación de algoritmos de Shor, Grover y lógica cuántica."),
    ("molecular_dynamics", "Simulaciones químicas, físicas y biofísicas."),
    ("agricultural_ai", "Uso de drones, sensores e IA aplicada al campo."),
    ("autonomous_vehicle_logic", "Visión artificial y sensores para autoconducción."),
    ("robotic_process_auto", "Automatización RPA con UiPath, Power Automate y Blue Prism."),
    ("chatbot_personality", "Diseño de personalidad, psicología y tono de voz para IAs.")
]

base_path = "skills"

for name, desc in skills:
    folder = os.path.join(base_path, name)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write(f"---\nname: {name}\ndescription: {desc}\n---\n\n")
        f.write(f"# Skill: {name}\n\n")
        f.write(f"Esta skill permite a Nova manejar peticiones relacionadas con: {desc}\n\n")
        f.write("## Capacidades\n- Reconocimiento de contexto específico.\n- Generación de lógica dedicada.\n- Integración con motores de Nova.\n")

print(f"Creados {len(skills)} nuevas skills en {base_path}")

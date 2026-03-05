
import yaml
import os

db_path = "engines/tools/tools_database.yaml"

new_tools = {
    "kubescape": {"name": "Kubescape", "description": "Seguridad en Kubernetes y KSPM.", "keywords": ["k8s security", "compliance", "kubescape"]},
    "checkov": {"name": "Checkov", "description": "Análisis estático de IaC.", "keywords": ["terraform scan", "iac security", "checkov"]},
    "terragrunt": {"name": "Terragrunt", "description": "Wrapper para mantener Terraform DRY.", "keywords": ["terraform", "terragrunt", "dry"]},
    "pulumi": {"name": "Pulumi", "description": "IaC usando lenguajes de programación reales.", "keywords": ["iac", "cloud", "pulumi"]},
    "helm": {"name": "Helm", "description": "Gestor de paquetes para Kubernetes.", "keywords": ["helm", "chart", "k8s deployment"]},
    "istio": {"name": "Istio", "description": "Service mesh para conectar y asegurar microservicios.", "keywords": ["service mesh", "istio", "envoy"]},
    "kong": {"name": "Kong", "description": "Gateway de API cloud-native.", "keywords": ["gateway", "proxy", "api", "kong"]},
    "apisix": {"name": "APISIX", "description": "Gateway de API de alto rendimiento.", "keywords": ["gateway", "lua", "apisix", "cloud"]},
    "keycloak": {"name": "Keycloak", "description": "Gestión de identidad y accesos open source.", "keywords": ["iam", "sso", "auth", "keycloak"]},
    "auth0": {"name": "Auth0", "description": "Plataforma de identidad como servicio.", "keywords": ["auth0", "jwt", "login"]},
    "vault": {"name": "HashiCorp Vault", "description": "Gestión de secretos y cifrado de datos.", "keywords": ["vault", "secrets", "pki"]},
    "consul": {"name": "HashiCorp Consul", "description": "Descubrimiento de servicios y configuración.", "keywords": ["service discovery", "kv", "consul"]},
    "nomad": {"name": "HashiCorp Nomad", "description": "Orquestador de cargas de trabajo flexible.", "keywords": ["orquestador", "nomad", "jobs"]},
    "boundary": {"name": "HashiCorp Boundary", "description": "Gestión de acceso privilegiado.", "keywords": ["pam", "access", "boundary"]},
    "waypoint": {"name": "HashiCorp Waypoint", "description": "Despliegue de aplicaciones simplificado.", "keywords": ["deploy", "waypoint", "app"]},
    "suricata": {"name": "Suricata", "description": "Motor de detección de intrusiones (IDS/IPS).", "keywords": ["ids", "ips", "monitoreo de red"]},
    "zeek": {"name": "Zeek", "description": "Monitor de seguridad de red avanzado.", "keywords": ["zeek", "bro", "network logs"]},
    "falco": {"name": "Falco", "description": "Seguridad en tiempo de ejecución para cloud native.", "keywords": ["falco", "runtime security", "ebpf"]},
    "trivy": {"name": "Trivy", "description": "Escáner de vulnerabilidades para contenedores.", "keywords": ["scanner", "vulnerabilidades", "container", "trivy"]},
    "grype": {"name": "Grype", "description": "Escáner de vulnerabilidades en SBOM.", "keywords": ["grype", "sbom", "security"]},
    "syft": {"name": "Syft", "description": "Generador de SBOM profesional.", "keywords": ["sbom", "syft", "inventory"]},
    "cosign": {"name": "Cosign", "description": "Firma y verificación de contenedores.", "keywords": ["sign", "verify", "sigstore", "cosign"]},
    "krakend": {"name": "KrakenD", "description": "Gateway de API ultra rápido sin estado.", "keywords": ["gateway", "krakend", "lfe"]},
    "tyk": {"name": "Tyk", "description": "Plataforma de gestión de APIs.", "keywords": ["api management", "tyk", "gateway"]},
    "temporal": {"name": "Temporal", "description": "Orquestación de workflows duraderos.", "keywords": ["workflow", "durability", "temporal"]},
    "camunda": {"name": "Camunda", "description": "Motor de procesos BPMN.", "keywords": ["bpmn", "camunda", "procesos"]},
    "rabbitmq": {"name": "RabbitMQ", "description": "Broker de mensajería asíncrona.", "keywords": ["colas", "mensajeria", "amqp", "rabbitmq"]},
    "activemq": {"name": "ActiveMQ", "description": "Servidor de mensajería multi-protocolo.", "keywords": ["jms", "activemq", "broker"]},
    "nats": {"name": "NATS", "description": "Sistema de mensajería cloud-native ultra-rápido.", "keywords": ["messaging", "nats", "pubsub"]},
    "mqtt": {"name": "MQTT", "description": "Protocolo de mensajería para IoT.", "keywords": ["iot", "mqtt", "mosquitto"]},
    "influxdb": {"name": "InfluxDB", "description": "Base de datos de series temporales.", "keywords": ["time series", "metricas", "influx"]},
    "timescale": {"name": "TimescaleDB", "description": "SQL masivo para series temporales.", "keywords": ["timescale", "postgres", "tsdb"]},
    "neo4j": {"name": "Neo4j", "description": "Base de datos orientada a grafos.", "keywords": ["grafos", "nodos", "neo4j"]},
    "cassandra": {"name": "Apache Cassandra", "description": "Base de datos distribuida escalable.", "keywords": ["cassandra", "nosql", "columnar"]},
    "scylladb": {"name": "ScyllaDB", "description": "NoSQL de alto rendimiento compatible con Cassandra.", "keywords": ["scylladb", "rapido", "full-throttle"]},
    "clickhouse": {"name": "ClickHouse", "description": "Base de datos analítica columnar.", "keywords": ["analytics", "olap", "clickhouse"]},
    "dask": {"name": "Dask", "description": "Computación paralela nativa en Python.", "keywords": ["paralelismo", "dask", "big data"]},
    "ray": {"name": "Ray", "description": "Runtime de computación distribuida para IA.", "keywords": ["distribuido", "ray", "scaling"]},
    "mlflow": {"name": "MLflow", "description": "Gestión del ciclo de vida de ML.", "keywords": ["mlflow", "experimentos", "model registry"]},
    "kubeflow": {"name": "Kubeflow", "description": "Platforma de ML sobre Kubernetes.", "keywords": ["k8s", "ml", "kubeflow", "pipeline"]},
    "wandb": {"name": "W&B", "description": "Pesos y sesgos para experimentos de IA.", "keywords": ["visualizar ai", "experimentos", "wandb"]},
    "optuna": {"name": "Optuna", "description": "Optimización de hiperparámetros automatizada.", "keywords": ["hiperparametros", "optuna", "tuning"]},
    "streamlit": {"name": "Streamlit", "description": "Apps de datos rápidas en Python.", "keywords": ["web app", "data science", "streamlit"]},
    "gradio": {"name": "Gradio", "description": "Interfaces rápidas para modelos de IA.", "keywords": ["demo ai", "gradio", "ui"]},
    "sanic": {"name": "Sanic", "description": "Framework web async de alta velocidad.", "keywords": ["web", "async", "sanic", "rapido"]},
    "tortoise-orm": {"name": "Tortoise ORM", "description": "ORM asíncrono para Python inspirado en Django.", "keywords": ["orm", "async", "tortoise", "db"]},
    "sqlalchemy": {"name": "SQLAlchemy", "description": "El toolkit SQL y ORM definitivo para Python.", "keywords": ["sqlalchemy", "orm", "sql"]},
    "prisma": {"name": "Prisma", "description": "ORM moderno para TypeScript y Python.", "keywords": ["prisma", "schema", "database"]},
    "drizzle": {"name": "Drizzle ORM", "description": "ORM ligero y rápido para TypeScript.", "keywords": ["drizzle", "typescript", "orm"]},
    "tauri": {"name": "Tauri", "description": "Apps de escritorio seguras y ligeras con Rust.", "keywords": ["tauri", "desktop app", "rust", "frontend"]}
}

current_db = {"tools": {}, "internal_agent_tools": {}}

if os.path.exists(db_path):
    with open(db_path, "r", encoding="utf-8") as f:
        current_db = yaml.safe_load(f) or {"tools": {}, "internal_agent_tools": {}}

current_db["tools"].update(new_tools)

with open(db_path, "w", encoding="utf-8") as f:
    yaml.dump(current_db, f, allow_unicode=True, default_flow_style=False)

print(f"Base de datos de herramientas actualizada con {len(new_tools)} entradas adicionales.")

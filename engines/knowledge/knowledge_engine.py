from engines.knowledge.ingestor_engine import KnowledgeIngestor
import os

class KnowledgeEngine:
    def __init__(self):
        self.ingestor = KnowledgeIngestor()

    def process(self, request: str, health_check: bool = False) -> dict:
        """
        Analiza documentos locales para proveer respuestas basadas en archivos.
        """
        if health_check:
            return {"status": "success", "message": "KnowledgeEngine ready."}

        if os.getenv("NOVA_TEST_MODE", "").strip().lower() in {"1", "true", "mock"}:
            return {
                "status": "success",
                "intent": "knowledge_retrieval",
                "instructions_for_llm": "Modo prueba activo: respuesta de conocimiento simulada.",
                "source": "mock_knowledge"
            }
             
        # Intentar ingerir nuevos archivos en la carpeta raw
        raw_path = os.path.join("data", "raw_documents")
        new_docs = self.ingestor.process_folder(raw_path)
        
        # En una implementación completa, esto iría a una base vectorial.
        # Por ahora, extraemos el contenido de los documentos encontrados.
        doc_context = ""
        if new_docs:
            print(f"[Knowledge] Procesados {len(new_docs)} documentos para contexto.")
            for doc in new_docs:
                doc_context += f"\n--- Documento: {doc['filename']} ---\n{doc['content'][:2000]}\n"

        instructions = "Actúa como un EXPERTO y PROFESOR en la materia. Tu respuesta debe ser profunda y detallada."
        if doc_context:
            instructions += f"\n\nUSA ESTE CONTEXTO DE DOCUMENTOS LOCALES:\n{doc_context}"

        return {
            "status": "success",
            "intent": "knowledge_retrieval",
            "instructions_for_llm": instructions,
            "source": "local_documents" if doc_context else "general_knowledge_llm"
        }

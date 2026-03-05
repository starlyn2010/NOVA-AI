import argparse
import json
import os
import statistics
import sys
import time
from collections import Counter


BAD_TEXT_FRAGMENTS = [
    "entiendo.",
    "entiendo",
    "no entiendo",
    "no comprendo",
    "lo siento pero no entiendo",
]


def is_low_quality_text(text: str) -> bool:
    if text is None:
        return True
    norm = str(text).strip().lower()
    if not norm:
        return True
    if len(norm) <= 12:
        return True
    return any(frag in norm for frag in BAD_TEXT_FRAGMENTS)


def prompt_bank() -> list:
    # Cobertura de capacidades principales en frases realistas.
    return [
        "hola nova, como estas hoy?",
        "crea una funcion python para validar correos y dame ejemplo",
        "resuelve 45*3-10 y explica los pasos",
        "escribe un microcuento de robots en 4 lineas",
        "explica que es la memoria ram en lenguaje simple",
        "quiero automatizar tareas de desarrollo y pruebas",
        "busca informacion de ia aplicada en educacion",
        "lista archivos del proyecto",
        "lee la imagen test.png y dime si detectas texto",
        "haz un grafico de barras con ventas enero 10 febrero 12 marzo 8",
        "transcribe un audio de ejemplo",
        "navega en la web y extrae un resumen general",
        "como esta mi pc de cpu y ram ahora",
        "envia un aviso por telegram con el estado del sistema",
        "analiza seguridad del archivo README.md",
        "haz mantenimiento de memoria y logs antiguos",
        "documenta este avance en la wiki del proyecto",
        "cambia la interfaz al modo creativo",
    ]


def build_prompts(count: int) -> list:
    bank = prompt_bank()
    # Prompts ligeros para volumen.
    light_bank = [
        bank[0],   # social
        bank[1],   # programming
        bank[2],   # mathematics
        bank[3],   # creative
        bank[4],   # knowledge
        bank[7],   # files
        bank[15],  # maintenance
        bank[16],  # wiki
    ]

    prompts = []
    light_idx = 0

    # Cada bloque de 100 incluye cobertura completa de capacidades una vez.
    while len(prompts) < count:
        for p in bank:
            if len(prompts) >= count:
                break
            prompts.append(p)

        while len(prompts) % 100 != 0 and len(prompts) < count:
            prompts.append(light_bank[light_idx % len(light_bank)])
            light_idx += 1

    prompts = prompts[:count]
    return prompts


def main() -> int:
    parser = argparse.ArgumentParser(description="Stress test conversacional para Nova.")
    parser.add_argument("--count", type=int, default=3000, help="Numero total de conversaciones.")
    parser.add_argument("--max-turns", type=int, default=1, help="Turnos maximos por conversacion.")
    parser.add_argument(
        "--real-llm",
        action="store_true",
        help="Usa Ollama real. Por defecto usa modo mock para pruebas masivas rapidas.",
    )
    parser.add_argument(
        "--allow-low-quality",
        action="store_true",
        help="No marca como fallo respuestas genericas.",
    )
    parser.add_argument(
        "--output-json",
        default="logs/stress_test_chat_results.json",
        help="Ruta para guardar resultados detallados.",
    )
    args = parser.parse_args()

    if not args.real_llm:
        os.environ["NOVA_TEST_MODE"] = "mock"

    sys.path.append(os.getcwd())
    from orchestrator import Orchestrator

    os.makedirs(os.path.dirname(args.output_json), exist_ok=True)

    nova = Orchestrator()
    prompts = build_prompts(args.count)

    started = time.time()
    latencies = []
    failures = []
    counters = Counter()

    for idx, prompt in enumerate(prompts, 1):
        t0 = time.time()
        try:
            res = nova.process_request(prompt, max_turns=args.max_turns)
            latency = time.time() - t0
            latencies.append(latency)
            counters["total"] += 1

            if not isinstance(res, dict):
                failures.append(
                    {
                        "index": idx,
                        "prompt": prompt,
                        "type": "invalid_response_type",
                        "detail": str(type(res)),
                    }
                )
                counters["failed"] += 1
                continue

            text = str(res.get("text", "")).strip()
            raw = res.get("raw", {}) if isinstance(res.get("raw", {}), dict) else {}
            raw_status = raw.get("status", "n/a")

            if not text:
                failures.append(
                    {
                        "index": idx,
                        "prompt": prompt,
                        "type": "empty_text",
                        "raw_status": raw_status,
                    }
                )
                counters["failed"] += 1
            elif (not args.allow_low_quality) and is_low_quality_text(text):
                failures.append(
                    {
                        "index": idx,
                        "prompt": prompt,
                        "type": "low_quality_text",
                        "raw_status": raw_status,
                        "text_preview": text[:200],
                    }
                )
                counters["failed"] += 1
            else:
                counters["passed"] += 1

        except Exception as e:
            latency = time.time() - t0
            latencies.append(latency)
            counters["total"] += 1
            counters["failed"] += 1
            failures.append(
                {
                    "index": idx,
                    "prompt": prompt,
                    "type": "exception",
                    "detail": str(e),
                }
            )

        if idx % 100 == 0:
            print(
                f"[{idx}/{args.count}] passed={counters['passed']} failed={counters['failed']} "
                f"avg_latency={statistics.mean(latencies):.3f}s",
                flush=True,
            )

    total_time = time.time() - started
    avg_latency = statistics.mean(latencies) if latencies else 0.0
    p95_latency = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else avg_latency

    report = {
        "mode": "real_llm" if args.real_llm else "mock_llm",
        "count": args.count,
        "total_time_sec": round(total_time, 3),
        "avg_latency_sec": round(avg_latency, 4),
        "p95_latency_sec": round(p95_latency, 4),
        "passed": counters["passed"],
        "failed": counters["failed"],
        "failures": failures[:200],  # truncate to keep artifact manageable
    }

    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n--- STRESS TEST SUMMARY ---")
    print(f"Mode: {report['mode']}")
    print(f"Total: {args.count}")
    print(f"Passed: {report['passed']}")
    print(f"Failed: {report['failed']}")
    print(f"Avg latency: {report['avg_latency_sec']}s")
    print(f"P95 latency: {report['p95_latency_sec']}s")
    print(f"Total time: {report['total_time_sec']}s")
    print(f"Report: {args.output_json}", flush=True)

    return 0 if counters["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

# Trabajo Final — Generador de documentación y release notes con LLM

Herramienta que, dado un repositorio de código, genera:

- **Documentación general** del proyecto (arquitectura, módulos, modelo de datos, endpoints) siguiendo un template dado.
- **Release notes** a partir del diff entre una rama base y la rama activa.

El pipeline funciona en dos etapas, cada una a cargo de un agente LLM (Gemini):

1. **Condenser**: batchea los archivos del repo (o los archivos modificados, para release notes) y los condensa — reduce drásticamente el contenido preservando lo relevante para el objetivo (firmas, entidades, rutas/decoradores, etc.), descartando boilerplate.
2. **Documenter**: toma los batches condensados + metadata del repo y redacta el documento final siguiendo el template indicado.

## Requisitos

```
pip install -r requirements.txt
```

Crear `config/.env` con la API key del modelo:

```
API_KEY=<tu-api-key-de-gemini>
```

## Uso

```
python main.py --config <path-al-config.json> [-r|--release-notes] [-c|--use-cache]
```

- `--config <path>`: config a usar. Default: `./config/config.json`.
- `-r` / `--release-notes`: genera release notes (diff `base_branch` → HEAD) en vez de documentación general.
- `-c` / `--use-cache`: reutiliza los batches ya condensados de una corrida anterior (`<output_path>/condensed_batches.json` o `condensed_cache_rn.json`), evitando volver a llamar al condenser. Útil para reintentar solo la etapa del documenter sin regenerar el contexto condensado.

Ejemplos:

```
python main.py --config ./config/doc-general/go_config.json
python main.py --config ./config/doc-general/go_config.json -c
python main.py --config ./config/config.json -r
```

## Configs

Cada config (`config/*.json`) define una corrida contra un repo puntual. Ver `config/config.json` como ejemplo de referencia.

| Campo | Descripción |
| --- | --- |
| `repo_dir` | Path absoluto al repo a documentar. |
| `base_branch` | Rama base. Para documentación general se usa solo para metadata de historial; para release notes es el punto de comparación del diff. |
| `ignore_paths` | Paths a excluir del análisis. |
| `code_extensions` | Extensiones de archivo consideradas código (el resto se trata como no-código y se condensa más agresivamente). |
| `output_language` | Idioma del documento generado. |
| `output_path` | Carpeta de salida (`doc.md`/`doc.html`, caches, y si `debug: true`, los intermedios en `tmp/`). |
| `output_extension` | Extensión del archivo de salida. |
| `template_path` / `rn_template_path` | Templates de documentación / release notes (ver `example-templates/`). |
| `debug` | Si es `true`, guarda en `<output_path>/tmp/` los batches, prompts y respuestas crudas de cada llamada — útil para diagnosticar fallos de condensación. |
| `agents.condenser.model` / `agents.documenter.model` | Modelo Gemini a usar en cada etapa. |
| `agents.<agent>.thinking_level` | Nivel de "thinking" del modelo (`LOW`/`MEDIUM`/`HIGH`), opcional. |

Los configs usados para los casos de evaluación del TF (Go, Java, JS) viven en `config/doc-general/` en la branch `tf-eval-cases`.

## Manejo de errores y reintentos

`service/llm_service.py` reintenta automáticamente errores transitorios (429/500/502/503/504) con backoff exponencial. El número de reintentos es configurable por agente vía `max_retries` al instanciar `LlmService` — el `Documenter` usa `max_retries=1` por defecto (la llamada final es la más cara, y no tiene sentido reintentar contra alta demanda del modelo consumiendo cuota).

Si algún batch falla al condensar (error de red persistente o JSON inválido en la respuesta), la corrida aborta antes de invocar al documenter en vez de generarle contexto roto.

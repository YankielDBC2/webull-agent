# CHANGELOG

Registro cronologico de todos los cambios del proyecto. Cada entrada incluye: fecha, autor, descripcion del cambio, motivo y archivos afectados.

---

## 2026-06-19 (2) — Investigacion de datos y estadisticas de contratos

**Cambios:**
- Investigacion exhaustiva de 10 preguntas clave sobre datos de contratos
- Documentado que datos SI/NO/PARCIAL estan disponibles
- Analisis de viabilidad para deteccion de whales, muros, order flow

**Archivos creados:**
- `docs/contracts-data-research.md` — Investigacion completa con tabla de respuestas

**Archivos modificados:**
- `logs/CHANGELOG.md` — Esta entrada

---

## 2026-06-19 (1) — Inicializacion del proyecto

**Cambios:**
- Creado proyecto `webull-agent` a partir de carpeta `tradingview`
- Documentadas todas las APIs publicas de Webull (8 servicios)
- Establecido sistema de documentacion obligatoria y logs
- Estructura inicial del proyecto
- Repositorio Git inicializado y subido a GitHub

**Motivo:** Investigacion de APIs de Webull para trading algoritmico con contratos

**Archivos creados:**
- `README.md` — Overview del proyecto
- `.gitignore` — Exclusion de credenciales y archivos sensibles
- `docs/webull-api-reference.md` — Referencia completa de APIs
- `docs/setup-guide.md` — Guia de configuracion
- `docs/security.md` — Buenas practicas de seguridad
- `logs/CHANGELOG.md` — Este archivo
- `logs/2026-06-19.md` — Log detallado de la sesion
- `logs/.session-template.md` — Template para futuras sesiones

**Estructura:**
```
webull-agent/
├── README.md
├── docs/
├── logs/
├── src/
├── skills/
├── config/
└── scripts/
```

# CHANGELOG

Registro cronologico de todos los cambios del proyecto. Cada entrada incluye: fecha, autor, descripcion del cambio, motivo y archivos afectados.

---

## 2026-06-19 (6) — Implementacion del bot: Webull client + Telegram reporter

**Cambios:**
- Implementado cliente HTTP con firma HMAC-SHA1 (sin depender del SDK — compatible Python 3.14)
- Verificada conexion a Webull test env: account list OK, snapshot AAPL OK
- Integrado Telegram reporter: mensajes de prueba enviados al canal
- Documentada restriccion: test env solo permite AAPL (necesita API key prod para 10 stocks)
- Estructura del bot completa: webull_client, market_data, telegram_reporter, bot main loop

**Archivos creados/modificados:**
- `src/webull_client.py` — Cliente HTTP con HMAC signing manual (docs oficiales)
- `src/market_data.py` — Engine de polling con cache y alertas
- `src/telegram_reporter.py` — Formateo y envio a Telegram
- `src/bot.py` — Main loop async del bot
- `src/config.py` — Configuracion desde .env
- `src/__init__.py` — Package
- `requirements.txt` — Dependencias
- `scripts/test_connection.py` — Verifica Webull
- `scripts/test_watchlist.py` — Test 10 stocks
- `scripts/test_telegram.py` — Test Telegram
- `.gitignore` — Ajustado (config/ ya no esta ignorado, solo .env)
- `docs/bot-strategy.md` — Estrategia completa + restricciones

---

## 2026-06-19 (5) — Arquitectura Paper Trading y Rate Limits

**Cambios:**
- Compilados rate limits de TODOS los endpoints (HTTP, MQTT, gRPC)
- Disenada arquitectura de paper trading con 6 componentes
- Calculado presupuesto de peticiones: consumo <3% del limite en fase paper
- Documentados fees reales de Webull a simular (SEC, FINRA, CAT)
- Plan de implementacion en 4 fases

**Archivos creados:**
- `docs/paper-trading-architecture.md` — Rate limits, fees, arquitectura, fases

---

## 2026-06-19 (4) — Lista de stocks para operar opciones con $100

**Cambios:**
- Compilada lista de 20 stocks con alto volumen aptos para opciones con presupuesto de $100
- Clasificados en 3 tiers por ajuste de presupuesto y liquidez
- Documentados criterios de seleccion y endpoints API para verificacion
- Plan de script para refresco diario de la lista

**Archivos creados:**
- `docs/optionable-stocks.md` — 20 stocks, criterios, endpoints y script plan

---

## 2026-06-19 (3) — Investigacion de datos adicionales (NOII, streaming, trade events, etc.)

**Cambios:**
- Investigados 10 endpoints adicionales no cubiertos en la investigacion inicial
- Documentados schemas de respuesta con campos especificos (snapshot, trade events)
- Descubierto NOII (subasta), streaming MQTT, trade events gRPC
- Documentado rate limits detallados por endpoint

**Archivos creados:**
- `docs/additional-data.md` — Campos de respuesta, streaming, NOII, news, screener, watchlists

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

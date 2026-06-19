# Webull Agent

Integracion con las APIs publicas de Webull para trading algoritmico, datos de mercado, y operaciones con contratos (stocks, opciones, futuros, crypto, event contracts).

## APIs Disponibles

| API | Entorno | Acceso |
|-----|---------|--------|
| **Open API** (REST + WebSocket) | Produccion / Test | API Key + Secret + 2FA |
| **Cloud MCP** (OAuth) | Produccion | Zero-config para agentes AI |
| **Agent Skills** (Python CLI) | Produccion / Test | Scripts listos para asistentes AI |
| **Broker API** | Produccion | Plataformas FinTech |
| **Paper Trading** | Produccion | Simulacion sin riesgo |
| **Script Editor** | Produccion | Indicadores (tipo Pine Script) |

## Reglas del Proyecto

- **Documentacion obligatoria:** Todo hallazgo, cambio, decision o error se documenta en `logs/` y `CHANGELOG.md`
- **Cada sesion** genera un archivo `logs/YYYY-MM-DD.md` con: contexto, plan, cambios, decisiones, errores y rollback
- **Antes de modificar** cualquier archivo, se revisa su estado actual
- **Punto de retorno:** Cada cambio debe tener un camino claro de rollback

## Documentacion

- [Referencia de APIs](./docs/webull-api-reference.md) — Todas las APIs documentadas con endpoints
- [Investigacion de Contratos](./docs/contracts-data-research.md) — Que datos y estadisticas podemos obtener
- [Datos Adicionales](./docs/additional-data.md) — Schemas, streaming MQTT, NOII, trade events, screener
- [Stocks para Opciones](./docs/optionable-stocks.md) — 20 stocks con buen volumen para operar con ~$100
- [Guia de Configuracion](./docs/setup-guide.md) — Como obtener credenciales y configurar el entorno
- [Seguridad](./docs/security.md) — Buenas practicas de seguridad
- [CHANGELOG](./logs/CHANGELOG.md) — Registro cronologico de cambios
- [Logs de sesion](./logs/) — Registro detallado por sesion

## Estructura del Proyecto

```
webull-agent/
├── README.md
├── docs/
│   ├── webull-api-reference.md
│   ├── setup-guide.md
│   └── security.md
├── logs/
│   ├── CHANGELOG.md
│   ├── .session-template.md
│   └── YYYY-MM-DD.md
├── src/                   # Codigo fuente
├── skills/                # Webull Agent Skills
├── config/                # Configuracion (.env, tokens)
└── scripts/               # Scripts auxiliares
```

## Enlaces Oficiales

- **Developer Portal:** https://developer.webull.com/apis
- **Open API:** https://www.webull.com/open-api
- **Agentic (AI):** https://www.webull.com/agentic
- **Paper Trading:** https://www.webull.com/paper-trading
- **GitHub SDKs:** https://github.com/webull-inc

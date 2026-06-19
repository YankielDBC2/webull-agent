# Webull API Reference

Documentacion completa de las APIs publicas de Webull.

---

## 1. Open API (REST + WebSocket)

**Base URLs:**

| Entorno | HTTP API | Trade Events (gRPC) | Market Streaming (MQTT) |
|---------|----------|---------------------|-------------------------|
| Produccion | `api.webull.com` | `events-api.webull.com` | `data-api.webull.com` |
| Test | `us-openapi-alb.uat.webullbroker.com` | `us-openapi-events.uat.webullbroker.com` | — |

**Autenticacion:** API Key + App Secret + firma HMAC en cada request. 2FA opcional con Dynamic Token.

**SDKs oficiales:**

```bash
# Python
pip install webull-openapi-python-sdk

# Java
# Agregar webull-openapi-java-sdk a dependencias Maven
```

---

## 2. Market Data API

### Stocks / ETFs

| Endpoint | Descripcion |
|----------|-------------|
| `stock_snapshot` | Snapshot en tiempo real (precio, cambio, volumen) |
| `stock_bars` | Velas OHLCV por simbolo |
| `stock_batch_bars` | Velas OHLCV para multiples simbolos |
| `stock_tick` | Tick-by-tick (cada transaccion individual) |
| `stock_quotes` | Bid/Ask con depth en tiempo real |
| `stock_footprint` | Footprint de ordenes grandes (order flow) |
| `stock_noii_snapshot` | NOII snapshot (desequilibrio de subasta) |
| `stock_noii_bars` | NOII OHLCV bars |
| `stock_gainers_losers` | Top ganadores/perdedores por % cambio |
| `stock_most_active` | Acciones mas activas del dia |

**Niveles de datos:**
- **Level 1 (gratis):** Streaming quotes para mercado US
- **Level 2:** Depth de ordenes (requiere suscripcion)
- **50 niveles** de datos en tiempo real para US stocks

### Futuros

| Endpoint | Descripcion |
|----------|-------------|
| `futures_snapshot` | Snapshot en tiempo real |
| `futures_bars` | Velas OHLCV |
| `futures_tick` | Tick-by-tick |
| `futures_depth` | Order book depth |
| `futures_footprint` | Footprint de ordenes grandes |
| `instrument_futures_products` | Todos los codigos de productos |
| `instrument_futures_product_class` | Grupos de clasificacion |
| `instrument_futures_list` | Instrumentos por simbolo |

### Crypto

| Endpoint | Descripcion |
|----------|-------------|
| `crypto_snapshot` | Snapshot en tiempo real |
| `crypto_bars` | Velas OHLCV |

### Event Contracts

| Endpoint | Descripcion |
|----------|-------------|
| `event_snapshot` | Snapshot en tiempo real |
| `event_depth` | Order book depth |
| `event_bars` | Velas OHLCV |
| `event_tick` | Tick-by-tick |
| `get_event_series` | Series de contratos |
| `get_event_instruments` | Instrumentos por serie |
| `get_event_categories` | Categorias de eventos |
| `get_event_events` | Eventos dentro de una serie |

### Informacion de Instrumentos

| Endpoint | Descripcion |
|----------|-------------|
| `get_instruments` | Info de stocks/ETFs |
| `get_futures_instruments` | Info de futuros |
| `get_futures_instruments_by_code` | Contratos por codigo |
| `get_futures_products` | Todos los productos de futuros |
| `get_crypto_instruments` | Info de criptomonedas |
| `instrument_company_profile` | Perfil de empresa (CEO, sector, empleados) |
| `instrument_analyst_rating` | Ratings de analistas (buy/hold/sell) |
| `instrument_analyst_target_price` | Precio objetivo (media, alto, bajo, mediana) |

### Watchlists

| Endpoint | Descripcion |
|----------|-------------|
| `watchlist_list` | Listar todas las watchlists |
| `watchlist_create` | Crear nueva |
| `watchlist_delete` | Eliminar |
| `watchlist_update` | Actualizar nombre/orden |
| `watchlist_instruments_list` | Instrumentos en una watchlist |
| `watchlist_instruments_add` | Agregar instrumentos |
| `watchlist_instruments_remove` | Eliminar instrumentos |
| `watchlist_instruments_update` | Actualizar orden |

---

## 3. Trading API

### Stocks

| Endpoint | Descripcion |
|----------|-------------|
| `place_stock_order` | Colocar orden (market, limit, stop, stop-limit) |
| `preview_stock_order` | Previsualizar orden sin enviar |
| `replace_stock_order` | Modificar orden existente |
| `place_stock_combo_order` | Orden combo (OTO/OCO/OTOCO) |
| `place_algo_order` | Orden algoritmica (TWAP/VWAP/POV) |

### Opciones

| Endpoint | Descripcion |
|----------|-------------|
| `place_option_single_order` | Orden simple de opcion |
| `preview_option_order` | Previsualizar orden de opcion |
| `replace_option_order` | Modificar orden de opcion |
| `place_option_strategy_order` | Estrategia multi-leg |

> **Comisiones:** $0 comision para stocks/ETFs/opciones. $0.50/contrato para index options. $0.10/contrato para oversized option orders.

### Futuros

| Endpoint | Descripcion |
|----------|-------------|
| `place_futures_order` | Colocar orden de futuros |
| `replace_futures_order` | Modificar orden de futuros |

### Crypto

| Endpoint | Descripcion |
|----------|-------------|
| `place_crypto_order` | Colocar orden de crypto |

### Event Contracts

| Endpoint | Descripcion |
|----------|-------------|
| `place_event_order` | Colocar orden de event contract |
| `replace_event_order` | Modificar orden |

### Gestion de Ordenes

| Endpoint | Descripcion |
|----------|-------------|
| `cancel_order` | Cancelar orden no ejecutada |
| `get_order_history` | Historial de ordenes |
| `get_open_orders` | Ordenes abiertas/pendientes |
| `get_order_detail` | Detalle de una orden especifica |

---

## 4. Account API

| Endpoint | Descripcion |
|----------|-------------|
| `get_account_list` | Listar cuentas vinculadas |
| `get_account_balance` | Balance, buying power, cash |
| `get_account_positions` | Posiciones actuales y holdings |

---

## 5. Connect API (MCP para Agentes AI)

### Cloud MCP Server

- **URL:** `https://api.webull.com/mcp`
- **Auth:** OAuth (autorizar una vez, se refresca automaticamente)
- **Zero-config:** Sin instalacion local, compatible con ChatGPT, Claude, Cursor, Codex, Kiro
- **5 asset classes** soportadas

### Local MCP Server

- **Instalacion:** via `uvx`
- **Credenciales:** locales, nunca salen del dispositivo
- **Ideal para:** Claude Code, Cursor, Codex

### Agent Skills (Python CLI)

- **Repositorio:** https://github.com/webull-inc/webull-openapi-skills
- **Comando:** `webull-skill <modulo> --action <accion>`
- **Modulos:** `trading`, `market-data`, `auth`
- **Output:** Texto formateado a stdout, errores a stderr
- **Seguridad:** Whitelist de simbolos, limites de orden, preview obligatorio

---

## 6. Broker API

Para plataformas FinTech que necesitan integrar Webull como broker:

| Funcionalidad | Descripcion |
|---------------|-------------|
| Onboarding | Creacion y verificacion de cuentas de usuario |
| Account Management | Gestion de cuentas y balances |
| Funding | Depositos, retiros, transferencias ACH |
| Order Management | Colocacion, modificacion y cancelacion de ordenes |
| Price Display | Visualizacion de precios y datos de mercado |

**Contacto:** Para acceso institucional, contactar a Webull directamente.

---

## 7. Paper Trading (Simulador)

Acceso a todos los productos (stocks, ETFs, opciones, futuros) con datos en tiempo real:

- Dinero virtual ilimitado
- 60+ indicadores tecnicos
- 17+ herramientas de graficos
- Sin riesgo ni comisiones

**Acceso:** `https://www.webull.com/paper-trading`

---

## 8. Script Editor

Lenguaje de scripting inspirado en Pine Script (TradingView) para crear indicadores personalizados:

- Accesible para usuarios sin conocimientos avanzados de programacion
- Optimizado en almacenamiento, tiempo de ejecucion y gramatica
- Los indicadores se pueden guardar y compartir

**Acceso:** `https://www.webull.com/help/faq/10782-Script-Editor`

---

## Niveles de Acceso por Tipo de Usuario

| Tipo | Trading | Market Data | Adicional |
|------|---------|-------------|-----------|
| **Retail** | Order, Cancel, Query | Real-Time Quotes, Historical Candlestick | — |
| **Institucional** | Non-Retail, Advanced Orders | High-Frequency Push, Level-2 Depth | — |
| **FinTech** | Order Management, Price Display | Via Trading & Market Data API | Broker API (Onboarding, Account, Funding) |

---

## Entornos

### Produccion

```
WEBULL_ENVIRONMENT=prod
WEBULL_REGION_ID=us
```

### Test (UAT)

```
WEBULL_ENVIRONMENT=uat
WEBULL_REGION_ID=us
```

El entorno de test tiene credenciales publicas compartidas — no requiere aplicacion previa.

---

## Enlaces Oficiales

| Recurso | URL |
|---------|-----|
| Dev Portal | https://developer.webull.com/apis |
| Open API Landing | https://www.webull.com/open-api |
| Agentic AI Trading | https://www.webull.com/agentic |
| Paper Trading | https://www.webull.com/paper-trading |
| Python SDK | https://github.com/webull-inc/webull-openapi-python-sdk |
| Agent Skills | https://github.com/webull-inc/webull-openapi-skills |
| API Reference | https://developer.webull.com/apis/docs/webull-open-api-reference |
| Getting Started | https://developer.webull.com/apis/docs/getting-started |

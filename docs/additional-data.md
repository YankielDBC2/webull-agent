# Datos Adicionales Disponibles en Webull API

> **Fecha:** 2026-06-19 | **Proposito:** Documentar endpoints y datos adicionales no cubiertos en la investigacion inicial de contratos.

---

## 1. Campos Especificos en Respuestas API

### Stock Snapshot (`/openapi/market-data/stock/snapshot`)

Ejemplo de respuesta documentada:

```json
{
  "symbol": "AAPL",
  "instrument_id": "913256135",
  "price": "185.50",
  "open": "184.00",
  "high": "186.20",
  "low": "183.80",
  "volume": "52340000",
  "change": "1.50",
  "change_ratio": "0.0082",
  "pre_close": "184.00",
  "last_trade_time": 1710849600000
}
```

**Campos confirmados:**

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `symbol` | string | Ticker |
| `instrument_id` | string | ID unico del instrumento |
| `price` | string | Ultimo precio (string para precision) |
| `open` | string | Precio de apertura |
| `high` | string | Maximo del dia |
| `low` | string | Minimo del dia |
| `volume` | string | Volumen total |
| `change` | string | Cambio absoluto |
| `change_ratio` | string | Cambio porcentual |
| `pre_close` | string | Cierre anterior |
| `last_trade_time` | int64 | Timestamp Unix ms de la ultima transaccion |

**Parametros adicionales:**
- `extend_hour_required=true` — Incluye pre-market (4:00-9:30 AM ET) y after-hours (4:00-8:00 PM ET)
- `overnight_required=true` — Incluye sesion overnight (8:00 PM-4:00 AM ET)
- `category=US_STOCK` o `US_ETF`

> **Nota:** Todos los precios y valores numericos se devuelven como **strings** para preservar precision. Timestamps en **Unix milliseconds**.

---

## 2. Streaming en Tiempo Real (MQTT)

### Subscribe (`/openapi/market-data/streaming/subscribe`)

Permite suscribirse a push de datos en tiempo real via **MQTT** sobre WebSocket/TCP.

**Tipos de datos suscribibles:**
- **Quotes** (bid/ask en tiempo real)
- **Snapshots** (precio, cambio, volumen)
- **Tick data** (cada transaccion)

**Rate limit:** 600 requests/minuto

**Disponible solo en produccion** — No en entorno de test (UAT).

### Flujo:
1. Llamar `subscribe` para registrar interes en simbolos
2. Recibir push MQTT continuo de datos
3. Llamar `unsubscribe` para liberar el topic quota

> **Estrategia:** Combinando MQTT streaming para quotes + snapshots en tiempo real, podes construir un sistema de monitoreo de order book en vivo sin hacer polling constante. Esto es clave para detectar muros y whales en tiempo real.

---

## 3. Trade Events (gRPC Streaming)

### Subscribe Trade Events

Conexion persistente **gRPC server-streaming** para recibir cambios de estado de ordenes en tiempo real.

**Escenas soportadas:**

| scene_type | Descripcion | Datos incluidos |
|-----------|-------------|-----------------|
| `FILLED` | Parcialmente ejecutada | symbol, filled_price, filled_qty, side, order_type |
| `FINAL_FILLED` | Completamente ejecutada | Idem + filled_qty total |
| `PLACE_FAILED` | Orden fallida | Motivo del fallo |
| `MODIFY_SUCCESS` | Modificacion exitosa | Nuevos parametros |
| `MODIFY_FAILED` | Modificacion fallida | Motivo |
| `CANCEL_SUCCESS` | Cancelacion exitosa | — |
| `CANCEL_FAILED` | Cancelacion fallida | Motivo |

**Campos en el evento:**

| Campo | Descripcion |
|-------|-------------|
| `request_id` | ID de la solicitud |
| `account_id` | ID de cuenta (hash) |
| `client_order_id` | ID definido por el cliente |
| `order_id` | ID de orden en Webull |
| `instrument_id` | ID del instrumento |
| `order_status` | SUBMITTED, FILLED, FAILED, CANCELLED |
| `symbol` | Ticker |
| `qty` | Cantidad original |
| `filled_price` | Precio de ejecucion |
| `filled_qty` | Cantidad ejecutada |
| `filled_time` | Timestamp ISO 8601 de ejecucion |
| `side` | BUY / SELL |
| `scene_type` | Tipo de evento |
| `category` | US_STOCK, etc. |
| `order_type` | LIMIT, MARKET, etc. |

### Subscribe Position Events
Tambien disponible — notificaciones de cambios en posiciones (mismo protocolo gRPC).

> **Valor:** Esto te da un feed en tiempo real de CUANDO se ejecutan tus ordenes, a que precio, y que cantidad. Combinado con order book streaming, podes correlacionar tus ejecuciones con el estado del mercado en ese momento exacto.

---

## 4. NOII — Net Order Imbalance (Desequilibrio de Subasta)

Dato exclusivo de **periodos de subasta** (opening y closing auctions).

**Horarios de publicacion:**

| Subasta | Horario (ET) | Duracion | Frecuencia |
|---------|-------------|----------|------------|
| Opening | 9:28 - 9:30 AM | 2 minutos | Cada 5 segundos |
| Closing | 3:50 - 4:00 PM | 10 minutos | Cada 5 segundos |

### NOII Snapshot (`/openapi/market-data/stock/noii/snapshot`)
- Muestra el desequilibrio neto de ordenes (compras vs ventas)
- Precio esperado de match (indicative match price)
- Relacion oferta-demanda en tiempo real

### NOII Bars (`/openapi/market-data/stock/noii/bars`)
- Velas OHLCV del desequilibrio de subasta
- Permite analisis historico de como se comportan las subastas

> **Estrategia:** El NOII te permite ver si hay mas compradores que vendedores (o viceversa) justo antes del open/close. Si ves un desequilibrio masivo a favor de compra en el closing auction, es probable que sean instituciones ajustando posiciones. Este dato es **oro puro** para detectar actividad institucional.

---

## 5. News API

### News Summary (`/openapi/market-data/news/summary`)

**Funcion:** Invoca un **LLM** para generar resumenes de noticias basados en tu watchlist.

**Rate limit:** 10 llamadas/minuto por usuario.

> **Valor:** Podes automatizar el analisis de noticias para tu watchlist. El LLM resume las noticias relevantes, permitiendote reaccionar rapidamente a eventos de mercado sin leer docenas de articulos.

---

## 6. Screener — Datos de Mercado Agregados

### Gainers & Losers (`/openapi/market-data/screener/gainers-losers`)
- Top ganadores y perdedores por `change_ratio`
- Filtrable por direccion (ASC = losers, DESC = gainers)

### Top Active (`/openapi/market-data/screener/top-active`)
- Acciones mas activas rankeadas por:
  - **volume** — Volumen total
  - **relative_volume** — Volumen relativo
  - **turnover** — Rotacion
  - **turnover_rate** — Tasa de rotacion
  - **amplitude** — Amplitud del movimiento
- Campo exclusivo: `relative_volume_10d` (volumen relativo a 10 dias)

> **Estrategia:** Usa `top_active` con `relative_volume_10d > 2.0` para encontrar acciones con actividad anormal HOY. Esto es un proxy para detectar donde estan operando las ballenas.

---

## 7. Account API — Datos de Cuenta

### Account Balance
Campos disponibles (segun documentacion): balance, buying power, cash details.

### Account Positions
- Holdings actuales
- Cantidad, precio promedio, P&L

### Account List
- Lista todas las cuentas (stock, options, futures, crypto pueden tener IDs separados)

---

## 8. Watchlist API

Gestion completa de watchlists programaticamente:
- `watchlist_list` — Listar todas
- `watchlist_create` / `watchlist_delete` — Crear/eliminar
- `watchlist_update` — Cambiar nombre/orden
- `watchlist_instruments_list` — Ver instrumentos
- `watchlist_instruments_add/remove/update` — Gestionar instrumentos

---

## 9. Display Solution vs Non-Display Solution

La API de Market Data se divide en dos modos:

| Modo | Uso | Quien |
|------|-----|-------|
| **Display Solution** | Mostrar datos a usuarios finales (UI) | Brokers, plataformas |
| **Non-Display Solution** | Uso interno, algoritmos, backtesting | Quants, traders algoritmicos |

Nosotros caemos en **Non-Display Solution**.

---

## 10. Rate Limits Detallados

| API | Limite |
|-----|--------|
| Market Data HTTP | 300 req/min (documentacion guias) / 600 req/min (referencia API) |
| Options Market Data | 60 req/min |
| Account Balance | 2 req/2s |
| Account Positions | 2 req/2s |
| Preview Order | 150 req/10s |
| Place Order | 600 req/60s |
| Replace/Cancel Order | 600 req/60s |
| Order History | 2 req/2s |
| Open Orders | 2 req/2s |
| Order Detail | 2 req/2s |
| Streaming Subscribe/Unsubscribe | 1 req/s por App Key |
| News Summary | 10 req/min por usuario |
| Historical Bars (batch) | 1 req/s por App Key |
| Instruments | 10 req/30s |

---

## Resumen de Datos Nuevos Descubiertos

| Dato | Disponible | Utilidad |
|------|-----------|----------|
| NOII (subasta) | **SI** | Detectar actividad institucional en open/close |
| Streaming MQTT | **SI (prod)** | Order book en tiempo real sin polling |
| Trade events gRPC | **SI** | Notificaciones instantaneas de ejecuciones |
| Position events gRPC | **SI** | Cambios en posiciones en tiempo real |
| News con LLM | **SI** | Resumenes automaticos de noticias |
| Screener (top active) | **SI** | Detectar acciones con volumen anormal |
| relative_volume_10d | **SI** | Comparar volumen hoy vs 10 dias |
| Overnight trading data | **SI** | Datos de sesion nocturna |
| Extended hours data | **SI** | Pre-market y after-hours |
| Watchlist programatica | **SI** | Gestionar listas de seguimiento |
| Campos snapshot | **SI** | open, high, low, close, volume, change, change_ratio |
| Precios como strings | **SI** | Precision total, sin redondeo |

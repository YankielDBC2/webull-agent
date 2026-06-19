# Paper Trading — Rate Limits y Arquitectura

> **Fecha:** 2026-06-19 | **Objetivo:** Definir los rate limits de la API, planificar el presupuesto de peticiones, y disenar un paper trading que simule fees reales sin usar cuenta real.

---

## 1. Rate Limits por Endpoint

### Market Data API (HTTP)

| Endpoint | Rate Limit | Ventana | Notas |
|----------|-----------|---------|-------|
| `stock_snapshot` | 600 | por minuto | Soporta batch (multiples simbolos en 1 request) |
| `stock_bars` | — | — | 1 req/s por App Key (batch tambien) |
| `stock_batch_bars` | — | — | Varios simbolos en 1 request |
| `stock_tick` | 600 | por minuto | Tick-by-tick |
| `stock_quotes` | 600 | por minuto | Order book depth |
| `stock_footprint` | 600 | por minuto | Order flow |
| `stock_noii_snapshot` | 600 | por minuto | Subasta, solo en horarios especificos |
| `stock_noii_bars` | 600 | por minuto | Velas de subasta |
| `stock_gainers_losers` | 600 | por minuto | Screener |
| `stock_most_active` | 600 | por minuto | Screener |
| `option_snapshot` | **60** | por minuto | ⚠️ Mas restrictivo |
| `option_tick` | **60** | por minuto | ⚠️ Mas restrictivo |
| `option_bars` | — | — | 1 req/s por App Key |
| `futures_snapshot` | 600 | por minuto | — |
| `futures_bars` | — | — | — |
| `futures_depth` | 600 | por minuto | — |
| `crypto_snapshot` | 600 | por minuto | — |
| `crypto_bars` | — | — | — |
| `event_snapshot` | 600 | por minuto | — |
| `get_instruments` | 10 | cada 30s | Info de instrumentos |
| `news_summary` | 10 | por minuto **por usuario** | LLM summaries |

### Trading API (HTTP)

| Endpoint | Rate Limit | Ventana |
|----------|-----------|---------|
| `account_list` | 10 | cada 30s |
| `account_balance` | 2 | cada 2s |
| `account_positions` | 2 | cada 2s |
| `preview_order` | 150 | cada 10s |
| `place_order` | **600** | cada 60s |
| `batch_place_orders` | **600** | cada 60s |
| `replace_order` | **600** | cada 60s |
| `cancel_order` | **600** | cada 60s |
| `order_history` | 2 | cada 2s |
| `open_orders` | 2 | cada 2s |
| `order_detail` | 2 | cada 2s |

### Streaming (MQTT)

| Endpoint | Rate Limit | Ventana |
|----------|-----------|---------|
| `subscribe` | **1** | por segundo (por App Key) |
| `unsubscribe` | **1** | por segundo (por App Key) |

### Trade Events (gRPC)

- Conexion persistente — no aplica rate limit HTTP
- 1 conexion gRPC por cuenta

---

## 2. Presupuesto de Peticiones para Paper Trading

### Objetivo: Operar 10 stocks simultaneamente

Asumiendo **1 request = 1 snapshot con hasta 20 simbolos** (batch), o requests individuales.

### Estrategia A — Conservadora (solo HTTP, sin streaming)

| Operacion | Frecuencia | Requests/min | % del limite (600) |
|-----------|-----------|-------------|---------------------|
| Snapshot batch (10-20 simbolos) | Cada 5 segundos | 12 | 2% |
| Quotes (order book, 10 simbolos) | Cada 10 segundos | 6 | 1% |
| Screener (top active) | Cada 5 minutos | 0.2 | ~0% |
| Account balance | Cada 60 segundos | 1 | N/A (limite 2/2s) |
| Account positions | Cada 60 segundos | 1 | N/A (limite 2/2s) |
| Historical bars (1 simbolo) | Bajo demanda | ~2 | N/A (limite 1/s) |
| **TOTAL** | | **~22 req/min** | **3.7% del limite** |

> **Conclusion:** Con HTTP puro, tenes margen para **27x mas** peticiones antes de llegar al limite de 600/min. Podes hacer snapshot cada 1 segundo (60 req/min, 10% del limite) sin problemas.

### Estrategia B — Agresiva con Streaming MQTT (produccion)

| Operacion | Frecuencia | Requests/min |
|-----------|-----------|-------------|
| Streaming MQTT (quotes 10 simbolos) | Tiempo real, 0 requests HTTP | 0 |
| Snapshot batch (precio de referencia) | Cada 30 segundos | 2 |
| Screener | Cada 5 minutos | 0.2 |
| Account | Cada 60 segundos | 2 |
| Historical bars | Bajo demanda | ~2 |
| **TOTAL** | | **~6 req/min** |

> Con streaming MQTT, los quotes y snapshots llegan por push sin consumir rate limit HTTP. El 99% del limite queda libre para ordenes y consultas bajo demanda.

---

## 3. Fees Reales de Webull (a simular en Paper Trading)

### Opciones sobre acciones (equity options)

| Fee | Monto | Cuando |
|-----|-------|--------|
| **Comision Webull** | **$0.00** | Siempre |
| Index options | $0.50/contrato | Solo index options |
| Oversized option orders | $0.10/contrato | Ordenes > cierto tamaño |
| **SEC Fee** | $0.0000206 × total trade | **Solo sells** |
| **FINRA TAF** | $0.000195 × total trade (min $0.01, max $9.79) | **Solo sells** |
| **CAT Fee** | $0.000003 × total trade | Buys y sells |

### Calculo practico para opciones (1 contrato, stock a $15)

```
Compra 1 CALL de SOFI:
  Prima: $0.50 × 100 = $50.00
  CAT Fee: 0.000003 × 100 shares = $0.0003 (redondea a $0.00)
  --------------------------------------------
  Costo total entrada: $50.00

Venta 1 CALL de SOFI:
  Venta: $0.80 × 100 = $80.00
  SEC Fee: 0.0000206 × 100 = $0.002 (~$0.00)
  FINRA TAF: 0.000195 × 100 = $0.0195 → $0.01 (minimo)
  CAT Fee: 0.000003 × 100 = $0.0003 (~$0.00)
  --------------------------------------------
  Neto salida: $80.00 - $0.01 = $79.99
  Ganancia: $79.99 - $50.00 = $29.99
```

> **Simplificacion para paper trading:** Asumir **$0.00 fees en buys** y **$0.02 fees en sells** (redondeando los regulatory fees para contratos pequenos).

### Fees para stocks

| Fee | Monto | Cuando |
|-----|-------|--------|
| Comision | $0.00 | Siempre |
| SEC Fee | $0.0000206 × total | Solo sells |
| FINRA TAF | $0.000195 × total (min $0.01, max $9.79) | Solo sells |
| CAT Fee | $0.000003 × total | Buys y sells |

---

## 4. Arquitectura del Paper Trading

```
┌─────────────────────────────────────────────────────┐
│                  PAPER TRADING ENGINE                │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────┐   ┌──────────┐   ┌──────────────────┐ │
│  │ Market   │   │ Position │   │ Fee Calculator   │ │
│  │ Data     │   │ Manager  │   │ (simula fees     │ │
│  │ Polling  │   │ (virtual │   │  reales de SEC,  │ │
│  │ (HTTP o  │   │  P&L)    │   │  FINRA, CAT)     │ │
│  │  MQTT)   │   │          │   │                  │ │
│  └────┬─────┘   └────┬─────┘   └────────┬─────────┘ │
│       │              │                  │           │
│       └──────────────┼──────────────────┘           │
│                      │                              │
│              ┌───────┴────────┐                     │
│              │  Order Engine  │                     │
│              │  (simula fill  │                     │
│              │   a precio     │                     │
│              │   bid/ask)     │                     │
│              └───────┬────────┘                     │
│                      │                              │
│              ┌───────┴────────┐                     │
│              │  Risk Manager  │                     │
│              │  (stop loss,   │                     │
│              │   max daily    │                     │
│              │   loss, etc.)  │                     │
│              └───────┬────────┘                     │
│                      │                              │
│              ┌───────┴────────┐                     │
│              │  Journal       │                     │
│              │  (log de cada  │                     │
│              │   operacion)   │                     │
│              └────────────────┘                     │
└─────────────────────────────────────────────────────┘
```

### Componentes

**1. Market Data Polling**
- Obtiene snapshots y quotes cada N segundos
- Almacena en buffer circular para backtesting
- Detecta cambios de precio significativos

**2. Position Manager**
- Mantiene posiciones virtuales (JSON/SQLite local)
- Calcula P&L en tiempo real (mark-to-market con ultimo bid/ask)
- Track: entry_price, current_price, fees_paid, unrealized_pnl, realized_pnl

**3. Fee Calculator**
- Simula exactamente los fees de Webull
- Compra: $0.000003 × shares (CAT)
- Venta: SEC + FINRA + CAT
- Redondea a $0.01 (minimo FINRA)

**4. Order Engine**
- Simula ejecucion a precio bid (sell) o ask (buy)
- Slippage configurable (ej: 0.5% en market orders)
- Time-in-force: simulacion de DAY y GTC

**5. Risk Manager**
- Max loss diario configurable
- Max posiciones abiertas simultaneas
- Stop loss y take profit automaticos
- Alerta si el spread es demasiado alto (poca liquidez)

**6. Journal**
- Registra cada trade: timestamp, symbol, side, qty, price, fees, pnl
- Exportable a CSV para analisis
- Estadisticas: win rate, avg win/loss, profit factor, sharpe ratio

---

## 5. Plan de Implementacion por Fases

### Fase 1 — Solo consulta (sin cuenta real, sin API key propia)

```python
# Usar el entorno TEST de Webull (credenciales publicas)
# Solo lectura: snapshots, quotes, historical bars
# Sin ordenes reales ni virtuales aun
```

**Peticiones necesarias:**
- 1 snapshot batch cada 5s para 10 simbolos = 12 req/min
- 1 screener cada 5min = 0.2 req/min
- Total: ~13 req/min → **2% del limite**

### Fase 2 — Paper trading virtual (local)

```python
# Motor local que simula ordenes
# Sin tocar la API de trading (solo market data)
# Journal en SQLite local
```

**Peticiones necesarias:**
- Igual que Fase 1 + quotes cada 10s para spreads = 6 req/min extra
- Total: ~19 req/min → **3% del limite**

### Fase 3 — Streaming (produccion, requiere API key propia)

```python
# MQTT streaming para quotes en tiempo real
# Ordenes virtuales con datos live
# Preparado para Fase 4 (real)
```

**Peticiones necesarias:**
- MQTT: 0 req/min (streaming)
- HTTP solo para account y bajo demanda
- Total: ~5 req/min → **<1% del limite**

### Fase 4 — Real (cuando estes listo)

```python
# Activar place_order real
# Mantener el paper trading como validador/simulador
```

---

## 6. Resumen de Capacidad

| Metrica | Valor |
|---------|-------|
| Rate limit HTTP total | **600 req/min** |
| Consumo Fase 1 (consulta) | ~13 req/min (2%) |
| Consumo Fase 2 (paper) | ~19 req/min (3%) |
| Consumo Fase 3 (streaming) | ~5 req/min (<1%) |
| Margen para ordenes | **581–595 req/min libres** |
| Simbolos monitoreables | **20–50 simultaneos** sin problemas |
| Frecuencia snapshot | Cada **1–5 segundos** seguro |
| Streaming MQTT | **Ilimitado** (no consume rate limit HTTP) |
| Options data | **60 req/min** (10% del limite general, suficiente) |

> **Conclusin clave:** Los rate limits de Webull son **extremadamente generosos** para paper trading. Podes monitorear 50+ simbolos con snapshot cada 1 segundo y aun asi usar <10% del limite. El unico cuello de botella real es options data (60/min) pero incluso eso alcanza para seguir 10-20 contratos activos.

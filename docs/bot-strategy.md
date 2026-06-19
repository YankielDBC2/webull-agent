# Estrategia del Bot — Paper Trading con Webull + Telegram

> **Fecha:** 2026-06-19 | **Version:** 0.1.0

---

## Objetivo

Bot de monitoreo en tiempo real de 10 stocks (extensible) usando la API de Webull (entorno test → paper trading → real). Comunicacion de logs, alertas y estadisticas via canal de Telegram.

---

## Arquitectura General

```
┌────────────────────────────────────────────────────────────┐
│                     MAIN LOOP (async)                      │
│                     cada 5 segundos                        │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐     ┌──────────────────┐              │
│  │ WebullClient    │────▶│ MarketDataEngine │              │
│  │ (HTTP HMAC)     │     │ - snapshots       │              │
│  │ test endpoint   │     │ - quotes (bid/ask)│              │
│  └─────────────────┘     │ - spreads          │              │
│                          │ - change %        │              │
│                          └────────┬─────────┘              │
│                                   │                        │
│                          ┌────────┴─────────┐              │
│                          │ AlertEngine      │              │
│                          │ - price alerts   │              │
│                          │ - volume spikes  │              │
│                          │ - spread alerts  │              │
│                          └────────┬─────────┘              │
│                                   │                        │
│                          ┌────────┴─────────┐              │
│                          │ TelegramReporter │              │
│                          │ - status reports │              │
│                          │ - alerts push    │              │
│                          │ - hourly summary │              │
│                          └────────┬─────────┘              │
│                                   │                        │
│                         ┌────────┴─────────┐              │
│                         │ CANAL TELEGRAM   │              │
│                         │ -1002372286698   │              │
│                         └──────────────────┘              │
└────────────────────────────────────────────────────────────┘
```

---

## Stocks Iniciales (Tier 1)

```python
WATCHLIST = [
    "SOFI",   # SoFi Technologies — FinTech
    "F",      # Ford Motor — Automotriz
    "NIO",    # NIO Inc — EV Chino
    "SNAP",   # Snap Inc — Redes Sociales
    "AAL",    # American Airlines — Aerolineas
    "CCL",    # Carnival Corp — Cruceros
    "RIVN",   # Rivian Automotive — EV
    "AMC",    # AMC Entertainment — Entretenimiento
    "RIOT",   # Riot Platforms — Crypto Mining
    "MARA",   # MARA Holdings — Crypto Mining
]
```

---

## Datos a Obtener por Cada Stock

### En cada ciclo (cada 5s):

| Dato | Endpoint | Campo |
|------|----------|-------|
| Precio actual | `stock_snapshot` | `price` |
| Cambio % | `stock_snapshot` | `change_ratio` |
| Cambio $ | `stock_snapshot` | `change` |
| Volumen | `stock_snapshot` | `volume` |
| Bid | `stock_quotes?depth=1` | `bid_price` |
| Ask | `stock_quotes?depth=1` | `ask_price` |
| Spread | Calculado | `ask - bid` |
| Spread % | Calculado | `(ask-bid)/price * 100` |
| Maximo del dia | `stock_snapshot` | `high` |
| Minimo del dia | `stock_snapshot` | `low` |
| Apertura | `stock_snapshot` | `open` |
| Cierre anterior | `stock_snapshot` | `pre_close` |

### Cada hora:

| Dato | Endpoint | Campo |
|------|----------|-------|
| Velas 1h | `stock_bars?granularity=H1` | OHLCV ultimas 24h |
| Top gainers/losers | `screener/gainers-losers` | Ranking global |

### Cada dia (opening):

| Dato | Endpoint |
|------|----------|
| NOII (apertura 9:28-9:30 ET) | `stock_noii/snapshot` |
| NOII (cierre 3:50-4:00 ET) | `stock_noii/snapshot` |

---

## Formato de Mensajes Telegram

### 1. Status Report (cada 5 minutos)

```
📊 STATUS 14:35 ET
━━━━━━━━━━━━━━━━━━━━━━
💰 SOFI   $15.42  +2.3%  Vol:12.4M
   Bid:15.41  Ask:15.43  Spread:$0.02
━━━━━━━━━━━━━━━━━━━━━━
🚗 F      $10.15  -0.8%  Vol:45.2M
   Bid:10.14  Ask:10.16  Spread:$0.02
━━━━━━━━━━━━━━━━━━━━━━
...
```

### 2. Alertas (inmediato)

```
🚨 ALERTA VOLUMEN — SOFI
   Volumen: 28.5M (3.2x promedio)
   Precio: $15.42 (+2.3%)
   Spread: $0.02

🚨 ALERTA SPREAD — NIO
   Spread: $0.12 (2.4% del precio)
   Liquidez BAJA — evitar operar
```

### 3. Resumen Horario

```
📈 RESUMEN 15:00 ET
━━━━━━━━━━━━━━━━━━━━━━
Top 3 Gainers:
  1. MARA +4.2%
  2. RIOT +3.8%
  3. CCL  +2.9%

Top 3 Losers:
  1. NIO  -2.1%
  2. SNAP -1.5%
  3. F    -0.8%

Mayor Volumen: F (45.2M)
Menor Spread: SOFI ($0.02)
Mayor Spread: AMC ($0.05)
━━━━━━━━━━━━━━━━━━━━━━
```

### 4. Daily Open/Close

```
🔔 APERTURA — NOII 9:28 ET
   SOFI: Compra +125K vs Venta -80K → 🟢 Alcista
   AMC:  Compra +50K vs Venta -200K → 🔴 Bajista

🔔 CIERRE — NOII 15:50 ET
   MARA: Compra +300K vs Venta -50K → 🟢 Muy Alcista
```

---

## Umbrales de Alerta

| Alerta | Condicion | Prioridad |
|--------|-----------|-----------|
| Volumen anormal | `volume > avg_volume_10d * 2` | Alta |
| Spread alto | `spread_pct > 1.0%` | Media |
| Movimiento brusco | `abs(change_ratio) > 5% en 5min` | Alta |
| Cambio de tendencia | Precio cruza VWAP | Media |
| Soporte/Resistencia | Precio toca high/low del dia | Baja |

---

## Estructura de Archivos del Bot

```
src/
├── bot.py                    # Entry point, main loop
├── webull_client.py          # HTTP client con HMAC signing
├── market_data.py            # Engine de polling y caching
├── alerts.py                 # Deteccion de alertas
├── telegram_reporter.py      # Formateo y envio a Telegram
├── config.py                 # Carga de .env y constantes
└── utils.py                  # Helpers (logging, timing)

config/
├── .env                      # Credenciales (NO COMMITEAR)
└── watchlist.json            # Lista de stocks monitoreados

data/                          # Datos cacheados (gitignore)
├── snapshots.db              # SQLite con historico de snapshots
└── logs/                     # Logs del bot
```

---

## Configuracion (.env)

```env
# Webull Test
WEBULL_APP_KEY=a88f2efed4dca02b9bc1a3cecbc35dba
WEBULL_APP_SECRET=c2895b3526cc7c7588758351ddf425d6
WEBULL_ENVIRONMENT=uat
WEBULL_REGION_ID=us
WEBULL_API_HOST=us-openapi-alb.uat.webullbroker.com

# Telegram
TELEGRAM_BOT_TOKEN=8970074756:AAHA5gyiY8XEBoQGcwOAzJ2e8nLBxbqU32c
TELEGRAM_CHANNEL_ID=-1002372286698

# Bot Settings
POLL_INTERVAL_SECONDS=5
REPORT_INTERVAL_MINUTES=5
HOURLY_SUMMARY=true
```

---

## Plan de Implementacion

### Semana 1: Fundacion
- [x] `webull_client.py` — HTTP client con HMAC signing ✅
- [x] `config.py` — Carga de .env ✅
- [x] Verificar conexion con test endpoint ✅
- [x] `market_data.py` — Obtener snapshot de 1 stock ✅
- [x] `telegram_reporter.py` — Enviar primer mensaje al canal ✅
- [ ] Solicitar API key de produccion (para desbloquear 10 stocks)

### Semana 2: Core
- [ ] Main loop con 10 stocks (requiere API key prod)
- [ ] Status reports cada 5 minutos
- [ ] Alertas de volumen y spread
- [ ] Resumen horario
- [ ] SQLite para cache de datos

### Semana 3: Optimizacion
- [ ] Batch requests (1 request = 10+ simbolos)
- [ ] NOII en horarios de subasta
- [ ] Calculo de VWAP y volumen promedio
- [ ] Graficos ASCII en Telegram (velas, tendencia)

### Semana 4: Paper Trading
- [ ] Motor de ordenes virtuales
- [ ] Simulacion de fees
- [ ] Journal de operaciones
- [ ] P&L tracking

---

## ⚠️ Restriccion del Entorno Test

El entorno UAT compartido **solo permite consultar AAPL**. Los demas simbolos devuelven `403 INVALID_SYMBOL`. Esto es normal — es un sandbox.

**Para desbloquear los 10 stocks:**
1. Solicitar API key de produccion en https://www.webull.com/open-api
2. Cambiar `WEBULL_ENVIRONMENT=prod` en .env
3. Cambiar `WEBULL_API_HOST=api.webull.com`

**Verificacion actual:**
- ✅ Webull test conectado — Account list OK (2 cuentas)
- ✅ Snapshot AAPL funcionando — $298.01, Vol:85.9M, +0.70%
- ✅ Telegram conectado — mensaje de prueba enviado
- ⏳ 10 stocks — esperando API key de produccion

---

## Rate Limits — Consumo del Bot

Con 10 stocks en batch (1 request snapshot + 1 request quotes cada 5s):

| Operacion | Reqs/min | % Limite |
|-----------|----------|----------|
| Snapshot (batch 10) | 12 | 2% |
| Quotes (batch 10) | 12 | 2% |
| Screener | 0.2 | ~0% |
| Telegram envio | N/A | N/A |
| **TOTAL** | **24.2** | **4%** |

> **596 req/min libres** para futuras funcionalidades.

---

## Rollback

- Cada fase tiene su propio branch en git
- `git revert` para deshacer cambios especificos
- `.env` nunca se commitea (backup manual)
- SQLite local se puede borrar y regenerar

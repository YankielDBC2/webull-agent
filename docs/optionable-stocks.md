# Stocks para Operar Opciones con Presupuesto Reducido ($100 USD)

> **Fecha:** 2026-06-19 | **Objetivo:** Lista de stocks populares con alto volumen diario cuyos contratos de opciones sean accesibles con ~$100 USD por operacion.

---

## Regla de Presupuesto

- **1 contrato de opcion = 100 acciones**
- **Costo = Prima × 100**
- Para $100 USD → necesitas primas ≤ **$1.00** por contrato
- Ideal: contratos con primas de **$0.10–$0.50** para poder operar 2-5 contratos
- Buscar opciones **ATM o ligeramente OTM** a 7-30 dias de expiracion

---

## Lista de Stocks (15+ Seleccionados)

### Tier 1 — Mejor ajuste (precio accion < $20, opciones baratas, alto volumen)

| # | Ticker | Nombre | Precio ~ | Sector | Vol. Opciones | Prima ATM 7d ~ |
|---|--------|--------|----------|--------|---------------|-----------------|
| 1 | **SOFI** | SoFi Technologies | $15 | FinTech | Muy Alto | $0.40–0.80 |
| 2 | **F** | Ford Motor | $10 | Automotriz | Alto | $0.20–0.50 |
| 3 | **NIO** | NIO Inc (EV Chino) | $5 | EV | Muy Alto | $0.10–0.30 |
| 4 | **SNAP** | Snap Inc | $12 | Redes Sociales | Alto | $0.30–0.70 |
| 5 | **AAL** | American Airlines | $15 | Aerolineas | Alto | $0.30–0.70 |
| 6 | **CCL** | Carnival Corp | $18 | Cruceros | Alto | $0.40–0.80 |
| 7 | **RIVN** | Rivian Automotive | $12 | EV | Alto | $0.30–0.70 |
| 8 | **AMC** | AMC Entertainment | $5 | Entretenimiento | Extremo | $0.10–0.40 |
| 9 | **RIOT** | Riot Platforms | $10 | Crypto Mining | Muy Alto | $0.20–0.50 |
| 10 | **MARA** | MARA Holdings | $15 | Crypto Mining | Muy Alto | $0.40–0.80 |

### Tier 2 — Buen ajuste (precio accion $20–40, opciones accesibles)

| # | Ticker | Nombre | Precio ~ | Sector | Vol. Opciones |
|---|--------|--------|----------|--------|---------------|
| 11 | **PLTR** | Palantir Technologies | $25 | Data/AI | Extremo |
| 12 | **INTC** | Intel Corp | $30 | Semiconductores | Muy Alto |
| 13 | **T** | AT&T | $20 | Telecom | Alto |
| 14 | **PFE** | Pfizer | $28 | Farmaceutica | Alto |
| 15 | **GME** | GameStop | $25 | Videojuegos | Extremo |
| 16 | **BAC** | Bank of America | $35 | Banca | Muy Alto |
| 17 | **WBD** | Warner Bros Discovery | $10 | Media | Alto |

### Tier 3 — Mayor precio pero alta liquidez (monitorear)

| # | Ticker | Nombre | Precio ~ | Nota |
|---|--------|--------|----------|------|
| 18 | **UBER** | Uber Technologies | $70 | Alto volumen opciones, spreads semanales |
| 19 | **DKNG** | DraftKings | $45 | Muy popular en opciones |
| 20 | **AAPL** | Apple | $200+ | Mejor para credit spreads con $100 |

---

## Criterios de Seleccion

| Criterio | Valor minimo | Como verificarlo via API |
|----------|-------------|--------------------------|
| Volumen diario del stock | > 10M shares | `stock_snapshot` → campo `volume` |
| Open interest en opciones | > 1,000 contratos | `option_snapshot` (requiere suscripcion) |
| Spread bid/ask | < $0.05 ideal | `stock_quotes` → comparar bid vs ask |
| Precio de la accion | < $50 (ideal < $20) | `stock_snapshot` → campo `price` |
| Volatilidad (IV) | 30–80% | No disponible via API (calcular manualmente) |
| Volumen relativo | > 1.5x promedio | `get_top_active` → `relative_volume_10d` |

---

## Estrategia de Verificacion API

Cuando tengamos acceso a la API, ejecutar este flujo:

### 1. Obtener acciones mas activas del dia
```
GET /openapi/market-data/screener/top-active?rank_by=volume&limit=50
```
→ Filtrar por `relative_volume_10d > 1.5`

### 2. Verificar precio y volumen de cada candidato
```
GET /openapi/market-data/stock/snapshot?symbols=SOFI,F,NIO,SNAP,AAL,CCL,RIVN,AMC,RIOT,MARA,PLTR,INTC,T,PFE,GME,BAC,WBD
```
→ Quedarse con `price < 50` y `volume > 10000000`

### 3. Verificar spreads (liquidez de opciones)
```
GET /openapi/market-data/stock/quotes?symbols=...&depth=1
```
→ Spread = ask_price - bid_price. Buscar < $0.05

### 4. (Cuando disponible) Verificar opciones
```
GET /openapi/market-data/option/snapshot?option_codes=...
```
→ Chequear open_interest > 1000, volumen de opciones alto

---

## Script de Actualizacion Diaria (Plan)

```python
# Pseudocodigo del futuro script
candidates = [
    "SOFI", "F", "NIO", "SNAP", "AAL", "CCL", "RIVN", "AMC", "RIOT", "MARA",
    "PLTR", "INTC", "T", "PFE", "GME", "BAC", "WBD", "UBER", "DKNG"
]

# 1. Obtener snapshots
snapshots = api.get_stock_snapshot(candidates)

# 2. Filtrar por volumen (> 10M) y precio (< 50)
filtered = [s for s in snapshots if s.volume > 10_000_000 and s.price < 50]

# 3. Para los filtrados, obtener spread
quotes = api.get_stock_quotes([f.symbol for f in filtered], depth=1)
filtered = [q for q in quotes if q.ask - q.bid < 0.05]

# 4. Obtener top active para confirmar relative_volume
active = api.get_top_active(rank_by="volume", limit=50)

# 5. Cruzar y rankear
ranked = cross_reference(filtered, active)
# Output: lista final de 5-10 mejores para el dia
```

---

## Notas Importantes

- **El mercado cambia:** Esta lista debe refrescarse diariamente con datos reales de la API
- **Eventos:** Evitar operar opciones en dias de earnings (riesgo de IV crush)
- **Horario:** Mejor liquidez en opciones entre 10:00 AM–3:30 PM ET
- **Vencimiento:** Preferir 7-14 dias para balance theta/premium
- **Griegos:** Calcular delta, theta, gamma manualmente (no disponibles via API aun)
- **Earnings:** Verificar calendario de earnings antes de entrar (NOII puede ayudar)

---

## Verificacion Post-API Key

Cuando tengamos la API key, ejecutar `scripts/daily-stock-screener.py` (a crear) que:
1. Consulte top active del dia
2. Filtre por precio y volumen
3. Verifique spreads
4. Output: tabla markdown con los 10 mejores candidatos del dia listos para copiar

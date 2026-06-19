# Investigacion: Datos y Estadisticas de Contratos en Webull API

> **Fecha:** 2026-06-19 | **Proposito:** Determinar que datos y estadisticas podemos obtener de las APIs de Webull enfocados en contratos (opciones, futuros, event contracts).

---

## 1. Informacion de Contratos

### Opciones

| Aspecto | Disponible | Detalle |
|---------|-----------|---------|
| Trading de opciones | **SI** | 12 estrategias: SINGLE, COVERED_STOCK, VERTICAL, STRADDLE, STRANGLE, CALENDAR, BUTTERFLY, CONDOR, IRON_BUTTERFLY, IRON_CONDOR, COLLAR_WITH_STOCK, DIAGONAL |
| Tipos de orden | **SI** | LIMIT, STOP_LOSS, STOP_LOSS_LIMIT |
| Market data de opciones | **SI (pago)** | Tick, Snapshot, Historical Bars. Requiere suscripcion paga (en desarrollo activo) |
| Datos del contrato | **SI** | strike_price, option_expire_date, option_type (CALL/PUT), symbol subyacente |
| Combo orders | **SI** | OTO, OCO, OTOCO para opciones |
| Take-Profit / Stop-Loss | **SI** | En opciones |

### Futuros

| Aspecto | Disponible | Detalle |
|---------|-----------|---------|
| Trading de futuros | **SI** | Market, Limit, Stop Loss, Stop Loss Limit, Trailing Stop Loss |
| Market data | **SI** | Tick, Snapshot, Depth of Book, Footprint, Historical Bars |
| Productos | **SI** | Index, interest rate, currency, agriculture, metals, energy, crypto futures |
| Open interest | **SI** | Incluido en futures snapshot |
| 24/6 trading | **SI** | Near 24/6 |

### Event Contracts

| Aspecto | Disponible | Detalle |
|---------|-----------|---------|
| Trading | **SI** | Limit orders, fractional shares |
| Market data | **SI** | Snapshot, Depth, Bars, Tick |
| Categorias | **SI** | Economics, politics, sports, etc. |
| Sin suscripcion adicional | **SI** | No requiere pago extra |

---

## 2. Volumen, Ordenes Limite, Liquidez, Muros de Ordenes

### Volumen

| Endpoint | Que ofrece |
|----------|-----------|
| `stock_snapshot` | Volume, turnover rate |
| `stock_tick` | Tick-by-tick: trade time, price, **volume**, direction |
| `option_snapshot` | Trading volume, turnover rate |
| `stock_historical_bars` | OHLCV — Volume incluido en cada vela |
| `futures_snapshot` | Open interest (indicador de liquidez) |
| `stock_most_active` | Ranked by volume, relative volume, turnover, turnover rate, amplitude |
| `relative_volume_10d` | Campo unico del endpoint Top Active |

### Ordenes Limite y Muros (Order Book)

| Endpoint | Que ofrece |
|----------|-----------|
| `stock_quotes` | **Bid/Ask a profundidad especifica**: price, quantity, **order details** (numero de ordenes en cada nivel) |
| `futures_depth` | Market depth / order book para futuros |
| `event_depth` | Order book depth para event contracts |

> **Conclusin sobre muros:** El endpoint `quotes` devuelve datos de order book con "order details" a profundidad configurable. Esto permite **detectar muros de ordenes** (grandes cantidades de ordenes limite en un nivel de precio) y **monitorear como se van comiendo/rellenando** comparando snapshots sucesivos del order book. Sin embargo, NO hay un endpoint especifico de "order flow en tiempo real" que muestre cuando una orden grande entra al book — tendrias que hacer polling del endpoint `quotes` y detectar cambios.

### Footprint / Order Flow

| Endpoint | Que ofrece |
|----------|-----------|
| `stock_footprint` | Analisis de **order flow** y perfil de volumen. Consulta los N registros mas recientes basados en simbolo, categoria y granularidad temporal |
| `futures_footprint` | Order flow y perfil de volumen para futuros |

> **Conclusin:** El footprint permite analizar el flujo de ordenes — donde se estan ejecutando las ordenes grandes, que niveles de precio estan siendo "comidos", etc. Es la herramienta mas cercana a detectar actividad de "whales".

---

## 3. Identificacion de Ordenes por Usuario

**NO ES POSIBLE.**

Las APIs de Webull no exponen identidad de usuarios. Los datos de mercado son anonimos:
- Tick data muestra: tiempo, precio, volumen, direccion (buy/sell) — sin ID de usuario
- Quotes muestra: precio, cantidad, numero de ordenes en el nivel — sin identidad
- Footprint muestra: flujo agregado — sin identidad

**Fundamento legal/privacy:** Los brokers regulados por SEC/FINRA no pueden exponer datos PII de sus clientes via APIs publicas.

---

## 4. Identificacion de Whales (Ordenes de Alto Volumen)

**NO se puede identificar usuarios o cuentas especificas.**

**PERO se puede INFERIR actividad de whales mediante:**

| Metodo | Como funciona |
|--------|---------------|
| **Footprint** | Analiza donde se ejecutan ordenes de gran tamaño. Si ves volumen desproporcionado en ciertos niveles de precio, es probable actividad institucional/whale |
| **Quotes (order book)** | Monitorea cambios en el depth. Si aparece/desaparece una orden de 10,000+ contratos en un nivel, es una ballena colocando/retirando liquidez |
| **Tick data** | Transacciones individuales con volumen anormalmente alto en relacion al volumen promedio |
| **Volume spike detection** | Comparar volumen en tiempo real vs volumen promedio historico (requiere calculo propio) |
| **NOII (auction imbalance)** | Muestra desequilibrios de subasta que pueden indicar ordenes institucionales grandes antes del open/close |

> **Estrategia de deteccion:** Combinando polling frecuente del order book (`quotes`) + tick data + footprint, se puede construir un sistema que detecte actividad anomala de alto volumen. No sabras QUIEN, pero sabras DONDE y CUANTO.

---

## 5. Identificacion de Instituciones

**NO directamente.** No hay endpoint para "listar instituciones activas".

**PERO hay diferenciacion por niveles de acceso:**

| Nivel | Quien | APIs |
|-------|-------|------|
| Retail | Inversores individuales | Trading basico, Market Data Level 1 |
| Institucional | Prop traders, hedge funds, family offices | Non-Retail Trading, Advanced Orders, HF Push, Level-2 Depth |
| FinTech | Brokers, robo-advisors | Broker API completa + Trading + Market Data |

**Inferencia indirecta:**
- Ordenes que usan **algo orders** (TWAP/VWAP/POV) son tipicamente institucionales
- Alto volumen en **subastas** (NOII) suele ser institucional
- Operaciones en horarios de **baja liquidez** con alto volumen son sospechosas de ser institucionales
- Uso de **Level 2 depth** y **high-frequency push** es casi exclusivamente institucional

---

## 6. Horarios de Mayor Liquidez

**NO hay un endpoint directo que devuelva "horarios de liquidez".**

**PERO se puede CALCULAR analizando datos historicos:**

| Metodo | Datos necesarios |
|--------|-----------------|
| Analisis de volumen por hora | `historical_bars` con granularidad M1, M5, M15 |
| Densidad de ticks | `tick` data agregado por franja horaria |
| Spread bid/ask por hora | `quotes` snapshots periodicos |
| Profundidad de order book por hora | `quotes` con depth configurable |

**Periodos conocidos de alta liquidez (mercado US):**
- **Open:** 9:30–10:30 AM ET (mayor volumen del dia)
- **Close:** 3:00–4:00 PM ET (segundo pico)
- **Overnight:** 8:00 PM–4:00 AM ET (baja liquidez, disponible via API)
- **Pre-market:** 4:00–9:30 AM ET
- **After-hours:** 4:00–8:00 PM ET

> El endpoint `snapshot` soporta inclusion de datos pre-market, after-hours y overnight.

---

## 7. Greeks (Delta, Gamma, Theta, Vega, Rho)

**ESTADO: INCIERTO / PROBABLEMENTE LIMITADO.**

Evidencia:
- La **pagina principal** de Webull menciona: "free real-time quotes, **Greeks**, and IV for active traders"
- La **App de Webull** muestra Greeks en la interfaz de opciones
- La documentacion del **Option Snapshot API** dice que devuelve: "latest price, price change percentage, trading volume, turnover rate, and best bid/ask quotes"
- **NO menciona Greeks** en los campos devueltos por la API

**Conclusion:** 
- Los Greeks probablemente estan disponibles en la **app de Webull** (frontend) pero **NO estan expuestos via OpenAPI actualmente** (o estaran incluidos en la suscripcion paga de opciones que esta "under active development")
- La suscripcion de market data de opciones via OpenAPI esta en desarrollo — posiblemente incluya Greeks cuando se lance

**Workaround:** Calcular Greeks manualmente usando:
- Precio del subyacente (`stock_snapshot`)
- Strike, expiration, tipo de opcion (de la orden)
- Risk-free rate (externo)
- Dividend yield (externo o `instrument_company_profile`)
- IV (si se puede obtener de `option_snapshot`)
- Formulas Black-Scholes / Binomial

---

## 8. Horarios donde se Mueven Mejor los Greeks

**NO directamente.** No hay datos de Greeks en la API (ver punto 7).

Si los Greeks estuvieran disponibles, se podria analizar su variacion por horario usando:
- `option_snapshot` en intervalos regulares durante el dia
- Correlacionar cambios en Greeks con volumen y precio del subyacente
- Identificar patrones horarios (ej: gamma aumenta cerca del vencimiento, theta acelera en los ultimos dias)

---

## 9. Precios Bid/Ask

**SI, COMPLETAMENTE.**

| Endpoint | Que devuelve |
|----------|-------------|
| `stock_quotes` | Bid/Ask a profundidad configurable: **price, quantity, order details** |
| `option_snapshot` | **Best bid/ask quotes** |
| `futures_depth` | Order book completo con bids y asks |
| `event_depth` | Order book depth con bids y asks |
| `stock_snapshot` | Ultimo precio (no bid/ask directamente, pero si precio de mercado) |

> El endpoint `quotes` es el mas completo: pides depth N y te devuelve N niveles de bid y N niveles de ask con precio, cantidad y numero de ordenes en cada nivel.

---

## 10. Historial para Backtesting

**SI, MUY COMPLETO.**

| Endpoint | Granularidades | Productos |
|----------|---------------|-----------|
| `stock_bars` | **M1, M5, M15, M30, H1, H2, H4, D, W, M** | Stocks, ETFs |
| `stock_batch_bars` | Igual que arriba | Multiples simbolos en una llamada |
| `futures_bars` | Multiples granularidades | Futuros |
| `crypto_bars` | Multiples intervalos | Crypto |
| `option_historical_bars` | M1, M5, etc. | Opciones (requiere suscripcion) |
| `stock_tick` | Tick-by-tick (maxima granularidad) | Stocks |
| `futures_tick` | Tick-by-tick | Futuros |
| `option_tick` | Tick-by-tick | Opciones (requiere suscripcion) |

**Rate Limits:**
- Market Data API: **600 requests/minuto**
- Option endpoints: **60 requests/minuto**
- Historical bars (batch): **1 llamada/segundo por App Key**

**Capacidad de backtesting:**
- Datos OHLCV multi-timeframe para todos los productos
- Datos tick-by-tick para analisis de alta precision
- Consultas batch para multiples simbolos simultaneos
- NOII (desequilibrio de subasta) para estrategias de open/close
- Footprint para analisis de order flow historico
- Screener (gainers/losers, most active) para filtrar universo de backtesting

---

## Resumen General

| Pregunta | Respuesta | Nivel |
|----------|-----------|-------|
| Info de contratos | **SI** | Completo (12 estrategias, futuros, event contracts) |
| Volumen | **SI** | Tick, snapshot, bars incluyen volumen |
| Ordenes limite / muros | **PARCIAL** | Order book depth disponible, pero sin streaming en tiempo real del book completo |
| Ordenes siendo comidas | **PARCIAL** | Detectable via footprint + polling de quotes |
| Identificar usuarios | **NO** | Anonimizado por regulacion |
| Identificar whales | **INFERIBLE** | Via footprint + tick + quotes anormales |
| Identificar instituciones | **INFERIBLE** | Por tipo de orden (algo, size) y nivel de API usado |
| Horarios de liquidez | **CALCULABLE** | Analizando datos historicos de volumen |
| Greeks | **INCIERTO** | App si, API posiblemente no (o en desarrollo) |
| Horarios de Greeks | **NO** | Depende de tener Greeks primero |
| Bid/Ask | **SI** | Order book completo con depth configurable |
| Backtesting | **SI** | OHLCV multi-TF + tick data + batch queries |

### Limitaciones Clave

1. **Opciones market data requiere suscripcion paga** (en desarrollo)
2. **No hay Greeks via API** (posiblemente en la suscripcion futura)
3. **No hay identificacion de usuarios/entidades** (regulacion)
4. **Streaming MQTT** solo disponible en produccion, no en test
5. **Una sola sesion Level 1/Level 2 a la vez** por dispositivo
6. **Rate limits** requieren manejo cuidadoso para estrategias HF

# Seguridad

---

## Principios

- **Nunca compartir** App Key, App Secret o Token en chat, logs o repositorios
- Las credenciales solo deben pasarse via archivo `.env` o variables de entorno
- Usar `preview` siempre antes de colocar ordenes reales

---

## Configuracion de Limites

Agregar al `.env` para limitar la exposicion:

```env
# Limitar valor maximo de orden
WEBULL_MAX_ORDER_NOTIONAL_USD=10000

# Limitar cantidad maxima de shares
WEBULL_MAX_ORDER_QUANTITY=1000

# Restringir simbolos tradeables
WEBULL_SYMBOL_WHITELIST=AAPL,TSLA,MSFT
```

---

## Modo Read-Only

Para que un agente AI solo pueda consultar sin ejecutar trades, usar endpoints de solo lectura:

| Categoria | Endpoints seguros |
|-----------|-------------------|
| Account | `get_account_list`, `get_account_balance`, `get_account_positions` |
| Market Data | Todos los `stock_*`, `futures_*`, `crypto_*`, `event_*` |
| Watchlists | Todos los `watchlist_*` |
| Orders | `get_order_history`, `get_open_orders`, `get_order_detail` (solo lectura) |

---

## Autenticacion

### API Key + App Secret
Cada request se firma con HMAC usando el App Secret.

### Dynamic Token + 2FA
- Segunda capa de seguridad opcional
- Token generado por la app de Webull
- Se cachea localmente y se refresca automaticamente
- **Desconectar en cualquier momento** desde la app

### IP Whitelist
- Autogestionado desde el portal de desarrollador
- Restringe el acceso a IPs especificas

---

## Ordenes

### Preview obligatorio
Siempre usar `preview_*_order` antes de `place_*_order`:
```bash
# Previsualizar (no envia la orden)
webull-skill trading --action preview_stock_order --symbol AAPL --side buy --quantity 10

# Ejecutar (solo despues de revisar el preview)
webull-skill trading --action place_stock_order --symbol AAPL --side buy --quantity 10
```

### Verificacion local
Usar `local-check` para validar parametros de orden sin enviar requests.

---

## Buenas Practicas

1. **`.env` en `.gitignore`** — Nunca commitear credenciales
2. **Rotar API Keys** periodicamente
3. **Auditar logs** regularmente (`WEBULL_AUDIT_LOG_FILE`)
4. **Principio de minimo privilegio** — Solo los endpoints necesarios
5. **Test antes de produccion** — Validar toda la logica en UAT
6. **Monitorear posiciones** activamente
7. **Verificar detalles de orden** antes de ejecutar

---

## Responsabilidad

> Todo trading conlleva riesgo sustancial de perdida. Los agentes AI pueden malinterpretar instrucciones, actuar con datos atrasados o tener mal rendimiento bajo ciertas condiciones de mercado. Webull no asume responsabilidad por perdidas resultantes de decisiones automatizadas o dirigidas por AI. El usuario es el unico responsable de verificar los detalles de orden antes de ejecutar, monitorear activamente sus posiciones y asegurar que cualquier agente, algoritmo o herramienta opere exactamente como se espera.

# Guia de Configuracion

---

## Paso 1: Solicitar acceso a la API

### Cuenta Individual
Solicitar via el portal de Webull: https://www.webull.com/open-api
- El proceso de revision toma 1-2 dias habiles
- Se pueden usar credenciales de test mientras tanto

### Cuenta Institucional
Contactar a Webull directamente para acceso institucional con:
- Trading API (Non-Retail, Advanced Orders)
- Market Data API (High-Frequency Push, Level-2 Depth)

---

## Paso 2: Instalar SDK

```bash
# Python (recomendado)
pip install webull-openapi-python-sdk

# Requiere Python 3.10+
```

Para Java: Agregar `webull-openapi-java-sdk` a dependencias Maven.

---

## Paso 3: Configurar credenciales

Crear archivo `.env` en la raiz del proyecto:

### Entorno de Test (UAT)
```env
WEBULL_APP_KEY=<your_app_key>
WEBULL_APP_SECRET=<your_app_secret>
WEBULL_ENVIRONMENT=uat
WEBULL_REGION_ID=us
```

### Entorno de Produccion
```env
WEBULL_APP_KEY=<your_app_key>
WEBULL_APP_SECRET=<your_app_secret>
WEBULL_ENVIRONMENT=prod
WEBULL_REGION_ID=us
```

### Variables adicionales

| Variable | Default | Descripcion |
|----------|---------|-------------|
| `WEBULL_MAX_ORDER_NOTIONAL_USD` | `10000` | Valor maximo de orden en USD |
| `WEBULL_MAX_ORDER_QUANTITY` | `1000` | Maximo de shares por orden |
| `WEBULL_SYMBOL_WHITELIST` | (none) | Simbolos permitidos (separados por coma) |
| `WEBULL_TOKEN_DIR` | `conf/` | Directorio de almacenamiento de tokens |
| `WEBULL_AUDIT_LOG_FILE` | (stderr) | Archivo de log de auditoria |
| `WEBULL_LOG_LEVEL` | `WARNING` | Nivel de log del SDK |

---

## Paso 4: Verificar conexion

```python
from webull.core.client import ApiClient
from webull.trade.trade_client import TradeClient

api_client = ApiClient("<your_app_key>", "<your_app_secret>", "us")
api_client.add_endpoint("us", "us-openapi-alb.uat.webullbroker.com")

trade_client = TradeClient(api_client)
res = trade_client.account_v2.get_account_list()
print(res.json())
```

Si se recibe la lista de cuentas, la configuracion es correcta.

---

## Paso 5: Autenticacion 2FA (opcional)

Si la cuenta tiene Two-Factor Authentication habilitado:

```bash
webull-skill auth
```

Flujo:
1. Se genera una solicitud 2FA
2. Aprobar en la app de Webull
3. El token se cachea localmente y se auto-refresca

---

## Paso 6: Suscribirse a Market Data

Para recibir datos de mercado en tiempo real es necesaria una suscripcion:
- Guia: https://developer.webull.com/apis/docs/market-data-api/subscribe-quotes
- Level 1 streaming quotes para US market es **gratis**
- Level 2 depth requiere suscripcion paga

---

## Endpoints por Entorno

| Entorno | HTTP API | Trade Events (gRPC) | Market Streaming (MQTT) |
|---------|----------|---------------------|-------------------------|
| Produccion | `api.webull.com` | `events-api.webull.com` | `data-api.webull.com` |
| Test | `us-openapi-alb.uat.webullbroker.com` | `us-openapi-events.uat.webullbroker.com` | — |

---

## Integracion con Asistentes AI

### Cursor
Crear `.cursor/rules/webull.mdc`:
```
# Webull OpenAPI
Cuando necesites consultar datos de mercado o ejecutar trades:
- Trading: webull-skill trading --action <ACCION> [args...]
- Market Data: webull-skill market-data --action <ACCION> [args...]
- Auth: webull-skill auth
```

### Claude Desktop
Agregar el proyecto como working directory. Claude ejecuta comandos shell directamente.

### GitHub Copilot
En Agent Mode, solicitar ejecucion de comandos directamente.

### Cloud MCP (recomendado para no-devs)
1. Ir a https://www.webull.com/agentic
2. Conectar con OAuth
3. URL del servidor: `https://api.webull.com/mcp`
4. Usar lenguaje natural: "Get AAPL latest price", "Buy 10 shares of TSLA"

# API de Gestión de transactions de Pago

Proyecto del curso de **Integración Continua**. Demuestra el uso de **Docker** y su integración con ***Jenkins**.
para construir y comunicar dos contenedores:

- **Contenedor 1 — API:** aplicación en **Python 3.13 + FastAPI**.
- **Contenedor 2 — Base de datos:** **MariaDB**, consumida por la API.

Ambos contenedores se comunican a través de la network interna que usamos para Docker.
El api se conecta a la base de datos usando el nombre del servicio (`db`) como hostname.

> **Gestor de paquetes:** el proyecto usa **uv** en vez de pip.

---

## Descripción funcional

La API administra **commerces** y sus **transactions** de pago simulando una lógica de negocio realista:

- Alta y consulta de commerces.
- Registro de transactions (validando que el commerce exista y esté activo).
- Máquina de estados de la transacción con transiciones controladas:

  ```
  PENDIENTE ──> APROBADA ──> REVERSADA
      │
      └───────> RECHAZADA
  ```

- Resumen agregado por commerce (total aprobado y conteo por estado).

---

## Arquitectura por capas

El código separa responsabilidades para mantenerlo testeable y mantenible:

```
app/
├── api/            # Capa de presentación (routers/endpoints HTTP)
│   ├── deps.py     #   Inyección de dependencias (ensambla servicios)
│   └── v1/
│       ├── router.py
│       └── endpoints/   # commerces, transactions, health (o endpoint de salud)
├── services/       # Capa de negocio (reglas, validaciones, máquina de estados)
├── repositories/   # Capa de acceso a datos (consultas a la BD)
├── models/         # Modelos ORM de SQLAlchemy (tablas)
├── schemas/        # Esquemas Pydantic (validación entrada/salida)
├── core/           # Configuración, conexión a BD, enums, excepciones
└── main.py         # Arranque de la app, lifespan y manejadores de errores
```

Flujo de una petición:
`endpoint → service → repository → modelo ORM → MariaDB`.

---

## Requisitos previos

- Docker y Docker compose.
- (Opcional, solo para desarrollo local sin Docker) [uv](https://docs.astral.sh/uv/)
  y Python 3.13.

---

## Ejecutar el proyecto

1. Copiar el archivo de variables y ajustarlo:

   ```bash
   # Linux / Mac
   cp .env.template .env

   # Windows (PowerShell o CMD)
   copy .env.template .env
   ```

2. Levanta los contenedores:

   ```bash
   docker compose up -d --build
   ```

3. Verifica que ambos contenedores estén arriba y sanos:

   ```bash
   docker compose ps
   ```

4. Abre la documentación interactiva (Swagger UI):

   - http://localhost:8000/docs
   - Health check: http://localhost:8000/api/v1/health

5. Para detener todo:

   ```bash
   docker compose down
   docker compose down -v # Si se quiere eliminar el volumen de la bd tambéin
   ```

> La API espera a que MariaDB reporte estado *healthy* (`depends_on` +
> `healthcheck`) y además reintenta la conexión al arrancar, evitando errores
> de "race condition" típicos al iniciar varios contenedores a la vez.
>
> Dentro del contenedor, las dependencias se instalan con
> `uv sync --frozen --no-dev`, usando exactamente lo fijado en `uv.lock`.

---

## Endpoints principales

| Método | Ruta                                       | Descripción                          |
|--------|--------------------------------------------|--------------------------------------|
| GET    | `/api/v1/health`                           | Estado del servicio y de la BD       |
| POST   | `/api/v1/commerces`                        | Crear commerce                       |
| GET    | `/api/v1/commerces`                        | Listar commerces                     |
| GET    | `/api/v1/commerces/{id}`                   | Obtener commerce                     |
| PATCH  | `/api/v1/commerces/{id}`                   | Actualizar commerce                  |
| GET    | `/api/v1/commerces/{id}/resumen`           | Resumen de transactions             |
| POST   | `/api/v1/transactions`                    | Crear transacción                    |
| GET    | `/api/v1/transactions`                    | Listar (filtra por commerce/estado)  |
| GET    | `/api/v1/transactions/{id}`               | Obtener transacción                  |
| PATCH  | `/api/v1/transactions/{id}/estado`        | Cambiar estado                       |

### Ejemplo rápido (curl)

```bash
# 1) Crear un commerce
curl -X POST http://localhost:8000/api/v1/commerces \
  -H "Content-Type: application/json" \
  -d '{"name": "Tienda La 14", "nit": "900123456-7"}'

# 2) Crear una transacción (usa el id devuelto arriba)
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{"commerce_id": 1, "monto": "50000.00"}'

# 3) Aprobar la transacción
curl -X PATCH http://localhost:8000/api/v1/transactions/1/estado \
  -H "Content-Type: application/json" \
  -d '{"estado": "APROBADA"}'

# 4) Ver el resumen del commerce
curl http://localhost:8000/api/v1/commerces/1/resumen
```

---

## Desarrollo local (sin Docker)

Con uv no hace falta crear ni activar el entorno manualmente: `uv sync` crea
el `.venv` e instala todo a partir de `uv.lock`.

```bash
# Instala dependencias (incluye el grupo de desarrollo)
uv sync

# Ajustar DB_HOST=localhost en .env y tener una instncia de  MariaDB disponible
# Arrancar el servidor (uv run ejecuta dentro del entorno):
uv run uvicorn app.main:app --reload
```

> Si no tienes uv instalado:
> - Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
> - Linux / Mac: `curl -LsSf https://astral.sh/uv/install.sh | sh`
> - O bien, vía pip: `pip install uv`

### Tests

- Se crea una carpeta básica de tests para demostrar que Docker cree el artefacto del proyecto cuando se pasen los tests.

```bash
uv run pytest
```

## Integración Continua (GitHub Actions)

El workflow `.github/workflows/ci.yml` se ejecuta en cada push y pull request:

1. **pruebas:** instala uv, sincroniza dependencias (`uv sync --frozen`) y
   ejecuta `uv run ruff check .` y `uv run pytest`.
2. **build-imagen:** construye la imagen Docker (solo si las pruebas pasan).

---
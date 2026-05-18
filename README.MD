# 📦 Rápido-Entrega S.A. — Ecosistema de Microservicios

> Plataforma logística para la gestión de repartidores, rutas y notificaciones.

Este repositorio contiene la infraestructura de la plataforma logística de Rápido-Entrega S.A., implementada como un conjunto de microservicios desacoplados con frontend React/Vite y backend FastAPI.

## Cambios implementados

### Frontend

- Autenticación con login, registro y sesión persistente.
- Botón de `Cerrar sesión` funcional en la cabecera.
- Protección de rutas privadas: `Dashboard`, `Rutas`, `Notificaciones` y `Perfil`.
- Dashboard con métricas del usuario:
  - total de rutas
  - entregas completadas
  - rutas en tránsito
  - rutas pendientes
  - ratio de éxito
  - notificaciones totales
  - notificaciones sin leer
  - notificaciones fallidas
- Página `Rutas` con:
  - creación de rutas desde UI
  - listado de rutas con origen, destino, repartidor y estado
  - recarga manual de datos
- Página `Notificaciones` con:
  - envío de notificaciones
  - historial por usuario
  - filtros por tipo y estado
  - búsqueda por título o mensaje
  - marcado de notificaciones como leídas

### Backend

- `service1-rutas`:
  - validación de repartidor al crear rutas
  - `is_active` como booleano en el modelo de repartidor
- `service2-notificaciones`:
  - logs de auditoría y estado de notificaciones
  - soporte de plantillas para envíos masivos
- `service3`:
  - `ItemCreate` con `owner_id` en payload JSON
  - `ActivityCreate` con `user_id` en payload JSON
- Pruebas actualizadas para flujos más reales y menos dependencia de auth externa

---

## 📂 Estructura principal

```
R-pido-Entrega/
├── api-gateway/
├── frontend/
├── services/
│   ├── authentication/
│   ├── service1-rutas/
│   ├── service2-notificaciones/
│   └── service3/
├── docker-compose.yml
├── docker-compose.override.yml
├── pyproject.toml
└── README.MD
```

---

## 🔁 Flujo DevOps — Automatización Completa

### 1. Colaboración con Git

```
Dueño del repositorio
        │
        ├── clone  ──────────────────────── trabaja directamente
        │
Colaborador externo
        │
        └── fork → clone → branch → PR ──► revisión → merge
```

### 2. Ciclo de desarrollo local

```bash
# 1. Realizar cambios en el código
git add .
git commit -m "feat: descripción del cambio"   # ← pre-commit se ejecuta aquí
git push origin main
```

> ⚡ Al hacer `git commit`, los hooks de **pre-commit** se ejecutan automáticamente:
>
> - `ruff check` — linting del código Python
> - `ruff format` — formateo automático
> - `pytest` — ejecución de pruebas unitarias

### 3. Pipeline de CI/CD con GitHub Actions

```
git push ──────────────────► GitHub Actions: CI
                                   ├── ruff --lint
                                   ├── ruff --format
                                   └── pytest

git tag v1.0 && git push --tags ► GitHub Actions: CD  (patrón: v*)
                                   ├── [CI completo]
                                   ├── docker build (todos los servicios)
                                   └── docker push → Registry / Deploy
```

---

## 🛠️ Requisitos Previos

| Herramienta | Versión mínima | Uso |
|---|---|---|
| Docker | 24+ | Contenedores de servicios |
| Docker Compose | 2.x | Orquestación local |
| Python | 3.11+ | Microservicios backend |
| Node.js | 18+ | Frontend |
| Git | 2.x | Control de versiones |

---

## ⚙️ Instalación y Uso Local

### Clonar el repositorio

```bash
# Dueño / Colaborador con acceso directo
git clone https://github.com/tu-org/R-pido-Entrega.git
cd R-pido-Entrega

# Colaborador externo (fork)
git clone https://github.com/TU-USUARIO/R-pido-Entrega.git
cd R-pido-Entrega
git remote add upstream https://github.com/tu-org/R-pido-Entrega.git
```

### Configurar variables de entorno

```bash
cp services/authentication/.env.example services/authentication/.env
cp services/service1-rutas/.env.example services/service1-rutas/.env
cp services/service2-notificaciones/.env.example services/service2-notificaciones/.env
cp services/service3/.env.example services/service3/.env
cp frontend/.env.example frontend/.env
```

### Instalar pre-commit hooks (primera vez)

```bash
pip install pre-commit
pre-commit install
```

### Levantar toda la plataforma

```bash
docker-compose up --build
```

### Ejecutar frontend en modo desarrollo

```bash
cd frontend
npm run dev
```

### Ejecutar backend localmente

```bash
cd services/authentication
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

cd ../service1-rutas
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

cd ../service2-notificaciones
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

cd ../service3
uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
```

### Ejecutar pruebas

```bash
pytest
pytest services/service1-rutas/tests/test_rutas.py
pytest services/service2-notificaciones/tests/test_notificaciones.py
pytest services/service3/tests/test_service3.py
```

## 📌 Rutas principales

- Frontend: <http://localhost:3001>
- API Gateway: <http://localhost:80>
- Auth: <http://localhost:80/api/auth/>
- Rutas: <http://localhost:80/api/rutas/>
- Notificaciones: <http://localhost:80/api/notificaciones/>
- Service3: <http://localhost:80/api/service3/>

## 🤝 Contribución

1. Crea una rama nueva: `git checkout -b feature/nombre-del-cambio`
2. Haz tus cambios.
3. Ejecuta pruebas y confirma que pasan.
4. Haz commit.
5. Abre un Pull Request hacia `main` con descripción clara.

Gracias por contribuir a Rápido-Entrega. ¡Vamos a entregar rápido y con calidad!

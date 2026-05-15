# 📦 Rápido-Entrega S.A. — Ecosistema de Microservicios

> Plataforma logística para la gestión de repartidores, rutas y notificaciones en tiempo real, construida sobre una arquitectura de microservicios con CI/CD automatizado.
Este repositorio contiene la infraestructura automatizada para la plataforma logística de Rápido-Entrega S.A., diseñada para gestionar repartidores, rutas y notificaciones en tiempo real. La arquitectura sigue un modelo de microservicios robusto, priorizando la estabilidad mediante procesos de CI/CD.

## Arquitectura del Sistema

```
                        ┌─────────────┐
                        │   Frontend  │  (React / Vue / HTML)
                        └──────┬──────┘
                               │ HTTP
                        ┌──────▼──────────────┐
                        │   API Gateway        │  ← Reverse Proxy (Nginx)
                        │   Punto de entrada   │     Puerto 80
                        └──┬───┬───┬───┬──────┘
                           │   │   │   │
              ┌────────────┘   │   │   └────────────┐
              │                │   │                 │
       ┌──────▼──────┐  ┌──────▼─────┐  ┌──────▼──────┐  ┌──────▼──────┐
       │    auth      │  │    ms1     │  │    ms2      │  │    ms3      │
       │ Autenticación│  │   Rutas    │  │Notificaciones│  │  [Servicio] │
       └──────┬───────┘  └──────┬─────┘  └──────┬──────┘  └──────┬──────┘
              │                 │                │                 │
           [DB auth]         [DB ms1]         [DB ms2]         [DB ms3]
```

| Componente | Descripción | Puerto interno |
|---|---|---|
| **Frontend** | Interfaz de usuario para clientes y administradores | 3000 |
| **API Gateway** | Reverse proxy Nginx, único punto de entrada externo | 80 |
| **auth** | Gestión de usuarios, tokens y seguridad | 8001 |
| **ms1 — Rutas** | Logística y seguimiento de repartidores en tiempo real | 8002 |
| **ms2 — Notificaciones** | Alertas automáticas para clientes finales | 8003 |
| **ms3 — [Servicio]** | Módulo adicional de negocio | 8004 |

---

## 📂 Estructura de carpetas

```
rapido-entrega/
│
├── .github/
│   └── workflows/
│       ├── ci.yml                  # Pipeline: lint + test en cada push/PR
│       └── cd.yml                  # Pipeline: build + deploy al crear TAG v*
│
├── frontend/                       # Interfaz de usuario
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/               # Llamadas al API Gateway
│   │   └── main.js / main.jsx
│   ├── Dockerfile
│   ├── package.json
│   └── .env.example
│
├── api-gateway/                    # Reverse Proxy (Nginx)
│   ├── nginx.conf                  # Reglas de enrutamiento a microservicios
│   └── Dockerfile
│
├── services/                       # Microservicios (Backend)
│   │
│   ├── authentication/             # Servicio auth
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── models.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── tests/
│   │   │   └── test_auth.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── .env.example
│   │
│   ├── service1-rutas/             # Microservicio ms1
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── models.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── tests/
│   │   │   └── test_rutas.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── .env.example
│   │
│   ├── service2-notificaciones/    # Microservicio ms2
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── models.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── tests/
│   │   │   └── test_notificaciones.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── .env.example
│   │
│   └── service3/                   # Microservicio ms3
│       ├── app/
│       │   ├── __init__.py
│       │   ├── main.py
│       │   ├── models.py
│       │   ├── routes.py
│       │   └── schemas.py
│       ├── tests/
│       │   └── test_service3.py
│       ├── Dockerfile
│       ├── requirements.txt
│       └── .env.example
│
├── docker-compose.yml              # Orquestación completa de la plataforma
├── docker-compose.override.yml     # Overrides para desarrollo local
├── .pre-commit-config.yaml         # Hooks: ruff lint + format + pytest
├── pyproject.toml                  # Configuración de ruff y herramientas Python
└── README.md
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
git clone https://github.com/tu-org/rapido-entrega.git
cd rapido-entrega

# Colaborador externo (fork)
git clone https://github.com/TU-USUARIO/rapido-entrega.git
cd rapido-entrega
git remote add upstream https://github.com/tu-org/rapido-entrega.git
```

### Configurar variables de entorno

```bash
# Copiar los .env de ejemplo en cada servicio
cp services/authentication/.env.example    services/authentication/.env
cp services/service1-rutas/.env.example    services/service1-rutas/.env
cp services/service2-notificaciones/.env.example services/service2-notificaciones/.env
cp services/service3/.env.example          services/service3/.env
cp frontend/.env.example                   frontend/.env
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

| Servicio | URL local |
|---|---|
| Frontend | <http://localhost:3001> |
| API Gateway | <http://localhost:80> |
| Auth | <http://localhost:80/api/auth/> |
| Rutas (ms1) | <http://localhost:80/api/rutas/> |
| Notificaciones (ms2) | <http://localhost:80/api/notificaciones/> |
| Servicio 3 (ms3) | <http://localhost:80/api/service3/> |

### Ejecutar pruebas manualmente

```bash
# Todas las pruebas
pytest

# Un servicio específico
pytest services/authentication/tests/

# Con reporte de cobertura
pytest --cov=services --cov-report=html
```

---

## 🚢 Publicar una versión (Release)

```bash
git tag v1.0.0
git push origin v1.0.0
```

> Esto activa automáticamente el pipeline de **CD** en GitHub Actions, que construye y publica las imágenes Docker de todos los servicios.

---

## 🤝 Guía de Contribución

1. Haz **fork** del repositorio.
2. Crea una rama descriptiva: `git checkout -b feat/nombre-funcionalidad`.
3. Realiza tus cambios y asegúrate de que los tests pasen.
4. Haz commit: los hooks de pre-commit validarán el código automáticamente.
5. Abre un **Pull Request** hacia `main` describiendo los cambios.

---

## 📄 Licencia

Este proyecto es propiedad de **Rápido-Entrega S.A.** — todos los derechos reservados.

# 📦 Rápido-Entrega S.A. — Plataforma de Microservicios

> Plataforma logística para la gestión de repartidores, rutas y notificaciones.

Este repositorio contiene la infraestructura de la plataforma logística de Rápido-Entrega S.A., implementada como un conjunto de microservicios desacoplados con frontend React/Vite y backend FastAPI.

## Cambios implementados

### Frontend

- Autenticación con login, registro y sesión persistente.
- Botón de `Cerrar sesión` funcional en la cabecera.
- Protección de rutas privadas: `Dashboard`, `Rutas`, `Notificaciones` y `Perfil`.
- Dashboard con métricas del usuario.
- Rutas y notificaciones con filtros y búsqueda.

### Backend

- Microservicios desacoplados para auth, rutas, notificaciones y service3.
- Base de datos PostgreSQL independiente para cada servicio.
- Redis y RabbitMQ incluidos para caché y mensajes.
- API Gateway con Nginx para enrutar frontend y APIs.

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

## 🚀 Pasos para ejecutar en otra máquina

1. Clona el repositorio:

```bash
git clone https://github.com/tu-org/R-pido-Entrega.git
cd R-pido-Entrega
```

Si trabajas con un fork:

```bash
git clone https://github.com/TU-USUARIO/R-pido-Entrega.git
cd R-pido-Entrega
git remote add upstream https://github.com/tu-org/R-pido-Entrega.git
```

2. Crea los archivos de entorno:

```bash
cp services/authentication/.env.example services/authentication/.env
cp services/service1-rutas/.env.example services/service1-rutas/.env
cp services/service2-notificaciones/.env.example services/service2-notificaciones/.env
cp services/service3/.env.example services/service3/.env
cp frontend/.env.example frontend/.env
```

3. Verifica que Docker Compose esté instalado:

```bash
docker compose version
```

Si tu entorno solo reconoce `docker-compose`, usa ese comando.

4. Levanta toda la plataforma:

```bash
docker compose up --build
```

> `docker-compose up --build` también funciona en instalaciones antiguas.

5. Accede a la aplicación:

- Frontend: http://localhost:3001
- API Gateway: http://localhost:8080
- Auth: http://localhost:8001
- Rutas: http://localhost:8002
- Notificaciones: http://localhost:8003
- Service3: http://localhost:8004
- RabbitMQ UI: http://localhost:15672

---

## 🌱 Desarrollo local opcional

### Frontend local

```bash
cd frontend
npm install
npm run dev
```

Abre: http://localhost:3000

> El frontend usa el API Gateway en `http://localhost:8080/api`.

### Backend local (opcional)

```bash
cd services/authentication
python -m pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

cd ../service1-rutas
python -m pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

cd ../service2-notificaciones
python -m pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

cd ../service3
python -m pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
```

> Nota: cada servicio tiene su propio `requirements.txt` en la carpeta correspondiente. Instala estos paquetes antes de ejecutar `uvicorn` si trabajas fuera de Docker.


---

## 🧪 Ejecutar pruebas

```bash
pytest
pytest services/service1-rutas/tests/test_rutas.py
pytest services/service2-notificaciones/tests/test_notificaciones.py
pytest services/service3/tests/test_service3.py
```

---

## 🔧 Problemas comunes

- Si faltan variables de entorno, crea los `.env` desde los `.env.example`.
- Si `docker compose` no funciona, prueba `docker-compose`.
- Si hay puertos ocupados, libera `3001`, `8080`, `5432-5435`, `6379`, `5672`, `15672`.
- Para reiniciar todo:

```bash
docker compose down --volumes --remove-orphans
```

---

## 📌 Endpoints principales

- Frontend: http://localhost:3001
- API Gateway: http://localhost:8080
- Auth API: http://localhost:8080/api/auth/
- Rutas API: http://localhost:8080/api/rutas/
- Notificaciones API: http://localhost:8080/api/notificaciones/
- Service3 API: http://localhost:8080/api/service3/

---

## 🤝 Contribución

1. Crea una rama nueva: `git checkout -b feature/nombre-del-cambio`
2. Haz tus cambios.
3. Ejecuta pruebas y confirma que pasan.
4. Haz commit.
5. Abre un Pull Request hacia `main` con descripción clara.

Gracias por contribuir a Rápido-Entrega. ¡Vamos a entregar rápido y con calidad!

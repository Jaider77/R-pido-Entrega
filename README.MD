# 📦 Rápido-Entrega S.A. - Ecosistema de Microservicios

Este repositorio contiene la infraestructura automatizada para la plataforma logística de **Rápido-Entrega S.A.**, diseñada para gestionar repartidores, rutas y notificaciones en tiempo real. La arquitectura sigue un modelo de microservicios robusto, priorizando la estabilidad mediante procesos de CI/CD.

## 🚀 Arquitectura del Sistema
Basado en el diseño técnico del proyecto, el sistema se divide en:

*   **API Gateway (Reverse Proxy):** Punto único de entrada que redirige el tráfico a los servicios internos.
*   **Servicio de Autenticación (`auth`):** Gestión de usuarios y seguridad.
*   **Servicio de Rutas (`ms1`):** Logística y seguimiento de repartidores en tiempo real.
*   **Servicio de Notificaciones (`ms2`):** Alertas automáticas para clientes finales.

---

## 🛠️ Requisitos del Proyecto
Para garantizar la consistencia en todos los entornos, el proyecto utiliza las siguientes herramientas:
*   **Docker & Docker Compose:** Para la orquestación de contenedores.
*   **GitHub Actions:** Para la automatización de la integración y el despliegue.
*   **Ruff:** Linter para asegurar la calidad y el formato del código.
*   **Pytest:** Framework para la ejecución de pruebas unitarias y de integración.

---

## 📂 Estructura de Archivos
Siguiendo el esquema de organización del repositorio:


/
├── .github/workflows/      # Pipelines de CI/CD (GitHub Actions)
├── api-gateway/            # Configuración de Nginx como Reverse Proxy
├── services/               # Microservicios
│   ├── authentication/     # Servicio de Auth
│   ├── rutas/              # Servicio ms1
│   └── notificaciones/     # Servicio ms2
├── docker-compose.yml      # Orquestación de toda la plataforma
└── README.md               # Documentación principal del proyecto


## Flujo de Automatización (DevOps)
El proceso de desarrollo está blindado para evitar errores en producción:

# Colaboración y Calidad (Pre-commits)
Fork & Clone: Los desarrolladores deben trabajar en su propio fork.

Hooks Locales: Antes de cada commit, se ejecutan automáticamente ruff y pytest.

# Integración Continua (GitHub Actions)
Al realizar un push o crear un TAG (ej. v1.0), el pipeline ejecuta:

Linting: Verificación de estilo con ruff.

Testing: Validación de lógica con pytest.

Build: Construcción de imágenes Docker si las pruebas son exitosas.

## Instalación y Uso Local
Para levantar todo el ecosistema de Rápido-Entrega S.A., ejecute:

# Clonar el repositorio
git clone <url-del-repo>

# Levantar todos los servicios
docker-compose up --build

## Nota: El API Gateway estará disponible en el puerto 80, redirigiendo el tráfico a los servicios de auth, rutas y notificaciones según la ruta de la URL
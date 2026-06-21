# Despliegue de Microservicio en Kubernetes con GitOps

Trabajo final — Diplomado en Arquitectura de Software · Universidad de La Sabana.

Este proyecto implementa el ciclo de vida completo **cloud-native** de un
microservicio: desde su contenerización hasta su despliegue automatizado en
Kubernetes mediante **GitOps** con ArgoCD y un pipeline de **CI/CD**.

---

## 1. Arquitectura general

```
   Desarrollador
        │ git push (rama main)
        ▼
 ┌──────────────┐   build + push imagen    ┌──────────────┐
 │ GitHub Actions│ ───────────────────────▶ │  Docker Hub  │
 │   (CI/CD)     │                          └──────────────┘
 └──────┬───────┘
        │ actualiza tag en values.yaml (commit GitOps)
        ▼
 ┌──────────────┐   observa el repo (pull)  ┌──────────────┐
 │   Repo Git    │ ◀──────────────────────── │    ArgoCD    │
 └──────────────┘                           └──────┬───────┘
                                                   │ helm install/upgrade
                                                   ▼
                                          ┌──────────────────┐
                                          │ Kubernetes (pods)│
                                          │  task-api dev/prod│
                                          └──────────────────┘
```

**Tecnologías:** Python + FastAPI · Docker · Kubernetes (minikube) · Helm ·
ArgoCD · GitHub Actions.

---

## 2. Estructura del repositorio

```
.
├── .github/workflows/
│   └── ci-cd.yml              # Pipeline CI/CD (build, push, GitOps)
├── src/                       # Código del microservicio
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py            # API FastAPI (CRUD de tareas)
│   ├── Dockerfile             # Imagen multi-stage
│   ├── .dockerignore
│   └── requirements.txt
└── deploy/
    ├── argocd/
    │   ├── application-dev.yaml   # App ArgoCD (Desarrollo)
    │   └── application-prod.yaml  # App ArgoCD (Producción)
    └── helm/
        └── task-api-chart/        # Chart de Helm
            ├── Chart.yaml
            ├── values.yaml        # Valores por defecto (dev)
            ├── values-prod.yaml   # Overrides de producción
            └── templates/
                ├── _helpers.tpl
                ├── deployment.yaml
                └── service.yaml
```

---

## 3. El microservicio (Task Manager API)

API REST de gestión de tareas. Endpoints principales:

| Método | Ruta                              | Descripción                         |
|--------|-----------------------------------|-------------------------------------|
| GET    | `/`                               | Info del servicio y entorno actual  |
| GET    | `/health`                         | Health check (usado por Kubernetes) |
| GET    | `/api/v1/tasks`                   | Listar tareas                       |
| POST   | `/api/v1/tasks`                   | Crear tarea                         |
| GET    | `/api/v1/tasks/{id}`              | Obtener tarea                       |
| PUT    | `/api/v1/tasks/{id}/complete`     | Marcar como completada              |
| DELETE | `/api/v1/tasks/{id}`              | Eliminar tarea                      |

Documentación interactiva (Swagger) disponible en `/docs`.

La variable de entorno `APP_ENV` (inyectada por Helm) muestra el entorno en el
endpoint `/`, lo que permite verificar visualmente los overlays dev/prod.

---

## 4. Configuración inicial (reemplazar marcadores)

Antes de desplegar hay que reemplazar dos marcadores por tus datos reales:

| Marcador               | Dónde aparece                                  | Reemplazar por           |
|------------------------|------------------------------------------------|--------------------------|
| `TU_USUARIO_DOCKERHUB` | `deploy/helm/task-api-chart/values.yaml`       | Tu usuario de Docker Hub |
| `TU_USUARIO_GITHUB`    | `deploy/argocd/application-dev.yaml` y `-prod` | Tu usuario de GitHub     |

Y configurar en GitHub (`Settings → Secrets and variables → Actions`) dos
secretos para el pipeline:

| Secreto              | Valor                                  |
|----------------------|----------------------------------------|
| `DOCKERHUB_USERNAME` | Tu usuario de Docker Hub               |
| `DOCKERHUB_TOKEN`    | Un *access token* de Docker Hub        |

---

## 5. Ejecución local (sin Kubernetes)

```bash
cd src
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# Abrir http://localhost:8000/docs
```

---

## 6. Despliegue completo (paso a paso)

### 6.1 Construir y probar la imagen Docker
```bash
docker build -t task-api:local ./src
docker run -p 8000:8000 task-api:local
```

### 6.2 Levantar el clúster local
```bash
minikube start --driver=docker
```

### 6.3 Instalar ArgoCD
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### 6.4 Registrar las aplicaciones en ArgoCD
```bash
kubectl apply -f deploy/argocd/application-dev.yaml
kubectl apply -f deploy/argocd/application-prod.yaml
```

### 6.5 Acceder a la UI de ArgoCD
```bash
# Contraseña inicial del usuario 'admin':
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d; echo
# Exponer la UI:
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Abrir https://localhost:8080  (usuario: admin)
```

### 6.6 Acceder a la aplicación desplegada
```bash
kubectl get pods -n task-api-dev
kubectl port-forward -n task-api-dev svc/<nombre-del-servicio> 8000:80
# Abrir http://localhost:8000/
```

---

## 7. Flujo CI/CD (automatización)

1. Haces `git push` a la rama `main`.
2. GitHub Actions construye la imagen y la publica en Docker Hub con el tag
   igual al SHA del commit.
3. El pipeline actualiza ese tag en `values.yaml` y hace commit (con `[skip ci]`).
4. ArgoCD detecta el cambio en Git y sincroniza el clúster con la nueva versión.

> Resultado: cada commit a `main` despliega automáticamente la nueva versión,
> sin acceso manual al clúster (modelo GitOps *pull*).

---

## 8. Entornos y overrides de Helm

| Parámetro      | Desarrollo (`values.yaml`) | Producción (`values-prod.yaml`) |
|----------------|----------------------------|---------------------------------|
| Réplicas       | 1                          | 3                               |
| Tipo de Service| ClusterIP                  | LoadBalancer                    |
| `APP_ENV`      | Desarrollo                 | Producción                      |
| Recursos       | mínimos                    | ampliados                       |

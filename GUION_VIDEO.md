# Guion para el video de entrega

Duración recomendada: **6–9 minutos**. Graba pantalla con tu voz explicando.
La rúbrica premia que el video sea **claro, profesional y muestre todo el flujo**.

> Consejo: ten todo desplegado y funcionando ANTES de grabar. Usa este guion
> como teleprompter.

---

### 1. Introducción (30–45 s)
- Saluda y di tu nombre y el nombre del trabajo: *"Despliegue de un microservicio
  en Kubernetes con GitOps"*.
- Menciona el stack: FastAPI, Docker, Helm, Kubernetes, ArgoCD y GitHub Actions.
- Muestra el `README.md` y el diagrama de arquitectura.

### 2. El microservicio y Docker (1 min)
- Abre `src/app/main.py` y explica brevemente que es una API de tareas (CRUD).
- Muestra el `Dockerfile` y resalta: imagen multi-stage, usuario no-root, probes.
- (Opcional) Muestra la imagen ya publicada en tu Docker Hub.

### 3. Helm (1–1.5 min)
- Abre la carpeta `deploy/helm/task-api-chart`.
- Explica `values.yaml` (defaults/dev) y `values-prod.yaml` (overrides).
- Resalta la tabla de diferencias dev vs prod (réplicas, Service, APP_ENV).

### 4. ArgoCD y Kubernetes (2 min)
- Abre la UI de ArgoCD (https://localhost:8080).
- Muestra las dos aplicaciones (`task-api-dev`, `task-api-prod`) en estado
  **Synced / Healthy**.
- Entra a una app y muestra el árbol de recursos (Deployment, Service, Pods).
- En la terminal: `kubectl get pods -n task-api-dev` y `-n task-api-prod`
  (resalta que prod tiene 3 réplicas y dev 1).
- Haz `port-forward` y abre `http://localhost:8000/` mostrando que el campo
  `environment` dice "Desarrollo" (y en prod "Producción").
- Muestra `/docs` y crea una tarea con POST para probar que funciona.

### 5. CI/CD en vivo (2–3 min) — *la parte más valorada*
- En `src/app/main.py` haz un cambio visible (ej. el texto del mensaje raíz).
- `git add . && git commit -m "demo: cambio visible" && git push`.
- Ve a la pestaña **Actions** de GitHub y muestra el workflow ejecutándose:
  build → push a Docker Hub → commit del nuevo tag.
- Muestra que el pipeline hizo un commit automático en `values.yaml`.
- Vuelve a ArgoCD: muestra cómo detecta el cambio y **sincroniza solo**
  (o haz *Refresh*).
- Recarga `http://localhost:8000/` y muestra el cambio ya desplegado.
- Cierra recalcando: *"Cada commit a main despliega automáticamente, sin tocar
  el clúster a mano. Eso es GitOps."*

### 6. Cierre (20 s)
- Resume lo demostrado: Docker, Helm, Kubernetes, ArgoCD y CI/CD funcionando.
- Agradece.

---

## Checklist antes de grabar
- [ ] `minikube` corriendo.
- [ ] ArgoCD instalado y ambas apps en *Synced/Healthy*.
- [ ] `port-forward` de ArgoCD y de la app listos (en dos terminales).
- [ ] Imagen publicada en Docker Hub.
- [ ] Secretos `DOCKERHUB_USERNAME` y `DOCKERHUB_TOKEN` configurados en GitHub.
- [ ] Marcadores `TU_USUARIO_*` reemplazados en todo el repo.

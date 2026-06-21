# CLAUDE.md — Contexto del proyecto para Claude Code

> **Lee este archivo completo antes de hacer nada.** Contiene todo el contexto
> necesario para retomar este trabajo desde cualquier sesión nueva.
> La bitácora cronológica (qué se hizo y qué problemas surgieron) está en
> `MEMORY.md` (en esta misma carpeta).

---

## 1. Qué es este proyecto

Trabajo **final** del *Diplomado en Arquitectura de Software* de la
**Universidad de La Sabana**. Guía oficial: `k8s_guide.pdf` (en la raíz).

**Objetivo del usuario:** entregar el trabajo **de inicio a fin**. El propósito
**NO es aprender** los detalles, sino **completarlo y entregarlo**. Dar lo
mínimo necesario para avanzar, ser concreto y ejecutar.

El usuario **no tiene conocimientos previos** del tema. Claude conduce el
proyecto paso a paso, deja claro **qué hace Claude** y **qué debe hacer el
usuario** (cuentas, contraseñas sudo, grabar el video).

**Idioma:** responder siempre en **español**.

### Qué pide la guía (resumen)
Construir y desplegar **un microservicio** con toda la cadena cloud-native:
1. **Docker** — contenerizar el microservicio.
2. **Helm** — empaquetar con valores por defecto + overrides por entorno.
3. **Kubernetes** — desplegar en un clúster.
4. **ArgoCD** — GitOps (pull): ArgoCD lee el repo Git y sincroniza al clúster.
5. **CI/CD** — pipeline que al detectar un commit en una rama construye y despliega.

**Entregables:** código fuente + **video** mostrando el resultado funcionando.

**Rúbrica (3 criterios, 5 pts c/u):**
1. Microservicio + Docker + Helm + ArgoCD funcionando sin errores.
2. Pipeline CI/CD automatizado + calidad de código y video.
3. Documentación clara + video profesional.

---

## 2. Decisiones tomadas (NO volver a preguntar)

| Tema | Decisión |
|------|----------|
| Microservicio | **Propio y simple**: "Task Manager API" (CRUD de tareas). Original, para **evitar plagio** del repo de referencia del compañero (que era KYC/AML). |
| Stack | **Python + FastAPI** |
| Registro de imágenes | **Docker Hub** (cuenta a crear por el usuario) |
| Repo GitHub | Nombre **`trabajo-final-k8s`**, **público** (ArgoCD lee sin credenciales) |
| CI | **GitHub Actions** |
| Clúster local | **minikube** con driver docker |

**Repo de referencia del compañero** (solo como guía, NO copiar):
https://github.com/juan10024/Despliegue_K8S

---

## 3. Entorno de la máquina (Manjaro Linux)

- **SO:** Manjaro Linux, shell zsh. Gestor de paquetes: `pacman`.
- **sudo requiere contraseña** → Claude NO puede instalar; el usuario corre los
  comandos `sudo` él mismo (usando el prefijo `! ` en el prompt para que la
  salida quede en la sesión).
- **Python del sistema = 3.14.5** → ⚠️ rompe la instalación de `pydantic-core`
  (no hay wheels precompilados; faltaría Rust). **Usar `python3.12`** (está en
  `/home/singular1ty/.local/bin/python3.12`) para pruebas locales.
- CPU **soporta virtualización**. Usuario **aún no** está en el grupo `docker`
  (agregarse al grupo solo aplica en sesión nueva → usar `newgrp docker`).
- Herramientas presentes al inicio: git, node 24, python. **Faltan** (se instalan
  en Paso 1): docker, kubectl, helm, minikube, github-cli (gh).

---

## 4. Estructura del proyecto (ya creada y validada)

```
k8s/                              (raíz = working dir; será el repo git)
├── CLAUDE.md                     # este archivo
├── MEMORY.md                     # bitácora cronológica
├── README.md                     # documentación de entrega
├── GUION_VIDEO.md                # guion para grabar el video
├── k8s_guide.pdf                 # guía oficial del trabajo
├── .gitignore
├── .github/workflows/
│   └── ci-cd.yml                 # pipeline: build→push DockerHub→update tag→commit
├── src/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py               # FastAPI: CRUD de tareas + /health + /
│   ├── Dockerfile                # multi-stage, python:3.12-slim, usuario no-root
│   ├── .dockerignore
│   └── requirements.txt          # fastapi, uvicorn[standard], pydantic
└── deploy/
    ├── argocd/
    │   ├── application-dev.yaml   # ns task-api-dev, values.yaml
    │   └── application-prod.yaml  # ns task-api-prod, values.yaml + values-prod.yaml
    └── helm/task-api-chart/
        ├── Chart.yaml
        ├── values.yaml           # defaults/dev (1 réplica, ClusterIP, APP_ENV=Desarrollo)
        ├── values-prod.yaml      # override prod (3 réplicas, LoadBalancer, APP_ENV=Producción)
        └── templates/
            ├── _helpers.tpl
            ├── deployment.yaml    # con liveness/readiness probes a /health
            └── service.yaml
```

### Microservicio — endpoints
- `GET /` → info + `environment` (muestra APP_ENV; sirve para ver dev vs prod)
- `GET /health` → health check (usado por las probes de k8s)
- `GET /api/v1/tasks` · `POST /api/v1/tasks` · `GET /api/v1/tasks/{id}`
- `PUT /api/v1/tasks/{id}/complete` · `DELETE /api/v1/tasks/{id}`
- Swagger en `/docs`. Almacenamiento **en memoria** (sin BD externa).

---

## 5. ⚠️ Marcadores que se DEBEN reemplazar antes de desplegar

| Marcador | Archivo(s) | Reemplazar por |
|----------|-----------|----------------|
| `TU_USUARIO_DOCKERHUB` | `deploy/helm/task-api-chart/values.yaml` | usuario real de Docker Hub |
| `TU_USUARIO_GITHUB` | `deploy/argocd/application-dev.yaml` y `application-prod.yaml` | usuario real de GitHub |

Secretos a configurar en GitHub (Settings → Secrets and variables → Actions):
- `DOCKERHUB_USERNAME` = usuario de Docker Hub
- `DOCKERHUB_TOKEN` = access token de Docker Hub

---

## 6. Plan de trabajo (10 pasos) y estado

1. ✅ Microservicio FastAPI — hecho y **validado** con python3.12.
2. ✅ Dockerfile multi-stage.
3. ✅ Helm chart (values dev + override prod).
4. ✅ Manifiestos ArgoCD (dev/prod, ya con nombre `trabajo-final-k8s`).
5. ✅ Pipeline CI/CD GitHub Actions.
6. ✅ README + GUION_VIDEO.md.
7. 🟡 **Instalar tooling** — paquetes INSTALADOS (docker, kubectl, helm, minikube,
   github-cli). PERO el servicio de Docker NO arrancó tras la instalación
   (ver "RETOMAR AQUÍ").
8. ⬜ Crear cuenta Docker Hub + access token (guiar al usuario).
9. ⬜ Reemplazar marcadores, push a GitHub (con `gh`), configurar 2 secretos.
10. ⬜ Levantar minikube + ArgoCD, desplegar, validar flujo E2E, grabar video.

---

## 6.1 ⭐ RETOMAR AQUÍ (sesión nueva tras reinicio)

**Situación:** El usuario corrió el comando de instalación (Paso 1) en su terminal
normal — los paquetes se instalaron bien. Al hacer `systemctl enable --now docker`,
el servicio falló: `docker.service` → `failed (start-limit-hit)`. La causa muy
probable es que el `pacman -Syu` **actualizó el kernel**, y Docker no carga sus
módulos hasta **reiniciar**. **El usuario reinició el equipo.**

**Primer paso al volver:** verificar que tras el reinicio Docker arrancó. Pídele
al usuario (o que corra él en su terminal normal) y confirma:
```
systemctl status docker --no-pager        # debe estar 'active (running)'
docker run --rm hello-world               # debe imprimir el mensaje de éxito
```
Si Docker corre y `hello-world` funciona → la instalación quedó completa.
Verifica también (Claude puede correr esto, no necesita sudo):
```
docker --version; kubectl version --client; helm version; minikube version; gh --version
```
Nota: tras el reinicio el usuario YA debería estar en el grupo `docker` (probar
`docker ps` sin sudo). Si Docker SIGUE fallando tras reiniciar, pedir:
`journalctl -xeu docker.service --no-pager | tail -40` y diagnosticar.

**Luego, continuar con el Paso 8:** crear cuenta Docker Hub + access token,
reemplazar marcadores `TU_USUARIO_*`, push a GitHub, secretos, minikube + ArgoCD,
demo y video. (Detalle en este archivo y en README.md sección 6.)

---

## 7. Próximos comandos clave (referencia para retomar)

### PASO 1 — Instalar tooling (lo corre el USUARIO, pide contraseña)
```
! sudo pacman -Syu --noconfirm docker kubectl helm minikube github-cli && sudo systemctl enable --now docker && sudo usermod -aG docker $USER && echo "INSTALACION_OK"
```

### Verificación (la corre Claude)
```
docker --version; kubectl version --client; helm version; minikube version; gh --version
```

### Validar microservicio localmente (usar python3.12, NO el 3.14 del sistema)
```
cd src && python3.12 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt httpx
```

### Build/test imagen, clúster, ArgoCD → ver README.md sección 6.

---

## 8. Reglas de trabajo con este usuario

- Conducir y ejecutar; no sobre-explicar el "por qué". Mínimo necesario para hacer.
- Dejar siempre claro **qué hace Claude** vs **qué hace el usuario**.
- Los comandos `sudo` y logins interactivos los corre el usuario con prefijo `! `.
- Mantener `MEMORY.md` actualizado como bitácora tras cada avance o contratiempo.

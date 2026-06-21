# MEMORY.md — Bitácora del proyecto

> Registro cronológico de lo realizado, decisiones y contratiempos.
> Para el contexto completo del proyecto ver `CLAUDE.md`.
> Actualizar este archivo tras cada avance o problema.

---

## Sesión 1 — 2026-06-20

### Contexto inicial
- Usuario inicia el trabajo final del diplomado (U. de La Sabana). Pasa la guía
  `k8s_guide.pdf` y el repo de referencia de un compañero
  (https://github.com/juan10024/Despliegue_K8S).
- Propósito: **entregar**, no aprender. Usuario sin conocimientos previos del tema.

### Diagnóstico del entorno
- ✅ Presentes: git 2.54, node 24.11, python 3.14.5.
- ❌ Faltaban: docker, kubectl, minikube, kind, helm.
- Working dir NO era repo git (se hará `git init` más adelante).

### Decisiones acordadas con el usuario (vía preguntas)
- Microservicio **propio y simple** (Task Manager API) → evitar plagio del repo
  del compañero (KYC/AML).
- Stack **Python + FastAPI**.
- Registro **Docker Hub** (cuenta a crear). En Linux se usa Docker Engine nativo,
  **no Docker Desktop**.
- Repo GitHub **`trabajo-final-k8s`**, **público**.

### Trabajo realizado (código)
- ✅ Microservicio FastAPI creado: `src/app/main.py`, `__init__.py`,
  `requirements.txt`. CRUD de tareas + `/health` + `/`.
- ✅ Dockerfile multi-stage (python:3.12-slim, usuario no-root, healthcheck) +
  `.dockerignore`.
- ✅ Helm chart `deploy/helm/task-api-chart/` con `values.yaml` (dev) y
  `values-prod.yaml` (override prod), templates con probes y helpers.
- ✅ Manifiestos ArgoCD dev/prod en `deploy/argocd/` (repoURL ajustado al nombre
  `trabajo-final-k8s`).
- ✅ Pipeline `.github/workflows/ci-cd.yml` (build → push Docker Hub con tag=SHA
  → update tag en values.yaml → commit con `[skip ci]` para GitOps).
- ✅ `README.md`, `GUION_VIDEO.md`, `.gitignore`.

### Contratiempos y cómo se resolvieron
- ⚠️ **Python 3.14 rompe la validación local:** al crear venv con el python del
  sistema (3.14.5), `pip install` falló construyendo `pydantic-core` (sin wheels
  para 3.14, requeriría Rust que no está instalado).
  → **Solución:** se detectó `python3.12` en `~/.local/bin/python3.12` y se usó
  ese para el venv. El contenedor usa python:3.12-slim, así que no afecta al
  despliegue.
- ✅ **Validación exitosa** del microservicio con python3.12: root, /health (200),
  crear tarea (201), listar, completar, eliminar (204), 404 tras borrar. Todo OK.

### Diagnóstico para instalación
- `pacman` disponible; `sudo` **requiere contraseña** (Claude no puede instalar
  solo → el usuario corre el comando).
- `gh` no instalado; usuario **no** está en grupo `docker`; CPU soporta
  virtualización.

### Pausa solicitada por el usuario
- Se crearon `CLAUDE.md` (contexto para retomar) y este `MEMORY.md` (bitácora)
  como respaldo antes de instalar el tooling.

### Estado al cierre de este punto
- **Pendiente inmediato:** el usuario ejecutará el comando de instalación (Paso 1):
  ```
  ! sudo pacman -Syu --noconfirm docker kubectl helm minikube github-cli && sudo systemctl enable --now docker && sudo usermod -aG docker $USER && echo "INSTALACION_OK"
  ```
- Tras `INSTALACION_OK` → verificar instalación, crear Docker Hub + token,
  reemplazar marcadores, push a GitHub + secretos, levantar minikube + ArgoCD,
  desplegar y grabar video.

### Instalación del tooling — contratiempos
- ⚠️ **El prefijo `!` de Claude Code no sirve para `sudo`:** falla con
  `sudo: a terminal is required to read the password`. El `!` corre sin TTY, así
  que sudo no puede pedir contraseña.
  → **Solución:** el usuario corre los comandos `sudo` en su **terminal normal**
  (fuera de Claude Code) y luego vuelve. Claude verifica con comandos sin sudo.
- ❓ Duda del usuario sobre `gh`: la doc oficial dice `brew install gh`. Aclarado:
  `brew` es Homebrew (no lo tiene); en Manjaro el paquete oficial es `github-cli`
  vía pacman, que instala el mismo binario `gh`. Se mantiene `github-cli`.
- ✅ El usuario corrió la instalación en su terminal normal. **Paquetes instalados
  OK** (docker, kubectl, helm, minikube, github-cli).
- ⚠️ **El servicio de Docker NO arrancó:** `systemctl enable --now docker` →
  `docker.service: failed (start-limit-hit)`. El `start-limit-hit` es solo
  consecuencia de reintentos; la causa de fondo: el `pacman -Syu` actualizó el
  **kernel y módulos**, y Docker no carga sus módulos hasta **reiniciar**.
  → **Decisión:** el usuario **reinicia el equipo** y se inicia una **sesión
  nueva** de Claude Code para ahorrar tokens.

### Estado al cierre de la Sesión 1 (antes del reinicio)
- Código 100% listo y validado. Tooling instalado pero Docker pendiente de
  arrancar tras reinicio.
- **RETOMAR EN:** ver `CLAUDE.md` sección "6.1 ⭐ RETOMAR AQUÍ". Primer paso:
  confirmar que Docker arrancó tras el reinicio (`systemctl status docker`,
  `docker run --rm hello-world`), luego seguir con Docker Hub + push + ArgoCD.

<!-- Próximas entradas: agregar debajo con fecha/hora y qué pasó. -->

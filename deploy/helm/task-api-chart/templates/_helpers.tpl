{{/*
Helpers reutilizables del chart.
*/}}

{{/* Nombre base de los recursos. */}}
{{- define "task-api.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/* Nombre completo (incluye el nombre del release). */}}
{{- define "task-api.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "task-api.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/* Etiquetas comunes aplicadas a todos los recursos. */}}
{{- define "task-api.labels" -}}
app.kubernetes.io/name: {{ include "task-api.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{- end -}}

{{/* Etiquetas de selección (deben ser estables). */}}
{{- define "task-api.selectorLabels" -}}
app.kubernetes.io/name: {{ include "task-api.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/* Template helpers for naming and labels */}}

{{- define "security-mcp-server.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{- define "security-mcp-server.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := include "security-mcp-server.name" . }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "security-mcp-server.labels" -}}
app.kubernetes.io/name: {{ include "security-mcp-server.name" . }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "security-mcp-server.selectorLabels" -}}
app.kubernetes.io/name: {{ include "security-mcp-server.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "security-mcp-server.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- if .Values.serviceAccount.name }}
{{ .Values.serviceAccount.name }}
{{- else }}
{{ include "security-mcp-server.fullname" . }}
{{- end }}
{{- else }}
default
{{- end }}
{{- end }}

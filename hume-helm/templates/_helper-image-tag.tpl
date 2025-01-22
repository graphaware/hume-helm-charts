{{- define "apiImageTag" -}}
{{- if .Values.api.image.tag -}}
{{ .Values.api.image.tag }}
{{- else -}}
{{ .Values.appVersion | default .Chart.AppVersion }}
{{- end -}}
{{- end -}}

{{- define "webImageTag" -}}
{{- if .Values.web.image.tag -}}
{{ .Values.web.image.tag }}
{{- else -}}
{{ .Values.appVersion | default .Chart.AppVersion }}
{{- end -}}
{{- end -}}

{{- define "orchestraImageTag" -}}
{{- if .Values.orchestra.image.tag -}}
{{ .Values.orchestra.image.tag }}
{{- else -}}
{{ .Values.appVersion | default .Chart.AppVersion }}
{{- end -}}
{{- end -}}

{{- define "eventStoreImageTag" -}}
{{- if .Values.eventstore.image.tag -}}
{{ .Values.eventstore.image.tag }}
{{- else -}}
{{ .Values.appVersion | default .Chart.AppVersion }}
{{- end -}}
{{- end -}}

{{- define "mediaImageTag" -}}
{{- if .Values.media.image.tag -}}
{{ .Values.media.image.tag }}
{{- else -}}
{{ .Values.appVersion | default .Chart.AppVersion }}
{{- end -}}
{{- end -}}
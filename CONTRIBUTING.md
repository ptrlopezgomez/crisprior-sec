# Guía de contribución — Grupo 3012G

## Flujo de ramas (trunk-based)

- `main` está protegida: todo cambio entra vía Pull Request con al menos 1 aprobación del Product Owner.
- Crea una rama por historia de usuario: `feature/HU-0X-descripcion-corta`
  (p. ej. `feature/HU-02-checkov-integration`).
- Sin `develop` de larga duración: las ramas se integran a `main` al cerrar
  cada historia, no al cerrar el Sprint completo.
- Al cierre de cada Sprint Review, se etiqueta el commit en `main` como `sprint-N`.

## Commits

Usa el formato `tipo(alcance): descripción` (Conventional Commits):

```
feat(engine): calcular score contextual con controles compensatorios
fix(scanners): manejar timeout de tfsec en archivos grandes
docs(readme): actualizar instrucciones de setup
test(engine): cobertura de prioritizer.py
```

## Definition of Done (recordatorio)

Antes de abrir el PR, verifica que tu cambio cumple:

- [ ] Código en Python estructurado y sin redundancias.
- [ ] Cobertura de pruebas ≥ 80% en el módulo tocado (`pytest --cov`).
- [ ] Sin credenciales ni secretos expuestos (`.env` nunca se commitea).
- [ ] CI en verde (`backend-tests`, `iac-scan`, `frontend-lint`).
- [ ] Aprobado por el Product Owner contra los criterios de aceptación de la HU.

## Pull Requests

Título: `[HU-0X] Descripción breve`. En la descripción, enlaza la tarjeta de Jira
y resume qué criterios de aceptación cubre el cambio.

# UI UX Pro Max

Una habilidad de IA que proporciona inteligencia de diseño para crear UI/UX profesionales en múltiples plataformas y frameworks.

<p align="center">
  <img src="screenshots/website.png" alt="UI UX Pro Max" width="800">
</p>

## Descripción General

UI UX Pro Max es una base de datos consultable de estilos de UI, paletas de colores, combinaciones de fuentes, tipos de gráficos, recomendaciones de productos, guías de UX y mejores prácticas específicas por stack. Funciona como una habilidad/workflow para asistentes de código con IA (Claude Code, Cursor, Windsurf, etc.).

## Características

- **57 Estilos de UI** - Glassmorphism, Claymorphism, Minimalismo, Brutalismo, Neumorphism, Bento Grid, Modo Oscuro, y más
- **95 Paletas de Colores** - Paletas específicas por industria para SaaS, E-commerce, Salud, Fintech, Belleza, etc.
- **56 Combinaciones de Fuentes** - Combinaciones tipográficas curadas con importaciones de Google Fonts
- **24 Tipos de Gráficos** - Recomendaciones para dashboards y analíticas
- **8 Stacks Tecnológicos** - React, Next.js, Vue, Svelte, SwiftUI, React Native, Flutter, HTML+Tailwind
- **98 Guías de UX** - Mejores prácticas, anti-patrones y reglas de accesibilidad

## Instalación

### Usando CLI (Recomendado)

```bash
# Instalar CLI globalmente
npm install -g uipro-cli

# Ir a tu proyecto
cd /ruta/a/tu/proyecto

# Instalar para tu asistente de IA
uipro init --ai claude      # Claude Code
uipro init --ai cursor      # Cursor
uipro init --ai windsurf    # Windsurf
uipro init --ai antigravity # Antigravity (.agent + .shared)
uipro init --ai copilot     # GitHub Copilot
uipro init --ai kiro        # Kiro
uipro init --ai all         # Todos los asistentes
```

### Otros Comandos del CLI

```bash
uipro versions              # Listar versiones disponibles
uipro update                # Actualizar a la última versión
uipro init --version v1.0.0 # Instalar una versión específica
```

### Instalación Manual

Copia las carpetas apropiadas a tu proyecto:

| Asistente de IA | Carpetas a Copiar                                                   |
| --------------- | ------------------------------------------------------------------- |
| Claude Code     | `.claude/skills/ui-ux-pro-max/`                                     |
| Cursor          | `.cursor/commands/ui-ux-pro-max.md` + `.shared/ui-ux-pro-max/`      |
| Windsurf        | `.windsurf/workflows/ui-ux-pro-max.md` + `.shared/ui-ux-pro-max/`   |
| Antigravity     | `.agent/workflows/ui-ux-pro-max.md` + `.shared/ui-ux-pro-max/`      |
| GitHub Copilot  | `.github/prompts/ui-ux-pro-max.prompt.md` + `.shared/ui-ux-pro-max/`|
| Kiro            | `.kiro/steering/ui-ux-pro-max.md` + `.shared/ui-ux-pro-max/`        |

## Requisitos Previos

Se requiere Python 3.x para el script de búsqueda.

```bash
# Verificar si Python está instalado
python3 --version

# macOS
brew install python3

# Ubuntu/Debian
sudo apt update && sudo apt install python3

# Windows
winget install Python.Python.3.12
```

## Uso

### Claude Code

La habilidad se activa automáticamente cuando solicitas trabajo de UI/UX. Solo chatea naturalmente:

```
Construye una landing page para mi producto SaaS
```

### Cursor / Windsurf / Antigravity

Usa el comando slash para invocar la habilidad:

```
/ui-ux-pro-max Construye una landing page para mi producto SaaS
```

### Kiro

Escribe `/` en el chat para ver los comandos disponibles, luego selecciona `ui-ux-pro-max`:

```
/ui-ux-pro-max Construye una landing page para mi producto SaaS
```

### GitHub Copilot

En VS Code con Copilot, escribe `/` en el chat para ver los prompts disponibles, luego selecciona `ui-ux-pro-max`:

```
/ui-ux-pro-max Construye una landing page para mi producto SaaS
```

### Ejemplos de Prompts

```
Construye una landing page para mi producto SaaS

Crea un dashboard para analíticas de salud

Diseña un sitio web de portafolio con modo oscuro

Haz una UI de app móvil para e-commerce
```

### Cómo Funciona

1. **Tú preguntas** - Solicita cualquier tarea de UI/UX (construir, diseñar, crear, implementar, revisar, arreglar, mejorar)
2. **La habilidad se activa** - La IA busca automáticamente en la base de datos de diseño estilos relevantes, colores, tipografía y guías
3. **Recomendaciones inteligentes** - Basado en tu tipo de producto y requisitos, encuentra el sistema de diseño que mejor coincide
4. **Generación de código** - Implementa la UI con los colores, fuentes, espaciado y mejores prácticas adecuadas

### Stacks Soportados

La habilidad proporciona guías específicas para:

- **HTML + Tailwind** (predeterminado)
- **React** / **Next.js**
- **Vue** / **Svelte**
- **SwiftUI** / **React Native** / **Flutter**

Simplemente menciona tu stack preferido en el prompt, o déjalo por defecto en HTML + Tailwind.

## Historial de Estrellas

[![Star History Chart](https://api.star-history.com/svg?repos=nextlevelbuilder/ui-ux-pro-max-skill&type=Date)](https://star-history.com/#nextlevelbuilder/ui-ux-pro-max-skill&Date)

## Licencia

Este proyecto está licenciado bajo la [Licencia MIT](LICENSE).

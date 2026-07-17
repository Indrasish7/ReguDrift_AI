# Visual Design System Specification: Bento Space HUD (Dark Mode)

This document establishes the **visual system source of truth** for ReguDrift AI's frontend interfaces, adopting an immersive, dark-mode **Security Operations Center (SOC) Command Console** styled as a modular Bento Grid.

---

## 1. Brand Pillars & Style Direction
The creative direction centers on **Advanced Security Command**, evoking a sense of active monitoring, cryptographic control, and high-fidelity intelligence.

*   **Obsidian Depth:** Surfaces utilize deep space black and semi-transparent dark navy layering with glowing borders to establish a three-dimensional glass panel system.
*   **Active Monitoring HUD:** Features animated elements (rotating radar scanners, pulsing status rings, and dynamic Git timeline nodes) to represent live data ingestion and trace analysis.
*   **Bento Modularity:** Content is structured into a high-density, multi-sized grid of widgets, maximizing scanning efficiency.

---

## 2. Design Tokens Mapping

### 2.1 Color Palette
*   **Canvas Base Background:** `#030712` (Midnight Deep Space)
*   **Surfaces (Bento Panels):** `#090F1C` (Obsidian Glass)
*   **Outline Border (Glow):** `#1E293B` / `#334155` (Slate blueprint outlines)
*   **Active Accents:**
    *   *Cyber Blue / Cyan:* `#00F0FF` (Dashboard primary highlight)
    *   *Glowing Violet:* `#8B5CF6` (Git node states and active scans)
    *   *Hot Magenta:* `#F43F5E` (Drifts, errors, and warnings)
    *   *Emerald Green:* `#10B981` (Compliant status nodes)
*   **Text colors:**
    *   *High-Readability Text:* `#F8FAFC` (Pure white text)
    *   *Muted Labels:* `#94A3B8` (Muted slate grey)

---

## 3. Typography Scale
This design system balances editorial authority with clean technical print:
*   **Display / Headlines:** **Inter** (Regular, Medium, Bold)
*   **Technical Logs & Code:** **JetBrains Mono**

| Style | Font Family | Size | Weight | Line Height | Letter Spacing |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **display-lg** | Inter | 28px | Bold (700) | 36px | -0.01em |
| **headline-md** | Inter | 20px | Semibold (600) | 28px | Default |
| **title-sm** | Inter | 15px | Semibold (600) | 22px | Default |
| **body-md** | Inter | 13px | Regular (400) | 18px | Default |
| **code-terminal** | JetBrains Mono | 12px | Regular (400) | 18px | Default |

---

## 4. Shapes & Elevation
*   **Corner Radii:** Soft, modular corners:
    *   *Bento Cards:* `12px` (`rounded-xl`)
    *   *Pills & Buttons:* `24px` (`rounded-full`)
*   **Depth Representation:** Communicated through border glow and semi-transparent panels:
    *   *Glassmorphism:* `background: rgba(9, 15, 28, 0.7); backdrop-filter: blur(12px)`
    *   *Border Glow:* `1px solid rgba(30, 41, 59, 0.8)`

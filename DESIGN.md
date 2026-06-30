# Visual Design System Specification: ReguDrift AI

This document establishes the **visual system source of truth** for ReguDrift AI's frontend interfaces. All visual styling, component borders, typography pairings, and layout spacing parameters are directly mapped from the high-fidelity **StitchMCP** project workspace design configurations (`projects/6593205147055653661`).

---

## 1. Brand Pillars & Style Direction
The creative direction centers on **Institutional Precision**, evoking a sense of absolute security, control, and analytical command. 

*   **Fortified**: Containers, navigation bars, and data rows feel structurally grounded and protected.
*   **Clinical & Quantitative**: Information is presented in high density. Accent alert colors are used strictly to highlight compliance drift.
*   **Architectural Grid**: Minimal visual clutter. Layout is constructed using a high-density, sharp 1px dividing grid, producing a blueprint aesthetic.

---

## 2. Design Tokens Mapping

### 2.1 Color Palette (Fidelity Hex Mapping)
*   **Canvas Base Background**: `#0B0F19` (Midnight primary background canvas)
*   **Surface Dim (Sidebar & Navigation)**: `#131314` (Deep slate surface)
*   **Surface Container (Dashboard Cards)**: `#201f20` (Dark gray widget surfaces)
*   **Surface Container Low (Header Toolbar)**: `#1c1b1c` (Header gray)
*   **Surface Container Lowest (Terminal Canvas)**: `#0e0e0f` (Code dark panel)
*   **Outline Border (Blueprint Divider)**: `#46464c` / `#334155` (Slate-borders)
*   **Text colors**:
    *   *High-Readability Text*: `#e5e2e2` (Pure Off-White)
    *   *Sub-header Text*: `#c6c6cc` (Silver-Grey)
*   **Dynamic Alert Colors**:
    *   *Compliant / Success*: `#10B981` (Emerald Green)
    *   *Partial / Warning*: `#F59E0B` (Amber Gold)
    *   *Non-Compliant / Critical*: `#EF4444` (Vermillion Red)

### 2.2 Typography Scale
This design system uses a tri-font strategy to balance corporate authority with high-density data representation:
*   **Display / Headlines**: **Hanken Grotesk**
*   **Body Copy**: **Inter**
*   **Technical Logs & Labels**: **JetBrains Mono**

| Style | Font Family | Size | Weight | Line Height | Letter Spacing |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **display-lg** | Hanken Grotesk | 32px | Bold (700) | 40px | -0.02em |
| **headline-md** | Hanken Grotesk | 24px | Semibold (600) | 32px | -0.01em |
| **title-sm** | Inter | 18px | Semibold (600) | 24px | Default |
| **body-md** | Inter | 14px | Regular (400) | 20px | Default |
| **body-sm** | Inter | 13px | Regular (400) | 18px | Default |
| **code-terminal** | JetBrains Mono | 13px | Regular (400) | 20px | Default |
| **label-caps** | JetBrains Mono | 11px | Semibold (600) | 16px | 0.05em (Caps) |

### 2.3 Shapes & Elevation
*   **Corner Radii**: Strictly sharp and geometric to retain the architectural feel:
    *   *Cards & Widgets*: `2px` (`0.125rem` / `rounded-sm`)
    *   *Buttons & Inputs*: `4px` (`0.25rem` / `rounded`)
*   **Depth Representation**: Traditional blurred dropshadows are completely prohibited. Depth is communicated strictly through **Tonal Layering** (e.g. Surface Container sitting on Base Canvas) and **Thin Opaque Borders** (`1px solid #46464c`).

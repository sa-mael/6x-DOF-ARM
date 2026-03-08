# 6-DOF System — Industrial Desktop Robotics

> Precision at scale. Bridging the gap between inaccessible industrial automation and desktop manufacturing.

---

## Overview

The 6-DOF System is a custom-engineered six-axis robotic arm designed for hard-metal milling at desktop scale. Built around a dual-stage cycloidal gearbox, an ESP32-S3 AI kinematics core, and an integrated FlowiseAI / BabyAGI cognitive layer, it delivers industrial-grade precision at a fraction of the cost of conventional automation systems.

**Max Reach:** 1.0 m · **Dynamic Payload:** 2.0 kg · **Backlash:** Zero · **Confidence Rating:** 4.95 / 5.0

---

## Project Structure

```
6-dof-system/
├── index.html          # Main product landing page
├── portal.html         # Partner procurement portal
├── assets/
│   └── images/         # 3D renders, diagrams, product photography
└── README.md
```

---

## Pages

### `index.html` — Product Landing Page

The public-facing marketing site. Covers the full system architecture across five sections:

- **Hero** — System status, key specs, animated rings + scan line visual
- **01 · Kinematics** — Reach & rigidity analysis, torque vector visualiser, animated progress bars
- **02 · Cycloidal Core** — Dual-stage drive mechanics, live gear animation
- **03 · AI Architecture** — FlowiseAI + BabyAGI cognitive stack, animated data-flow diagram
- **04 · Visual Showcase** — Draggable / swipeable card carousel (6 slides, auto-advance, keyboard nav)
- **05 · Specifications** — Full spec grid with blue + gold accent cells

Features: custom cursor, scroll-triggered reveals, animated marquee investor ticker, responsive layout.

### `portal.html` — Partner Procurement Portal

A three-tab partner dashboard for volume buyers and ecosystem collaborators.

**Tab 1 · Procurement** — Three hardware modules with partner pricing, feature pills, and a full interactive volume calculator for the Full Kit.

**Tab 2 · Inventory History** — Order ledger with tier discounts applied, delivery status tags, and summary stat cards.

**Tab 3 · Rewards & Access** — Referral code system (+5% tier boost per invite) and claimable hardware gift tracker.

---

## Hardware Modules

### Dual-Stage Cycloidal Drive
Zero-backlash gearbox. Distributes load across multiple rolling contact points — eliminates gear shear under aggressive machining chatter. Market equivalents: $2,000–$4,000.

| Spec | Value |
|---|---|
| Partner Price | $1,800.00 |
| Market Rate | $2,000+ |
| Variants | Ratio 1:100 (High Speed) · Ratio 1:180 (High Torque) |
| Backlash | Sub-arcminute |
| Compatibility | NEMA 23 / NEMA 17 |

### ESP32-S3 AI Kinematics Core
A complete intelligence module — not just a microcontroller. Integrates high-voltage motor driving, stepper drivers, and an onboard AI layer for real-time motion stabilisation and next-state prediction. Eliminates the need to source separate PSUs, driver boards, and motion controllers.

**Why it matters:** Stepper motors on a 6-DOF arm require 24–48V at 2–4A per axis. Sourcing that externally adds cost, wiring complexity, and failure points. This core puts it all in one box.

| Spec | Value |
|---|---|
| Partner Price | $315.00 |
| MSRP | $350.00 |
| Voltage | 24–48V native |
| Current | Up to 4A / axis |
| Connectivity | Wi-Fi 6 telemetry |
| AI Features | Motion stabilisation · Predictive next-state |
| Compatibility | FlowiseAI · BabyAGI · G-code streaming |

### Full 6-DOF Assembly Kit
Complete mechanical skeleton, all six cycloidal drives, NEMA 23 + NEMA 17 motors, pre-wired harness, and ESP32-S3 AI Core pre-integrated. Industrial equivalent arms start at $15,000+.

---

## Volume Pricing — Full 6-DOF Assembly Kit

Pricing scales with order volume. Tier breaks at 10 and 60 units.

| Tier | Qty Range | Unit Price | Example Order (10 units) | Savings vs Standard |
|---|---|---|---|---|
| Standard | 1 – 9 | $5,200.00 | $52,000 | — |
| Volume 10 | 10 – 59 | $3,300.00 | $33,000 | –$19,000 |
| Volume 60 | 60 – 99 | $2,700.00 | $162,000 | –$150,000 |
| Volume 100 | 100+ | $2,700.00 | $270,000 | Contact for negotiation |

### Unit-by-Unit Breakdown (Qty 1 → 10, and Qty 60)

| # | Qty | Tier | Unit Price | Running Total | Saved vs Standard | Avg Cost/Unit |
|---|---|---|---|---|---|---|
| 01 | 1 | Standard | $5,200.00 | $5,200.00 | — | $5,200.00 |
| 02 | 2 | Standard | $5,200.00 | $10,400.00 | — | $5,200.00 |
| 03 | 3 | Standard | $5,200.00 | $15,600.00 | — | $5,200.00 |
| 04 | 4 | Standard | $5,200.00 | $20,800.00 | — | $5,200.00 |
| 05 | 5 | Standard | $5,200.00 | $26,000.00 | — | $5,200.00 |
| 06 | 6 | Standard | $5,200.00 | $31,200.00 | — | $5,200.00 |
| 07 | 7 | Standard | $5,200.00 | $36,400.00 | — | $5,200.00 |
| 08 | 8 | Standard | $5,200.00 | $41,600.00 | — | $5,200.00 |
| 09 | 9 | Standard | $5,200.00 | $46,800.00 | — | $5,200.00 |
| 10 | **10** | **Volume 10** | **$3,300.00** | **$33,000.00** | **Save $19,000** | **$3,300.00** |
| 11 | 60 | **Volume 60** | **$2,700.00** | **$162,000.00** | **Save $150,000** | **$2,700.00** |

> **Note:** The tier break at 10 units reduces the running total from $46,800 (9 units at standard) to $33,000 (10 units at Volume 10) — buying one additional unit saves $13,800 on the full order.

---

## Technology Stack

**Mechanics**
- Dual-stage cycloidal gearbox (custom, zero-backlash)
- NEMA 23 (base / shoulder joints) + NEMA 17 (wrist / tool joints)
- Precision wiring harness (routed through skeleton)

**Electronics**
- ESP32-S3 microcontroller (Wi-Fi 6, dual-core Xtensa LX7)
- Integrated stepper drivers (up to 4A / axis)
- 24–48V native power delivery

**Software**
- C++ inverse kinematics (runs natively on ESP32-S3)
- FlowiseAI — visual AI workflow orchestration
- BabyAGI — autonomous task loop planning
- Real-time G-code interpretation + dynamic path planning

---

## Partner Tier System

Volume-based discount tiers applied automatically in the portal.

| Tier | Discount | Unlock Condition |
|---|---|---|
| Base | 0% | Default |
| Level 2 Partner | 10% | $500+ total volume |
| Industrial | 20% | $2,500+ total volume |

Partners also earn +5% tier boosts for each successful engineer referral (both parties receive the boost).

---


**Links:** Sponsorship · GitHub Repo · Manufacturing Cell · Media & Press

---

*Engineered by a designer, maker, and technical problem-solver. Built to make industrial desktop robotics accessible.*

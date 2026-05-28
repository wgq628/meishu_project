# Cold Start Recovery — Worked Example

## Scenario: Starting Fresh for "航空发动机卡脖子" Analysis

### Step 1: Scan

```bash
$ ls memory/analysis/ | sort -r | head -5
2026-05-23_工业软件卡脖子BCS战略.md
2026-05-23_半导体卡脖子BCS三阶战略.md
2026-05-23_昆仑流水线v2.0升级.md
index.md
```

`index.md` shows two BCS analyses — both structural matches for a new domain.

### Step 2: Load

Load from the most structurally similar prior report:

**From semiconductor BCS report (§1 Problem Framework):**
- Trust-ecology double lock, not pure tech gap
- Five-category root cause (A: tech / B: ecology / C: supply chain / D: organization / E: capital)

**From industrial software BCS report (§3 System Structure / §4 Circuits):**
- R5 data assetization circuit (data → Why annotation → knowledge graph → AI → feedback)
- R6 standards diplomacy circuit (STEP/PMI + CRA + AI interfaces)

### Step 3: Diff for Aviation Engine

| Element | Source | Reuse/Adapt/Build | Notes |
|---|---|---|---|
| BCS 3-stage framework | Semiconductor + Industrial software | **Reuse** | Proven cross-domain generic pattern |
| 5-category root cause | Semiconductor | **Reuse** | Known generic framework |
| R5 data assetization | Industrial software | **Adapt** | Engine testing data ≠ CAD modeling data; adjust data collection mechanism |
| R6 standards diplomacy | Industrial software | **Build** | Aviation has entirely different standards bodies (FAA/EASA/CAAC) |
| Unique element: certification | — | **Build** | Engine certification (FAR Part 33) has no parallel in software domains — may be primary bottleneck |

### Checklist Result

- [x] Structurally similar prior analysis found → loaded BCS framework + 5-category root cause
- [x] Reusable: BCS 3-stage pattern, root cause framework, R5 concept
- [x] Avoid: tendency to underestimate certification barriers in first analysis
- [x] Diff: certification regime as primary bottleneck (aviation-only), unique supply chain structure (Rolls-Royce/GE/PW oligopoly)

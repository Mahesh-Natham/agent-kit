# PhD profile (sources: Admin_&_Cotutelle documents and the Command Center sheet, read 2026-11-19)

## Thesis
- **EN:** AI-based dynamical EVRP under charge and availability constraints: towards sustainable and eco-friendly urban delivery.
- **FR:** IA pour le problème de tournées dynamiques de véhicules électriques sous contraintes de charge et disponibilité : vers une livraison urbaine durable et respectueuse de l'environnement.
- **Scope:** dynamic EVRP for last-mile delivery. It covers battery charge and battery-life constraints, limited fixed and swapping stations plus mobile chargers, charging time and cost, and time windows. The planned approach is OR baselines (MILP/CMDP, OR-Tools, ALNS), then safe deep RL (a GAT encoder with PPO and SoC action masking), then multi-agent RL (MAPPO) for the fleet and mobile chargers, then SIL and hardware validation on the Mahindra AEV test bench (Jetson + STM32).

## People
- **Candidate:** Durga Mahesh Natham ("Mahesh"). Gmail: the account the connectors are signed into. He also has a student Outlook account.
- **Director (Centrale Lille):** Prof. Abdelkader EL KAMEL, abdelkader.elkamel@centralelille.fr, CRIStAL lab.
- **Co-director (Mahindra University):** Prof. Sreedhar MADICHETTY, sreedhar.madichetty@mahindrauniversity.edu.in, Smart and Cyber Physical Systems Lab, École Centrale School of Engineering (ECSoE).
- **Graduate school (France):** MADIS-631, Centrale Lille. **India:** Mahindra University, Dept. of Electrical and Computer Engineering.

## Cotutelle rules (Joint Doctoral Thesis Supervision Agreement)
- Start date 01 Nov 2026. Three years of research, plus one year of compulsory coursework at Mahindra at the beginning. Dual registration is renewed **every year** at both institutions, and each country's registration deadline applies.
- **Alternating stays (18 months in each country):**
  - India: Nov 2026–Jan 2027, Aug 2027–Jan 2028, Aug 2028–Jan 2029
  - France: Feb–Jul 2027, Feb–Jul 2028, Feb–Jul 2029
  - At least 12 months must be spent in France.
- **CSI** (Individual Monitoring Committee) at the end of each academic year at Centrale Lille. A favourable opinion is required to re-register. Termination must be declared at least 2 months before the academic year starts.
- **30 training credits** are required by the graduate school before he can ask to defend. Research ethics, scientific integrity and open science training are mandatory.
- **Fees:** the CVEC must be paid when registering in France. Fees are paid at one institution per year, with at least one year at each.
- **In France:** French social security (or private insurance) and civil liability insurance are required.
- **Funding:** INR 55,000/month all-inclusive in India (Mahindra covers its 18 months). €2,300 gross/month (2026) in France (Centrale Lille covers its 18 months).
- **Defense:** in English, held in **India**. The jury has 4, 6 or 8 members, half from each country, at least 50% professors and at least half external. Centrale Lille must know the jury **8 weeks** before the defense. The two pre-defense reports are due **3 weeks** before.
- **Manuscript:** in English, with a French or bilingual title page, summaries in French and English, and a French summary of at least 2 pages.

## Command Center (Google Sheet "00_PhD_Master_Command_Center")
- Spreadsheet ID: `1EQhgXFWA8MRJCgLbdHtVmNkvTTZa5Iwi765dqSZJLQo`
- Tabs: `Agile_Roadmap`, `Literature_Matrix`, `Experiment_Ledger`, `Supervisor_Decisions`, `Cotutelle_&_ECTS_Admin`. Rows 1–7 are headers and KPIs (frozen). Data starts at row 8. Read row 7 for the column names before writing.
- **Roadmap milestones MS-00 to MS-13:**
  - MS-00: setup, Oct 2026
  - MS-01: literature (30–50 papers) and grid-world Q-learning, Nov 2026
  - MS-02: CC-CV battery and M/M/c queue models, Dec 2026
  - MS-03: UML and Gymnasium EVRPEnv, Jan 2027
  - MS-04: CMDP/MILP and ALNS baselines, Feb–Mar 2027
  - MS-05: GAT-PPO, Apr–May 2027
  - MS-06: conference paper (ITSC or IFAC) and CSI #1, Jun–Jul 2027
  - MS-07: Q1 journal (TR-C/E), Aug–Oct 2027
  - MS-08: SIL, SUMO/Simulink and CAN, Nov 2027–Jan 2028
  - MS-09: MAPPO with mobile chargers, Feb–Apr 2028
  - MS-10: GIS case study and CSI #2, May–Jul 2028
  - MS-11: hardware test bench, Aug–Oct 2028
  - MS-12: Q1 journal #2 (T-ITS or Applied Energy), Nov 2028–Jan 2029
  - MS-13: thesis and defense, Feb–Oct 2029
- **Admin rows ADM-001 to ADM-008:**
  - ADM-001: agreement signatures
  - ADM-002: France visa. Start 90 days before the Feb 2027 departure.
  - ADM-003: ethics, 5 ECTS
  - ADM-004: open science, 5 ECTS
  - ADM-005: French language, 10 ECTS
  - ADM-006: disciplinary courses, 10 ECTS
  - ADM-007: CSI #1, Jun–Jul 2027
  - ADM-008: CSI #2, Jun–Jul 2028
- Reading note for LIT-001 (Schneider 2014): Google Doc `1ZC-Dv5PmaumqtK26UfPQzHU5LmfPAXOAmfYiWzKaURs`.

## Folder map: `D:\Ph.D 2026-2027`
| Folder | Put here |
|---|---|
| `Admin_&_Cotutelle` | agreement, thesis subject, funding forms, visa, registration, insurance, CVEC receipts |
| `Advisor_Meetings` | meeting slides, agendas, minutes. Name them `YYYY-MM-DD_SUP-00N_<topic>` |
| `Coursework_&_ECTS` | course certificates and ECTS evidence. Name them `ADM-00N_<course>` |
| `LiteratureSurvey/01_EVRP_Foundations` | classic EVRP papers and their notes |
| `LiteratureSurvey/02_DRL_&_GAT` | learning-based routing (Kool, Nazari, Lin…) |
| `LiteratureSurvey/03_Battery_&_Queues` | CC-CV charging, station queues |
| `LiteratureSurvey/04_Mobile_Chargers` | mobile charging units |
| `LiteratureSurvey/05_Extra` | side topics (EV path planning and tracking survey 2022–2026, ADP tracking control) |
| `Projects/EVRP_DRL/01_UML_&_Math_Models` … `04_Saved_Checkpoints` | the main research code and models (Colab notebooks live in Drive) |
| `Projects/AEV` | Mahindra autonomous ground vehicle: Jetson + STM32, ROS 2 migration |
| `Publications_&_Thesis/Paper1_Conference`, `Paper2_Journal_Q1`, `Paper3_Journal_Q1`, `Thesis_Manuscript` | papers and thesis |
| `Publications_&_Thesis/Drats` | side drafts: EV energy-aware planner (MATLAB/Simulink), snaking paper |
| `Extra` | tools (self-evolve etc.) |

Literature notes are named `LIT-00N_<FirstAuthor>_<Year>_<ShortTitle>_Reading_Note`.

## Things to watch (as of 2026-11-19)
- SUP-001 action ("finalize reading list and weekly sync slot") was due 2026-11-07 and is still Todo.
- SUP-002 action ("upload signed cotutelle agreement, confirm Feb 2027 France arrival logistics") is due 2026-11-30.
- MS-01 (30–50 papers) runs through November. The matrix has 5 papers logged, and the KPI cell says 7.
- The visa and Convention d'Accueil window is open now (Nov 2026–Jan 2027).

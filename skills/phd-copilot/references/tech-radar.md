# Tech radar: staying current, and AI agents in the thesis

Mahesh wants to finish the PhD as someone fluent in five areas, not only EVRP:
- **AI**, especially agents;
- **power electronics**;
- **autonomous vehicles**;
- **electric vehicles and charging**;
- **entrepreneurship**.

This file covers the twice-daily news brief, the `Tech_Radar` log, and how agentic AI can enter the research.

## 1. Tracks to watch

| Track | What counts | Typical sources |
|---|---|---|
| AI agents | New agent frameworks, protocols (MCP, A2A), tool use, multi-agent systems, agent benchmarks, LLM + optimisation | Anthropic, OpenAI and Google DeepMind blogs; arXiv cs.AI / cs.MA; Hugging Face blog |
| AI/ML research | RL, graph neural nets, neural combinatorial optimisation, LLMs for operations research, foundation models for driving | arXiv (cs.LG, math.OC), NeurIPS / ICML / ICLR, Papers with Code |
| Dev tools | Languages and tools worth learning: Rust for embedded and robotics, ROS 2 releases, JAX / PyTorch, uv, Zephyr / embedded Rust | Release notes, This Week in Rust, ROS Discourse |
| EV & charging | Batteries, charging standards (MCS, ISO 15118, V2G), fleet electrification, charging networks, EV policy in India and France | IEEE Spectrum, InsideEVs, Electrive, PIB India, French ministry pages |
| Power electronics | SiC / GaN devices, onboard chargers, 800 V platforms, motor drives, isolated gate drivers, ADAS power | IEEE PELS, Power Electronics News, Infineon / TI / ST application notes |
| Autonomy & robotics | AV companies, end-to-end driving, sim-to-real, low-speed campus or logistics autonomy, safety standards (ISO 26262, ISO 3691-4, UL 4600) | IEEE Spectrum, The Robot Report, company blogs |
| Startups & business | Funding in EV, charging, robotics and AI agents; business models; Indian and French startup programmes (Startup India, French Tech, Bpifrance) | TechCrunch, Inc42, YourStory, Sifted |
| Career & skills | Free courses, summer schools, conference deadlines, fellowships, competitions | University and conference pages |

## 2. Rules for a news item

- **Check it.** Only use items with a real source link from the last few days. Never invent a release, paper or number. If you're unsure, leave it out.
- **Relate it.** Each item says what it means for Mahesh. Name one of:
  - a thesis milestone (MS-01 … MS-13);
  - the AEV (Jetson, STM32, ROS 2, the VCU board);
  - one of the paper drafts;
  - his career goal.
- **Give an action.** Each item ends with a small next step:
  - "read section 3";
  - "try the quick-start on the EVRPEnv";
  - "note it for the related-work table";
  - "ignore unless X".
- **Avoid hype.** Say plainly when something is marketing, early or not yet useful for him.
- **No repeats.** Before choosing items, read the last ~60 `Tech_Radar` rows and skip anything already logged.

## 3. Brief format (email to his own address)

Subject: `[PhD] Tech radar AM – <date>` or `[PhD] Tech radar PM – <date>`. Plain text, under 350 words:

```
TOP 3 (most useful first)
1. <Item> (<track>) – <one line what it is>
   Why it matters for you: <thesis / AEV / career link>
   Next step: <one small action>  Link: <url>
2. ...
3. ...
QUICK HITS
- <one-liners for 2-4 other items, each with a link>
LEARN THIS WEEK (PM brief only)
- <one skill or concept, with a free resource>
```

The morning brief leans towards research, AI and agents. The evening brief leans towards EV, power electronics, autonomy and business. Both are open to anything important.

## 4. AI agents in the thesis (use when he asks how to "add agents")

Explain these simply and keep them tied to the existing plan. Don't rename the thesis. Agents are **layers around** the GAT-PPO core.

1. **LLM agent as the fleet operator interface (MS-08, MS-10).** The operator says, for example, "Station 4 is down until 15:00, prioritise hospital deliveries". A tool-using LLM agent turns this into constraint and mask updates for EVRPEnv, calls the trained GAT-PPO policy as a tool, and explains the new plan. The safety guarantee still comes from action masking, not from the LLM.
2. **LLM-generated heuristics as baselines or warm starts (MS-04).** This is an active research line in which LLMs evolve heuristics for routing problems. Examples to verify before citing: FunSearch (Romera-Paredes et al., Nature 2023), Evolution of Heuristics / EoH (Liu et al., ICML 2024), ReEvo (Ye et al., NeurIPS 2024). Comparing them against ALNS and GAT-PPO on Schneider's instances is a cheap, publishable side result.
3. **Multi-agent framing (MS-09).** MAPPO for EVs plus mobile chargers is already multi-agent RL. Position it against "agentic AI": learned agents with guarantees, compared with LLM agents that only plan in language.
4. **Agentic research workflow.** The co-pilot itself is an example: literature agents, experiment-tracking agents, and code agents for the ROS 2 rebuild. It's worth a methods paragraph or a workshop paper on "agent-assisted research on a cotutelle".
5. **On the AEV.** An LLM agent for the operator and diagnostics: it reads STM32 STATUS and ROS logs and explains faults. It never sits in the control loop, which keeps the safety case (the fail = brake rule) intact.

Always pair a suggestion with the risk: LLM output is not guaranteed, so anything that touches routing feasibility or vehicle motion must pass through masking, a solver check or the safety supervisor.

## 5. Tech_Radar tab (Command Center)

**Columns:**

| Column | Content |
|---|---|
| A | Date (YYYY-MM-DD) |
| B | Track (one of the 8 tracks above) |
| C | Item |
| D | Source_Link |
| E | What_It_Is |
| F | Why_It_Matters_For_Me |
| G | Action_Next |
| H | Status (`New`, `Try`, `Adopted` or `Parked`) |
| I | Thesis_Link (e.g. `MS-04`, `AEV`, `Paper: energy planner`, `Career`) |

- The header is on row 7 and data starts on row 8.
- Append only the TOP 3 items of each brief. Never delete or clear rows.
- When Mahesh tries or adopts something, update its Status. In the weekly review, mention any item in `Try` that is more than 14 days old.

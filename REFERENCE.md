# 📖 REFERENCE.md: Biological Foundation & Scientific Validation
### 🎯 Project Framework: `game-of-agents`
### 🧠 A Non-Biologist's Guide to Quorum Sensing, Colony Phases, and Emergent Systems

This document maps the software of **The Symbiosis Engine** onto the biology it borrows from. It describes the engine **as it runs today** (as of 2026-10-16). It also says where each analogy holds and where it breaks, because a model is only useful if you know its limits.

The original design vision (cell ages, resource pools, competing colonies) is kept at the end under [Part 5](#-part-5-original-design-vision-not-yet-built). None of it is implemented yet.

---

## 🗺️ The Engine at a Glance

The engine has two layers running at two speeds:

| Layer | Speed | What it does | Code |
|---|---|---|---|
| **Physics** | every frame (15 FPS) | Applies Conway's four rules to every cell at once | `next_board()` in `src/board.py` |
| **Quorum sensing coordinator** | requested every 50 epochs (about every 100 in practice) | Claude reads colony telemetry and picks one environmental event | `src/workflow.py`, applied in `_apply_decision()` in `src/app.py` |
| **Observation** | every epoch / every AI call | ClickHouse records what the colony did; Langfuse records what the AI thought | `src/telemetry.py`, `@observe` in `src/workflow.py` |

**The key design rule:** the AI never changes a cell's rules. It only changes the *state* of the board (which cells are alive) between generations. On the next frame the same four rules run on whatever board they are given. In maths terms, the AI perturbs the **state**, never the **transition function**.

| Biology | Cellular automaton term | In the code |
|---|---|---|
| alive or dead | State | `1` or `0` in the grid |
| senses molecules at its own surface | Neighbourhood | the 8 surrounding squares |
| its chemistry reacts | Rule | Conway's 4 rules |
| every cell, at the same moment | Time step | one `step()` call |

---

## 🔬 Part 1: The Physics Layer (Conway's Four Rules)

> **Software Logic:** Every cell counts its 8 live neighbours. A dead cell with exactly 3 becomes alive. A live cell with 2 or 3 survives. Fewer than 2: it dies of isolation. More than 3: it dies of overcrowding. Every cell updates at the same moment.

### The Real Science: Local Information Only
A bacterium is 1–2 µm long, so about 500 side by side span a millimetre. It has no brain and no nervous system. It reacts only to molecules touching its own surface: nutrients, toxins, and signals from neighbours. The Game of Life is a cartoon of that one constraint: **each cell knows only its immediate neighbourhood.**

1. **Birth needs neighbours.** In the model, a cell is only born next to exactly three living ones. Real bacteria divide on their own, but many depend on neighbours for shared enzymes, protection and signalling. That is the cooperative side of colony life.
2. **Death by isolation is the Allee effect.** Some populations decline below a critical density because individuals need others to survive. Conway's rule is an extreme version: a lone cell always dies. A probe on 2026-10-16 showed that **39 of 40 randomly placed cells die in the very next generation** on a sparse board. That is why NUTRIENT_BOOST barely helps (see Part 3).
3. **Death by overcrowding is competition.** Crowded cells compete for nutrients and poison each other with waste. The model compresses all of that into "more than 3 neighbours".
4. **Simultaneous update is double buffering.** Every cell in generation N+1 must be computed from the *same* generation N. The code reads from one grid and builds a new one, then swaps. Real cells copy DNA the same way: replication is *semiconservative*, building a new strand against the old one before the old one is released.

### Where the analogy breaks
Real cells change their behaviour in response to the environment by switching genes on and off. Conway cells have one fixed rulebook forever. This is deliberate: it keeps the question clean.

### 🔗 Recommended Reading
* What a cellular automaton is: [Cellular automaton](https://en.wikipedia.org/wiki/Cellular_automaton)
* The rules, patterns and history: [Conway's Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life)
* Why isolated cells die: [Allee effect](https://en.wikipedia.org/wiki/Allee_effect)
* How DNA is copied against the old strand: [Semiconservative replication](https://en.wikipedia.org/wiki/Semiconservative_replication)

---

## 🧠 Part 2: The Quorum Sensing Coordinator

> **Software Logic:** A decision is requested every 50 epochs, but only if the previous Claude call has finished. Calls take about 4–5 seconds (60–75 epochs), so in practice Claude decides about every 100 epochs. It receives a board summary (epoch, alive count, density) and the last 10 rows of telemetry. Its instructions give it thresholds: boost below 5% density, cull above 40%, sporulate below 2%, otherwise do nothing. It answers with one decision and a one-sentence reason. The decision is applied to the board when the answer arrives and logged to telemetry once, on that epoch.

### The Real Science: Quorum Sensing
Bacteria constantly release small signalling molecules called **autoinducers**. When the colony is sparse, the molecules drift away. As the colony grows, the concentration builds up. When the concentration *at an individual cell's surface* crosses a threshold, that cell switches on new genes. Because every cell sees roughly the same concentration, they all switch at about the same time, and the colony acts together.

No cell counts the colony, votes, or "realises" anything. Each one reacts to a local chemical level. Coordination emerges from many cells crossing the same threshold.

**The classic example** is *Aliivibrio fischeri* (formerly *Vibrio fischeri*) living in the Hawaiian bobtail squid. The bacteria glow only once enough of them have gathered in the squid's light organ. The squid uses that glow to cancel out its shadow in moonlight (counter-illumination), hiding it from predators below.

### Where the analogy breaks
Real quorum sensing is **distributed**: every cell senses for itself. The engine's coordinator is **centralised**: one observer sees the whole board and acts on it. That difference is the experiment. *Does a thinker with a global view do better than local thresholds?* In test runs, Claude's reasoning quoted its density thresholds almost every time ("0.8% density, well below the 2% crash threshold"). In effect, the "brain" behaved like a quorum sensing threshold.

Two more known limits:
* **Claude cannot see its own past decisions.** It sees only the last 10 epochs, and decisions are about 100 epochs apart, so it cannot tell whether an earlier intervention helped.
* **It acts on old data.** Each decision lands 60–75 epochs after the snapshot it was based on.

### 🔗 Recommended Reading
* The talk to start with: [Bonnie Bassler: How bacteria "talk"](https://www.ted.com/talks/bonnie_bassler_how_bacteria_talk)
* [Quorum sensing](https://en.wikipedia.org/wiki/Quorum_sensing) and [Autoinducer](https://en.wikipedia.org/wiki/Autoinducer)
* The squid partnership: [Hawaiian bobtail squid](https://en.wikipedia.org/wiki/Hawaiian_bobtail_squid) and [Aliivibrio fischeri](https://en.wikipedia.org/wiki/Aliivibrio_fischeri)
* Primary source: Waters & Bassler (2005), *Quorum sensing: cell-to-cell communication in bacteria*: [doi:10.1146/annurev.cellbio.21.012704.131001](https://doi.org/10.1146/annurev.cellbio.21.012704.131001)

---

## 🌦️ Part 3: The Four Interventions (Environmental Events)

Each intervention is a **one-off event** applied between two generations. None is a lasting "mode" or "stage". After each one, the cells go straight back to the same four rules.

All four map onto the **bacterial growth curve**. Put a few bacteria into fresh food and the population moves through four phases: **lag** (adjusting), **log** (explosive growth), **stationary** (births balance deaths) and **death** (decline as food runs out and waste builds up). Each intervention answers one phase:

| Intervention | Phase it answers | Event in the story |
|---|---|---|
| NUTRIENT_BOOST | death / famine | food arrives |
| PHAGE_CULL | log / boom | a virus outbreak |
| SPORULATION | crash / near extinction | dormant spores wake up |
| HOMEOSTASIS | stationary / calm | nothing happens |

### 🍽️ NUTRIENT_BOOST
> **Software Logic:** Picks 40 random dead cells anywhere on the board and makes them alive (highlighted green). Requested when density is below 5% or the colony is declining.

**The Real Science:** Fresh nutrients reaching a starving culture restart growth, like adding fresh broth to a dish. (The prompt calls this *chemotaxis*, which means cells swimming up a chemical gradient toward food. The model's cells cannot move, so "nutrient pulse" is the more accurate name.)

**Where the analogy breaks:** There is no food in the model. Cells do not eat; new cells simply appear. They are also placed at random rather than "in sparse regions" as the prompt says, and on a sparse board nearly all of them die of isolation in the next generation. The boost is the *story* of food, not its chemistry.

### ☣️ PHAGE_CULL
> **Software Logic:** Picks a random live cell and kills every live cell in a 16×16 square around it (highlighted red). Requested when density is above 40% or growth is explosive.

**The Real Science:** Bacteriophages ("phages") are viruses that infect only bacteria, and they are the most numerous biological entities on Earth. In the **lytic cycle**, a phage injects its DNA, turns the cell into a virus factory, and the cell bursts (**lysis**), releasing many new phages into its neighbours. Outbreaks spread fastest where bacteria are crowded, so phages naturally keep booming populations in check. Ecologists call this **"kill the winner"**. On a petri dish, an outbreak leaves a clear round hole in the lawn of bacteria called a **plaque**. The cleared square in the engine is its plaque.

**Where the analogy breaks:** The cull is centred on a *random* live cell, not the densest region the prompt describes. It happens instantly rather than spreading cell to cell. And because Conway colonies crash to 1–3% density quickly, the coordinator rarely chooses it.

### 🦠 SPORULATION
> **Software Logic:** Scatters 80 cells at random positions using `seed_random(80)`. A position that is already alive is flipped to dead, so a few existing cells can die. Requested when the population has crashed below 2%.

**The Real Science:** Some bacteria, such as *Bacillus* and *Clostridium*, respond to starvation by building an **endospore**: a dormant, armoured copy of the cell with its DNA sealed inside a coat that survives heat, drying and radiation. The parent cell dies making it, and the process takes hours, so it is an expensive last resort. The decision to sporulate is itself made by a threshold inside the cell, with no brain involved. When conditions improve, the spore **germinates** back into a living cell.

**Where the analogy breaks:** The prompt calls sporulation an "emergency reproduction burst". It is not: spores are for *surviving*, not reproducing. The engine's scatter is best described as *spores waking up*. Like the boost, scattered cells mostly die of isolation; in test runs three rounds of sporulation left density stuck at about 0.5%.

### ⚖️ HOMEOSTASIS
> **Software Logic:** Does nothing. Chosen when no threshold is crossed, or when Claude judges the colony is recovering on its own.

**The Real Science:** Homeostasis is a living system holding itself steady. At colony level, this is the stationary phase, where births and deaths balance and no outside help is needed.

**Notable moment:** In a test run at epoch 1129, Claude chose HOMEOSTASIS at 4.9% density, just *below* the 5% boost threshold, because the colony had been growing steadily. It was the first decision that weighed a trend over a threshold.

### 🔗 Recommended Reading
* The growth curve: [OpenStax Microbiology 9.1: How Microbes Grow](https://openstax.org/books/microbiology/pages/9-1-how-microbes-grow) and [Bacterial growth](https://en.wikipedia.org/wiki/Bacterial_growth)
* Phages: [Kurzgesagt: The Bacteriophage](https://www.youtube.com/watch?v=YI3tsmFsrOg), [Bacteriophage](https://en.wikipedia.org/wiki/Bacteriophage), [Lytic cycle](https://en.wikipedia.org/wiki/Lytic_cycle), [Plaque assay](https://en.wikipedia.org/wiki/Plaque_assay)
* Spores: [Endospore](https://en.wikipedia.org/wiki/Endospore)
* Steady state: [Homeostasis](https://en.wikipedia.org/wiki/Homeostasis)
* Primary sources: Thingstad (2000) on "kill the winner": [doi:10.4319/lo.2000.45.6.1320](https://doi.org/10.4319/lo.2000.45.6.1320) · Higgins & Dworkin (2012) on sporulation: [doi:10.1111/j.1574-6976.2011.00310.x](https://doi.org/10.1111/j.1574-6976.2011.00310.x)

---

## 🎲 Part 4: Emergence (Why the Simulation Is Worth Running)

> **Software Logic:** The board is seeded with 300 random cells. Nothing in the code describes gliders, oscillators, collapse or recovery. Those behaviours appear anyway.

### The Real Science: Behaviour With No One in Charge
**Emergence** is when a system shows behaviour that none of its parts has. A glider crosses the board, yet no cell moves: each one only lives or dies in place. The movement belongs to the pattern, not to any cell.

Biology is full of this. Bacteria coordinate through quorum sensing with no leader. The slime mould *Physarum polycephalum* has no neurons, yet it finds the shortest path through a maze and has grown networks resembling the Tokyo rail system. The research field that studies problem-solving without brains is called **basal cognition**.

### What is and is not emergent here
* **Emergent:** gliders, still lifes, oscillators, and the colony's collapse to 1–3% density. All of these come from the four local rules alone.
* **Not emergent:** the coordinator's decisions. They are explicit reasoning by one central model over thresholds written into its instructions.

That contrast is the point of the project: the emergent layer never makes a mistake, while the reasoning layer is only as good as the rules and data it is given.

### 🔗 Recommended Reading
* [Emergence](https://en.wikipedia.org/wiki/Emergence) and [Glider (Conway's Game of Life)](https://en.wikipedia.org/wiki/Glider_(Conway%27s_Game_of_Life))
* Brainless problem solving: [Physarum polycephalum](https://en.wikipedia.org/wiki/Physarum_polycephalum), Nakagaki et al. (2000) [doi:10.1038/35035159](https://doi.org/10.1038/35035159), Tero et al. (2010) [doi:10.1126/science.1177894](https://doi.org/10.1126/science.1177894)
* Basal cognition: Levin (2022), *Technological Approach to Mind Everywhere*: [frontiersin.org](https://www.frontiersin.org/articles/10.3389/fnsys.2022.768201/full)
* Where cellular automata are heading: [Growing Neural Cellular Automata (Distill, 2020)](https://distill.pub/2020/growing-ca/)

---

## 🧭 Part 5: Original Design Vision (Not Yet Built)

These six rules come from the first design of the engine, which imagined cell ages, a shared resource pool and two competing colonies. **None of them is implemented.** They are kept here as the roadmap and as good biology to build from later.

**Accuracy notes added on 2026-10-16:**
* *Contact inhibition* (Rule 2) is mainly described in animal cells; bacteria regulate density through quorum sensing and nutrient limits instead.
* Bacteria divide by *binary fission*, not *mitosis* (Rules 2 and 4).
* *Senescence* (Rule 4) is mainly a term for animal cells; the closest bacterial idea is dormancy (for example, spores or persister cells).
* In quorum sensing (Rule 3), cells do not "realise" they have a quorum; each reacts when the signal at its own surface crosses a threshold (see Part 2).

### 🔬 Rule 1: The Age-Fraction Resource Allocation
> **Software Logic:** A cell's resource consumption scales linearly with its age percentage. A newborn cell consumes very little (0.1 units), while an older, mature cell consumes the full allocation (1.0 unit).

#### The Real Science: Cell Growth and Surface-Area-to-Volume Constraints
In high school, you likely learned that cells divide to stay small. This is because of the **Surface-Area-to-Volume Ratio**.

1. **Newborn Phase:** When a cell splits, the resulting daughter cell is small. It has less cytoplasmic volume, fewer organelles, and its metabolic machinery is running at a baseline "maintenance" level.
2. **Growth Phase:** As the cell ages, it must physically expand. To do this, it must manufacture proteins, duplicate its cell wall components (lipids and peptidoglycans), and replicate its entire genome.
3. **Peak Consumption:** A mature cell preparing for division consumes drastically more carbohydrates (like glucose) and amino acids than a newborn cell because it is fueling the intensive structural assembly line needed to build a second cell.

#### 🔗 Recommended Reading
* [Surface-area-to-volume ratio](https://en.wikipedia.org/wiki/Surface-area-to-volume_ratio)
* [Cell cycle](https://en.wikipedia.org/wiki/Cell_cycle)

### 🧫 Rule 2: The 40% Density Threshold for Division
> **Software Logic:** When a colony fills up 40% of its spatial matrix quadrant, it hits a roadblock. It must halt local reproduction and initiate a macro-level division (mitosis) framework.

#### The Real Science: Contact Inhibition & Spatial Regulation
Cells do not grow blindly on top of each other into chaotic piles (unless they are cancerous). They are highly aware of their boundaries.

1. **Contact Inhibition:** In cellular biology, when a cell's membrane receptors physically bump into the receptors of a neighboring cell, a chemical signal is sent to the nucleus saying: *"We are out of room. Stop multiplying."*
2. **Biofilm Density:** In microbiology, bacterial and fungal colonies form structured sheets called biofilms. They monitor their physical boundaries to ensure they leave open microscopic channels between cell clusters. These channels act like plumbing, allowing fresh water and nutrients to flow into the deep layers of the colony. If they pass a specific density threshold, they lock down local growth to avoid choking off their own supply lines.

#### 🔗 Recommended Reading
* [Contact inhibition](https://en.wikipedia.org/wiki/Contact_inhibition)
* [Biofilm](https://en.wikipedia.org/wiki/Biofilm)

### 🧠 Rule 3: Chemical Signaling & The LangGraph Coordinator
> **Software Logic:** When a colony needs to divide but resources are low, the simulation pauses. A LangGraph workflow acts as a negotiation layer, forcing colonies to adjust their growth rates and share resources.

#### The Real Science: Quorum Sensing & Metabolic Cross-Feeding
Cells obviously don't speak English or pass JSON packets. However, they talk to each other constantly using a complex chemical language.

1. **Quorum Sensing:** Bacteria and fungi release tiny signaling molecules called *autoinducers* into their environment. If a colony is small, the molecules float away. But if the colony is large, the concentration of these chemicals builds up. Once it hits a threshold, the cells realize, *"We have a quorum (a majority)."* They instantly coordinate their behavior as a single, multi-cellular organism.
2. **Inter-Species Cross-Feeding:** When different species of cells live in the same dish, they don't just fight to the death. They engage in symbiotic negotiation. One colony will actively slow down its intake of a specific chemical, or secrete enzymes that break down waste for its neighbor, ensuring the entire ecosystem avoids total nutrient collapse. Your **LangGraph agent workflow** acts as a direct mathematical model of this chemical crosstalk.

#### 🔗 Recommended Reading
* [Quorum sensing](https://en.wikipedia.org/wiki/Quorum_sensing)
* [Symbiosis](https://en.wikipedia.org/wiki/Symbiosis)

### 🧬 Rule 4: Energy Surges vs. Growth Stagnation
> **Software Logic:** Dividing requires a massive lump-sum resource cost. If the shared pool is too low, the colony enters a permanent, non-replicating "Growth Stagnation" state.

#### The Real Science: G1/S Checkpoints & The Biological Stringent Response
Cell division is an all-or-nothing commitment. A cell cannot duplicate half its DNA and stop; doing so causes the cell to rupture and die.

1. **The G1/S Restriction Point:** Before a cell enters the replication phase, it passes through strict internal checkpoints. Special proteins act like safety inspectors, measuring the precise amount of available ATP (energy currency), amino acids, and lipids in the surrounding fluid. If the environment is impoverished, the cell cycle is completely blocked.
2. **The Stringent Response & Senescence:** When amino acid starvation is triggered, microbial cells activate a survival mode called the *stringent response*. They downregulate replication machinery and enter a dormant, non-dividing state called cellular **senescence**. The cells don't die immediately; they sit in a low-metabolic stagnation loop waiting for the environmental resource balance to recover.

#### 🔗 Recommended Reading
* [Cell cycle checkpoint](https://en.wikipedia.org/wiki/Cell_cycle_checkpoint)
* [Stringent response](https://en.wikipedia.org/wiki/Stringent_response)
* [Cellular senescence](https://en.wikipedia.org/wiki/Cellular_senescence)

### ☣️ Rule 5: Overcrowding & Disease Decay Loops
> **Software Logic:** Cells in highly crowded clusters (more than 5 neighbors) face an increased risk of catching a "disease" phase, turning red, draining massive system resources, and eventually disintegrating.

#### The Real Science: Phage Virulence Vectors & Lactic Acidosis Toxicity
In a crowded biological ecosystem, high density transforms an environment from a safe haven into a highly volatile danger zone due to two major natural laws:

1. **Viral Transmission (Bacteriophages):** In microbiology, viruses that target cells (phages) rely on physical proximity. In a loose, scattered population, viral particles struggle to find hosts. In an overcrowded cluster, a single infection spreads exponentially because host cell membranes are touching continuously.
2. **Metabolic Waste Suffocation:** Cells consume nutrients and excrete toxic byproducts (like lactic acid or ethanol). In an overcrowded cluster, the cells at the very center become trapped. Fresh nutrients can't get in, and toxic waste cannot diffuse out. This creates a highly acidic, toxic micro-environment. The trapped cells get sick, drain energy from the surrounding matrix trying to repair their cell walls, and eventually undergo **lysis** (they structurally burst and disintegrate into empty space).

#### 🔗 Recommended Reading
* [Bacteriophage](https://en.wikipedia.org/wiki/Bacteriophage)
* [Lysis](https://en.wikipedia.org/wiki/Lysis)

### 🎲 Rule 6: Emergent System Behavior (Simulation Worthiness)
> **Software Logic:** Initial seeding layout, cellular lifespans, and infection rates are randomized. The system avoids fixed, deterministic outcomes.

#### The Real Science: Chaotic Adaptation and Macro Evolution
Because individual cellular attributes operate on stochastic (randomized) variables, the simulation demonstrates **emergent complexity**—meaning simple local actions generate wildly unpredictable ecosystem states. Every time you run the simulation, it will self-organize into one of three distinct biological phenotypes:

1. **The Symbiotic Equilibrium:** Both colonies expand evenly. The LangGraph signaling protocol successfully negotiates staggered division windows. Nutrients dynamically deplete and recover in a perfect balanced loop.
2. **The Stagnant Deadlock:** An early, localized disease outbreak spikes resource drainage. The global ecosystem drops below the 250-unit threshold required for mitosis. The entire board enters chronic senescence and stops growing.
3. **The Competitive Monopolisation:** One colony experiences an evolutionary "speed lottery" run. It hits its 40% capacity early, consumes the initial resource buffer via a LangGraph contract, and expands its physical footprint—starving out the rival colony via pure spatial exclusion.

#### 🔗 Recommended Reading
* [Emergence](https://en.wikipedia.org/wiki/Emergence)

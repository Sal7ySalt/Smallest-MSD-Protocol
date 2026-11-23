# Smallest Magic-State Distillation Protocols

Simulation code, data and figures for the 2-qubit ([[2,1,1]]) and 3-qubit
([[3,1,1]]) magic-state distillation (MSD) protocols. The repository covers:

- the physical-level protocols with one round or many rounds, input noise and
  circuit-level noise;
- the same protocols encoded in the Steane [[7,1,3]] code (logical level);
- a gate-synthesis study that adds each protocol's "exotic" magic gate to
  Clifford+T, with a phase-estimation benchmark.

## Paper

**arXiv link:** 

## Quick start

```bash
# 1. Environment. The repository has no requirements file; this suggested setup
#    matches the versions recorded under "Environment".
conda create -n qiskit python=3.13
conda activate qiskit
pip install qiskit==2.5.0 qiskit-aer==0.17.2 numpy scipy matplotlib sympy mpmath scikit-learn pylatexenc jupyter

# 2. Regenerate a figure from the saved data, e.g. the 3-qubit logical-level plot
cd notebooks/three_qubit/logical_level
jupyter notebook 21_qubits.ipynb     # run the setup cells, then "Loading data from cluster" onward

# 3. (Optional) Re-run a logical-level sweep; appends shots to the saved file
python src/msd/two_qubit/no_errors.py   # run from the repository root
```

Every notebook reads and writes data through paths relative to its own folder
(for example `../../../data/...`). Start Jupyter so that each notebook's working
directory is its own folder; this is Jupyter's default. Notebooks that import
`msd` find `src/` themselves by searching upward from the working directory,
so no installation is needed.

## Repository layout

```
src/msd/                 shared Python code (importable as `msd`)
  two_qubit/             Steane-encoded 2-qubit circuit, noise models, sweep scripts
  three_qubit/           Steane-encoded 3-qubit (21-qubit) circuit
  gate_synthesis/        sequence search (sequences.py) and phase estimation (qpe.py)
  flow_diagrams.py       polynomial Bloch map of a stabilizer code (not called by any notebook)
notebooks/               simulations and figure scripts, grouped like data/
  two_qubit/             physical_level/{one_round,multiple_rounds}, logical_level, stable manifold
  three_qubit/           idealized_performance, physical_level, logical_level
  gate_synthesis/        algorithm.ipynb, qpe/
data/                    saved results (.npz) behind every figure; same tree as notebooks/
figures/                 PNG figures (see the figure map below)
archive/                 superseded Steane experiments; not used for the results
```

Each notebook begins with a markdown cell that states its purpose, inputs,
outputs, conventions and any known problems with re-running it. Each module in
`src/msd` has a module docstring with the circuit layout and noise model.

## Environment

The saved outputs were produced in a conda environment named `qiskit` (the
notebooks' kernel name). That environment has Python 3.13, Qiskit 2.5.0
(some notebook outputs show 2.4.1), Qiskit Aer 0.17.2, NumPy 2.4,
SciPy 1.17, Matplotlib 3.10, SymPy 1.14, mpmath 1.3 and scikit-learn 1.8.
`notebooks/gate_synthesis/algorithm.ipynb` also imports `line_profiler`.
The plotting cells set `text.usetex = True` and therefore need a LaTeX
installation. The repository pins no versions; the list above records what
was installed, not tested minimums. The archived notebooks additionally use
`pandas`, `lmfit` and an older Qiskit API.

## Conventions used throughout

| Quantity | Convention |
|---|---|
| 2-qubit target state | $\lvert \psi_\star\rangle = R_y(\theta_\star)\lvert0\rangle$, $\sin\theta_\star = x_\star \approx 0.8393$; Bloch vector $(x_\star,0,z_\star)$ with $z_\star\approx0.5437$ the real root of $z^3+z^2+z=1$. It is the fixed point of the accepted-branch map $(x,z)\mapsto(2z,\,x^2)/(1+z^2)$, which succeeds with probability $(1+z^2)/2$. In code: `x_star`, `theta`/`theta_star`, gate id `EMS1`. |
| 3-qubit target state | $R_y(\theta)\lvert0\rangle$ with $\tan^2\theta=(\sqrt5-1)/2$; Bloch vector ≈ (0.618, 0, 0.786). In code: `theta`, gate id `EMS`. |
| Error rate | Depolarizing-equivalent parameter. An average infidelity $r$ on $d$ levels maps to $\lambda = r\,d/(d-1)$, the argument of Qiskit's `depolarizing_error`. For one qubit, error rate = $2(1-F)$. Implemented by `inf_to_error` in each notebook. |
| Convergence-axis noise | Called "stable-axis" in file names. The channel is $\rho\mapsto(1-p)\rho+p\lvert\bar k\rangle\langle\bar k\rvert$ with Bloch vector of $\lvert\bar k\rangle$ equal to $(-z_\star,0,-x_\star)$. Its `inf_to_error` divides by $1-\lvert\langle \psi_\star\vert\bar k\rangle\rvert^2$ (≈0.956), so the error rate equals $p$. |
| Hardware rates | Quantinuum H2-2: one-qubit gate 2.8e-5, two-qubit gate 8.3e-4, idle 1.2e-4, readout P(1\|0)=6.7e-4 (`spam0`), P(0\|1)=1.2e-3 (`spam1`). Sweeps use 1×…5× these values, and the x-axis is the converted one-qubit rate. |
| Post-selection | 2-qubit protocol: keep the output when the measured qubit reads 0. 3-qubit protocol: keep the output when both measured qubits read 00. At the logical level the measured blocks must have trivial Z-stabilizer parities and $\bar Z = 0$. |
| Qubit order | Qiskit is little-endian. In NumPy code, the leftmost `np.kron` factor is the highest-index Qiskit qubit. Exception: `three_qubit/idealized_performance/threshold.ipynb` is pure NumPy and calls the leftmost factor "qubit 0". |
| Steane blocks | Block-local qubit $j$ is global qubit `start + j`. Stabilizers act on {0,1,2,3}, {1,2,4,5} and {2,3,5,6}; the logical $\bar Z$ check uses {0,1,4}. |
| Uncertainties | Notebooks: 95% normal approximation, $1.96\sqrt{F(1-F)/N_\text{acc}}$. Sweep scripts and their plot: ±1 SEM from $\sum F^2$. Phase estimation: Holevo standard deviation of bootstrap estimates. |
| Error budget | At each rate, a component's output error rate as a fraction of the sum of the 1Q (or H), 2Q (CX/CZ) and Meas outputs, averaged over the rates. Each component run also includes the input noise. |
| Randomness | No fixed seeds anywhere. Aer seeds itself, and the phase-estimation and gate-synthesis code seeds from `time.time_ns()` or draws unseeded Haar unitaries. Saved `.npz` files are the reference results; re-runs agree only statistically. |

## From inputs to figures

There are no external inputs. Every result is simulated from the constants
above. Producing a figure takes two stages: (1) a simulation notebook or
script writes an `.npz` to `data/`, and (2) a plotting cell reads it. All
`.npz` files needed by the plotting cells are committed, so stage 1 is only
needed to regenerate data.

### Figure map

"Saved" means the cell calls `fig.savefig` with that path. "Commented"
means its `savefig` line is present but commented out. "Inferred" means no
cell saves the file, and the match is based on the panel layout and on
numbers in the image that equal values in the saved data.

| Figure | Produced by | Status | Data read |
|---|---|---|---|
| `figures/2Q_logical_plots.png` | `notebooks/two_qubit/logical_level/creating_plots.ipynb`, last cell (sweep data) | Commented. The committed image matches this cell's data and layout. The *earlier* cell (cluster data) has an active `savefig` to the same path and overwrites the figure if run. | `data/two_qubit/logical_level/depolarizing/logical_msd_*_sweep.npz` |
| `figures/3Q_logical_plots.png` | `notebooks/three_qubit/logical_level/21_qubits.ipynb`, final plot cell | Saved | `data/three_qubit/logical_level/cluster_logical_msd_*.npz`, `data/three_qubit/physical_level/physical_level_component_analysis.npz` |
| `figures/gate_synthesis.png` | `notebooks/gate_synthesis/algorithm.ipynb`, final plot cell | Commented | `data/gate_synthesis/xy_data_exotic_set{1,2,3}.npz` |
| `figures/repetition_code_combined.png` | `notebooks/two_qubit/physical_level/creating_plots.ipynb`, four-panel cell | Commented | `data/two_qubit/physical_level/multiple_rounds/{depolarizing_error_rates,stable_manifold_error_rates}.npz`, `.../one_round/depolarizing_error_rates.npz` |
| `figures/2Q_physical_plots.png` | `notebooks/two_qubit/physical_level/one_round/creating_plots.ipynb`, "together" cell | Inferred (table values 4.3e-2/3.8e-1/5.8e-1 and 3.6e-2/3.3e-1/6.3e-1 match the data) | `data/two_qubit/physical_level/one_round/*.npz` |
| `figures/2Q_noise_thresholds.png` | same notebook, "Threshold plots" cell | Inferred (thresholds 0.704 and 0.120) | same |
| `figures/3Q_physical_plots.png` | `notebooks/three_qubit/physical_level/physical_level.ipynb`, last cell | Inferred (1.9e-2/3.1e-1/6.7e-1) | `data/three_qubit/physical_level/physical_level_component_analysis.npz` |
| `figures/3Q_idealized_performance.png` | `notebooks/three_qubit/idealized_performance/creating_plots.ipynb` | Inferred (λ = 0.2085, threshold ≈ 0.319) | `data/three_qubit/idealized_performance/{scaling,threshold}.npz` |
| `figures/phase_estimation.png` | `notebooks/gate_synthesis/qpe/creating_plots.ipynb` | Inferred (exotic set 1 curve) | `data/gate_synthesis/qpe/final_plot_exotic_set1.npz` |
| `figures/repetition_code.png` | probably `notebooks/two_qubit/physical_level/creating_plots.ipynb` (first plot cell; its `savefig` names this file) | **Unverified**: the cell now draws four panels, the committed image has two | `data/two_qubit/physical_level/...` |
| `figures/2Q_multiple_distillation_rounds.png` | no current cell | **Unverified**: shows λ = 0.162 / 0.173, while the saved data hard-code λ = 0.1752 | likely `data/two_qubit/physical_level/multiple_rounds/*.npz` (older version) |
| `figures/stable_manifold_error_rates.png` | no current cell | **Unverified**: single-panel version of the stable-manifold decay | likely `.../multiple_rounds/stable_manifold_error_rates.npz` |
| `figures/flow_diagrams.png` | no current cell | **Unverified**: [[2,1,1]] and [[3,1,1]] flow diagrams. `src/msd/flow_diagrams.py` builds the maps, but no notebook calls it. | none |

### Stage 1: data producers

Run each notebook from its own directory. Shot counts and sweep ranges are
documented in each notebook's header cell.

**2-qubit protocol, physical level** (`notebooks/two_qubit/physical_level/`)

| Notebook | Writes |
|---|---|
| `one_round/depolarizing.ipynb` | `data/two_qubit/physical_level/one_round/depolarizing_error_rates.npz`: threshold curve plus per-component outputs |
| `one_round/stable_axis_noise.ipynb` | `.../one_round/stable_axis_error_rates.npz`: the same for convergence-axis input noise |
| `multiple_rounds/depolarizing.ipynb` | `.../multiple_rounds/depolarizing_error_rates.npz`: `output_error_rate_matrix` of shape (6 initial p, 36 rounds) |
| `multiple_rounds/stable_axis_noise.ipynb` | `.../multiple_rounds/stable_axis_error_rates.npz`: shape (6, 66) |
| `../stable_manifold.ipynb` | `.../multiple_rounds/stable_manifold_error_rates.npz`: 400 rounds from a point on the stable manifold (mpmath, 100 digits) |
| `multiple_rounds/{amplitude_damping,dephasing,pauli_noise,preparation_angle_noise}.ipynb` | nothing (exploratory) |

**2-qubit protocol, logical level** (Steane-encoded, 14 qubits)

- Sweep scripts (resumable; each run adds 500 000 shots per rate to the
  saved totals):
  ```bash
  python src/msd/two_qubit/no_errors.py      # -> logical_msd_no_errors_sweep.npz
  python src/msd/two_qubit/one_q_errors.py   # -> logical_msd_1q_errors_sweep.npz
  python src/msd/two_qubit/two_q_errors.py   # -> logical_msd_2q_errors_sweep.npz
  python src/msd/two_qubit/meas_errors.py    # -> logical_msd_meas_errors_sweep.npz
  python src/msd/two_qubit/all_errors.py     # -> logical_msd_all_errors_sweep.npz
  ```
  All outputs go to `data/two_qubit/logical_level/depolarizing/`. To start a
  sweep from zero, delete its file first.
- `notebooks/two_qubit/logical_level/{depolarizing,convergence_axis}.ipynb`
  read the cluster tallies `cluster_logical_msd_*.npz` and write
  `{depolarizing,convergence_axis}_error_rates.npz`, which the cluster-data
  plot cells use.

**3-qubit protocol** (`notebooks/three_qubit/`)

| Notebook | Writes |
|---|---|
| `idealized_performance/scaling.ipynb` | `data/three_qubit/idealized_performance/scaling.npz` (50 ideal rounds, fitted λ) |
| `idealized_performance/threshold.ipynb` | `.../idealized_performance/threshold.npz` (one-round threshold, pure NumPy) |
| `physical_level/physical_level.ipynb` | `data/three_qubit/physical_level/physical_level_component_analysis.npz` (infidelities, not error rates) |
| `logical_level/21_qubits.ipynb` | reads `cluster_logical_msd_*.npz` and saves `figures/3Q_logical_plots.png` |

**Gate synthesis** (`notebooks/gate_synthesis/`)

| Notebook | Writes |
|---|---|
| `algorithm.ipynb` | `exotic_set*_max6.pkl` next to the notebook (not committed); the figure uses the committed cluster results `data/gate_synthesis/xy_data_exotic_set*.npz` |
| `qpe/ideal.ipynb` | `data/gate_synthesis/qpe/{ideal,final_plot_ideal}.npz` (exact gates) |
| `qpe/exotic_set{1,2,3}.ipynb` | reads the cluster runs `qpe/exotic_set1_max10.npz`, `exotic_set2_max10.npz`, `exotic_set3_max8.npz` and writes `qpe/final_plot_exotic_set{1,2,3}.npz` |

## Data files

All files are NumPy `.npz` archives. Arrays are indexed by error rate (or by
round) in the order of the producing notebook. The `cluster_*.npz` files
hold raw tallies: `sum_fid_list` (sum of fidelities over accepted shots),
`accepted_list` and `total_shots`. They were produced on a computing cluster
by driver scripts that are **not** in this repository; the circuits are the
`logical_msd_*` functions in `src/msd/two_qubit/logical_{depolarizing,convergence}.py`
and `src/msd/three_qubit/logical.py`. The same applies to
`data/gate_synthesis/xy_data_exotic_set*.npz` and
`data/gate_synthesis/qpe/exotic_set*_max*.npz`. The latter contain Qiskit
gate objects and need `allow_pickle=True`.
`data/gate_synthesis/xy_data.npz` is not read by any notebook.

## Archive and other files

- `archive/steane_three_qubit/`: earlier Steane-encoding experiments for the
  3-qubit protocol, superseded by `src/msd/three_qubit/logical.py`. They are
  not used for any result and are not expected to run unchanged: one module
  imports a package that is not in this repository, and the notebooks use an
  older Qiskit API.
- `notebooks/two_qubit/stable_manifold_exploration.ipynb`: scratch notebook,
  moved from the repository root (where it was `test.ipynb`); exploratory
  only.
- `src/msd/two_qubit/hardware.py`: reference copy of the constants above;
  not imported anywhere.
- `.vscode/settings.json`: editor setting that selects the conda environment
  manager; it does not affect results.

## Known caveats

These are documented here and in the relevant cells. The code was **not**
changed.

1. **Post-selection key parsing in the logical-level modules.** With
   `conditional=True`, Aer keys saved states by the hex value of *all*
   classical bits. That includes the two 3-bit syndrome registers of the
   final error-correction round, which are the most significant bits. This was
   checked with Qiskit Aer 0.17.2. The modules take the leading 7 (2-qubit) or
   14 (3-qubit) characters of the zero-padded binary string as the
   measured-block bits. That is exact when both syndrome registers read 0. For
   shots with a nonzero final syndrome, the parity checks see syndrome bits
   instead of block bits, so such shots can be wrongly accepted or rejected.
   Affected files: `src/msd/two_qubit/logical_{depolarizing,convergence}.py`
   and `src/msd/three_qubit/logical.py`.
2. **Missing or renamed inputs.** These cells load
   `data/two_qubit/physical_level/one_round/convergence_axis_error_rates.npz`,
   which does not exist:
   - `notebooks/two_qubit/physical_level/one_round/creating_plots.ipynb`
   - the final-plot cell of `notebooks/two_qubit/logical_level/convergence_axis.ipynb`

   The data is saved as `stable_axis_error_rates.npz` in the same folder.
   Locally produced files such as `*.pkl`, `exotic_set1_max7.npz` and
   `three_qubit/logical_level/logical_msd_{all,no}_errors.npz` are also
   absent.
3. **Notebooks were executed out of order** and several do not run top to
   bottom as saved. The header cell of each affected notebook lists the
   cells involved. Examples:
   - an import of `SaveStatevector` is missing;
   - a variable is defined only inside a disabled string;
   - local-run cells unpack two values where the module now returns three;
   - `distillable_magic_states.ipynb` has an unclosed parenthesis.

   The committed outputs and `.npz` files are the reference results.
4. **Hard-coded fit values.** Both `multiple_rounds/*_error_rates.npz` files
   store `lambda_value = 0.1752`, a typed constant rather than the fit result.
5. **Convergence-axis gate rates.** In the convergence-axis notebooks,
   `inf_to_error` ignores `num_qubits`, so it also rescales the one- and
   two-qubit gate infidelities by ≈1.046 instead of by $d/(d-1)$.
6. **Physical-level 3-qubit H noise** acts only on the H gate on qubit 2. The
   final H gates on qubits 0 and 1 use the standard name, which the noise model
   does not target.

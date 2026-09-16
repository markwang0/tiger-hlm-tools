# tiger-hlm-tools

Tools for setting up and running Tiger HLM GPU (runoff) + Tiger HLM Routing on Princeton's Tiger cluster.

## Structure

```
tiger-hlm-tools/
├── tiger_hlm_setup/        # runoff + routing setup tools
│   ├── __init__.py
│   ├── lookup.py           # forcing lookup table generation
│   ├── partition_hybrid.py # GPU + CPU partition generation
│   ├── setup.py            # longterm / forecast / spinup orchestration
│   ├── defaults.py         # all defaults and SLURM settings
│   ├── utils.py            # shared helpers
│   └── templates/
│       ├── runoff.yaml
│       ├── routing.yaml
│       ├── runoff.slurm
│       ├── routing.slurm
│       └── hetjob_wrapper.sh
├── setup.py
├── requirements.txt
└── example.ipynb
```

## Installation

```bash
pip install git+https://github.com/atmichalek/tiger-hlm-tools.git
```

Then in any notebook or script:

```python
from tiger_hlm_setup import setup_longterm, setup_forecast, setup_spinup, generate_lookup
```

## Modes

**longterm** — multi-year run, initial conditions chained year-to-year  
**forecast** — single run from a specified date window with user-supplied IC files  
**spinup**   — repeat a single year N times, chaining states between cycles  

## Customization

- All SLURM settings (account, partition, email, time limits, module versions) live in `defaults.py:SLURM_DEFAULTS` and can be overridden per-call via `slurm_cfg={}`.
- Solver presets per region live in `defaults.py:SOLVER_PRESETS`. Add a new region key or pass solver fields directly in `runoff_inputs`.
- `generate_lookup(..., flip_dims=True)` handles products like IMERG where lat/lon array dimensions are transposed.
- Routing output `level` and `resolution` are configurable via `out_level` and `out_resolution` in `routing_inputs`.
- Runoff cleanup after routing is off by default; enable with `slurm_cfg={'remove_runoff': True}`.
- Spinup automatically generates runoff and then routing without outputs except final. Runoff is automatically removed. 


## GPU + CPU routing

### Create the routing partition file

Create once for each routing CSV:

```bash
PARAMS=/path/to/CONUS_West_routing_params.csv
PART=/path/to/project/partitions/West_g1c1.part # file to write, g1c1: one GPU rank, one CPU rank

mkdir -p "$(dirname "$PART")"  # make partitions directory if it doesn't exist
python -m tiger_hlm_setup.partition_hybrid "$PARAMS" 1 "$PART"
```

The builder writes the specified `.part` file and a `.part.txt` summary.
The partition file should be rebuilt if:
 - routing CSV changes
 - number of GPU or CPU ranks changes

Set these config values in the notebook:

```python
routing_inputs = {
    'params': '/path/to/CONUS_West_routing_params.csv',
    'partition_file': '/path/to/project/partitions/West_g1c1.part',
    'sav_path': '/path/to/West_sav.csv',
}
```

## Details

- Runoff module details: https://github.com/PrincetonUniversity/Tiger_HLM_GPU/wiki
- Routing module details: https://github.com/PrincetonUniversity/Tiger_HLM_Routing/wiki    

# V7 CORE++ — JARVIS Exfoliation Energy

Inference package from **AcuVizionAI** for the JARVIS `dft_3d` exfoliation-energy benchmark.

The package builds 196 composition and crystal-structure descriptors, loads the saved preprocessing parameters and FT-Transformer checkpoint, and generates predictions for the 81 benchmark test IDs.

| Item | Value |
|---|---|
| Model | `V7_COREPP_exfoliation` |
| Reported test MAE | **37.6200** |
| Default inference | CPU, `portable_tanh` profile |
| Benchmark submission | [JARVIS pull request #34](https://github.com/atomgptlab/jarvis_leaderboard/pull/34) |
| Project | [AcuVizionAI](https://acuvizionai.com/) |

## Quick start with Docker

Requires Git, Docker, and internet access for the first build and dataset download. Run these commands in Bash, including WSL on Windows:

```bash
git clone https://github.com/AcuVizionAI/V7_COREPP_exfoliation.git
cd V7_COREPP_exfoliation
docker build -t v7-corepp-exfoliation .
mkdir -p output
docker run --rm --mount "type=bind,source=$(pwd)/output,target=/output" v7-corepp-exfoliation
```

The default Docker command writes predictions to `output/reproduced/` and caches the structure archive in `output/cache/`.

The prediction directory must not already exist. For another run, choose a new directory while reusing the cache:

```bash
docker run --rm --mount "type=bind,source=$(pwd)/output,target=/output" v7-corepp-exfoliation --out-dir /output/reproduced_2 --cache-dir /output/cache
```

## Run directly with Python

Use **Python 3.10** and a dedicated environment. From the repository root, on Linux or WSL:

```bash
python3.10 -m venv .venv
.venv/bin/python -m pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python run.py --device cpu --profile portable_tanh --out-dir reproduced
```

On Windows PowerShell, create the environment with `py -3.10 -m venv .venv` and use `.\.venv\Scripts\python.exe` in place of `.venv/bin/python` in the remaining commands.

`run.sh` is a Bash wrapper around `run.py` and forwards the same arguments. It uses `python` by default; set `PYTHON_BIN` to select another Python executable.

## Inputs and outputs

On the first run, `run.py` downloads the pinned [JARVIS structure archive](https://figshare.com/ndownloader/files/38521619) and verifies its SHA-256 checksum. It selects the records in `test_ids.json` and passes their IDs, formulas, and atomic structures to the feature extractor.

A successful run creates these files in the selected output directory:

```text
AI-SinglePropertyPrediction-exfoliation_energy-dft_3d-test-mae.csv
AI-SinglePropertyPrediction-exfoliation_energy-dft_3d-test-mae.csv.zip
```

The CSV contains 81 rows with columns `id,prediction`, in the order recorded in `test_ids.json`. The ZIP contains that CSV. The script generates predictions; it does not calculate MAE.

To use an existing copy of the pinned archive:

```bash
.venv/bin/python run.py --data-zip /path/to/jdft_3d-12-12-2022.json.zip --out-dir reproduced_local
```

The archive must contain `jdft_3d-12-12-2022.json` and match this SHA-256:

```text
d4c64660e9e1fa45c82bd8868a96ec10162195eed69636445972c05550d8d0d6
```

## Command options

| Option | Default | Purpose |
|---|---|---|
| `--out-dir` | `reproduced` beside `run.py` | New directory for CSV and ZIP outputs; an existing directory is rejected. |
| `--cache-dir` | `.cache` beside `run.py` | Location for the downloaded structure archive. |
| `--data-zip` | Download/cache | Supply a local copy of the pinned archive. |
| `--device` | `cpu` | Choose `cpu` or `cuda`; CUDA requires a compatible PyTorch installation and GPU. |
| `--profile` | `portable_tanh` | CPU-compatible activation path. `historical_cuda` requires `--device cuda`. |

The Docker image uses CPU PyTorch and overrides the default output and cache paths to `/output/reproduced` and `/output/cache`.

## Package contents

| Path | Purpose |
|---|---|
| `featurize.py` | Composition and crystal-structure descriptors. |
| `model_inference.py` | Model definition, preprocessing loader, asset checks, and prediction. |
| `model/RAW_fold1.pth` | Saved model weights. |
| `model/preproc.json` | Saved feature preprocessing and model dimensions. |
| `model/REG_STATS_fold1.json` | Saved target normalization parameters. |
| `run.py`, `run.sh` | Inference entry points. |
| `requirements.txt`, `Dockerfile` | Dependency versions and container setup. |
| `test_ids.json` | Ordered list of 81 benchmark test IDs. |
| `metadata.json` | Submission and project metadata. |
| `AI-SinglePropertyPrediction-exfoliation_energy-dft_3d-test-mae.csv.zip` | Submitted prediction archive. |

## Troubleshooting

- **Package version mismatch:** use the Docker image or install the exact versions in `requirements.txt`. The entry point checks all six listed package versions.
- **Output directory already exists:** choose a new `--out-dir`; the script preserves existing output directories.
- **Dataset checksum mismatch:** obtain the pinned archive linked above. A different JARVIS dataset snapshot is not accepted by this entry point.
- **Missing or changed model asset:** restore the weight and preprocessing files from this repository. Their checksums are verified before inference.
- **CUDA unavailable:** use the default CPU configuration or install a compatible CUDA build of PyTorch 2.5.1.

## Contact

[AcuVizionAI](https://acuvizionai.com/) · Belgium

[kamran.soleimani@acuvizionai.be](mailto:kamran.soleimani@acuvizionai.be)

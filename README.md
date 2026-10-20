# V7 CORE++ — JARVIS Exfoliation Energy

Inference package from **AcuVizionAI** for the JARVIS `dft_3d` exfoliation-energy benchmark.

The package builds 196 composition and crystal-structure descriptors, loads the saved preprocessing parameters and FT-Transformer checkpoint, and generates predictions for the 81 benchmark test IDs.

| Item | Value |
|---|---|
| Model | `V7_COREPP_exfoliation` |
| Reported test MAE | **37.6200 meV/atom** (local evaluation on the 81 benchmark test IDs) |
| Default inference | CPU, `portable_tanh` profile |
| Benchmark submission | [JARVIS pull request #34](https://github.com/atomgptlab/jarvis_leaderboard/pull/34) |
| Project | [AcuVizionAI](https://acuvizionai.com/) |

The reported score was computed locally for the included submission predictions. The submission record is linked above. The [JARVIS task table](https://github.com/atomgptlab/alignn/blob/main/README.md) specifies exfoliation energy in **meV/atom**.

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
.venv/bin/python -m pip install --no-deps torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu
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

## Recorded CPU and CUDA replay

The submitted prediction values come from the historical CUDA inference path. Archived local checks on 13-14 October 2026 recorded:

| Inference path | Test MAE (meV/atom) | Maximum absolute prediction difference from the historical reference (meV/atom) |
|---|---:|---:|
| Historical CUDA, NVIDIA RTX 3090 | 37.6200093531 | 0 |
| Portable CPU, standalone replay | 37.6200084112 | 0.0000457763671875 |

Both scores round to **37.6200 meV/atom**. The historical CUDA replay matched its reference CSV byte for byte in the recorded environment; the portable CPU replay produced numerically close predictions, not identical CSV bytes.

These are results from the recorded environments, not a guarantee of identical output on every CPU or GPU. The archived checks preceded the submission's identifier-column rename to `id`; compare prediction values by ID when comparing files with different headers.

A further local CPU replay on **20 October 2026** is documented in [the replay evidence summary](evidence/replay_20261020.json). It used a fresh checkout and isolated environment at package commit `9f2e80d162e8f0681d04bfe287c69e1f450b1ac9`, with the pinned structure archive. All 81 IDs matched in order; the maximum prediction difference was `4.57763671875e-5` meV/atom, below the fixed `1e-4` tolerance. The archive bytes differ. This execution compared predictions without recomputing MAE; it does not replace the historical score evidence above. The inference code, model assets, and submitted predictions are unchanged in this license/documentation update.

## Package contents

To compare reproduced predictions with the submitted archive without reading benchmark targets:

```bash
.venv/bin/python verify.py AI-SinglePropertyPrediction-exfoliation_energy-dft_3d-test-mae.csv.zip reproduced/AI-SinglePropertyPrediction-exfoliation_energy-dft_3d-test-mae.csv.zip
```

The comparison requires 81 unique IDs in the same order, finite predictions, and a maximum absolute difference of `1e-4` meV/atom. It prints `PASS` or `FAIL` and returns a corresponding exit code. This checks prediction agreement; it does not compute a fresh benchmark score.

| Path | Purpose |
|---|---|
| `featurize.py` | Composition and crystal-structure descriptors. |
| `model_inference.py` | Model definition, preprocessing loader, asset checks, and prediction. |
| `model/RAW_fold1.pth` | Saved model weights. |
| `model/preproc.json` | Saved feature preprocessing and model dimensions. |
| `model/REG_STATS_fold1.json` | Saved target normalization parameters. |
| `run.py`, `run.sh` | Inference entry points. |
| `verify.py` | Compare reproduced predictions with the submitted ZIP. |
| `requirements.txt`, `Dockerfile` | Dependency versions and container setup. |
| `test_ids.json` | Ordered list of 81 benchmark test IDs. |
| `metadata.json` | Submission and project metadata. |
| `AI-SinglePropertyPrediction-exfoliation_energy-dft_3d-test-mae.csv.zip` | Submitted prediction archive. |

## Troubleshooting

- **Package version mismatch:** use the Docker image or install the exact versions in `requirements.txt`. The entry point checks all six listed package versions.
- **Output directory already exists:** choose a new `--out-dir`; the script preserves existing output directories.
- **Dataset checksum mismatch:** obtain the pinned archive linked above. A different JARVIS dataset snapshot is not accepted by this entry point.
- **Empty dataset download:** check network/proxy access or provide the pinned archive with `--data-zip`.
- **Missing or changed model asset:** restore the weight and preprocessing files from this repository. Their checksums are verified before inference.
- **CUDA unavailable:** use the default CPU configuration or install a compatible CUDA build of PyTorch 2.5.1.

## License

This package is **not open source**. It is licensed for benchmark reproduction
only: you may download, fork, run, and verify it to reproduce the results
submitted to the JARVIS Leaderboard exfoliation_energy (dft_3d) task. See
[LICENSE](LICENSE).

The Prediction Files, as defined in the LICENSE (the submitted prediction CSV,
its ZIP archive, and `metadata.json`), are contributed to the JARVIS
Leaderboard under that repository's license.

Any other use of the code or model weights, including commercial use,
fine-tuning, or research beyond this benchmark, requires written permission:
kamran.soleimani@acuvizionai.be.

## Contact

[AcuVizionAI](https://acuvizionai.com/) · Belgium

[kamran.soleimani@acuvizionai.be](mailto:kamran.soleimani@acuvizionai.be)

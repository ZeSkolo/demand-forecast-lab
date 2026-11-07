# Demand Forecast Lab

**Data science** · Leakage-conscious time-series forecasting with rolling-origin backtests.

## Run locally

Python 3.11+; no third-party packages required. From this directory:

```bash
python main.py demo
python main.py run example.json
python -m unittest discover -s tests -v
```

`example.json` is the input contract and contains only synthetic or fictional data. `core.run(payload)` returns a JSON-serializable result. Invalid inputs produce an error and a nonzero CLI exit code.

## What it implements

- Regular daily date validation and deterministic seasonal synthetic demand.
- Seven-day seasonal-naive and linear trend + weekday regression models.
- Rolling-origin holdouts with MAE, RMSE and WAPE; chooses the lower-MAE model.
- Refits the selected model on all historical observations to forecast the next 1–30 days.

## Design and limitations

Educational daily-demand model, not a promise of future business accuracy. Requires at least 42 consecutive daily nonnegative observations; irregular dates and missing values are rejected. Backtest selection can still overfit a short history. No holidays, exogenous regressors, probabilistic intervals or real retail data are included.

## Suggested next step

Add your own data and domain-specific acceptance tests. Read and understand the implementation before presenting it in interviews. No live deployment is implied.

<!-- AH-INDEPTH-DOCS:START -->
## In-depth engineering guide

### Problem and scope

Leakage-conscious time-series forecasting with rolling-origin backtests.

This is an independent runnable reference implementation, with synthetic sample input and explicit limits. It is not a deployed service or independently validated business result.

### Architecture and end-to-end flow

```text
Daily history → date/value validation → rolling-origin folds → compare seasonal-naive and trend/weekday models → selected-model forecast
```

| File | Responsibility |
|---|---|
| core.py | Domain validation and project-specific algorithm/state transitions |
| main.py | Bounded JSON CLI input, demo dispatch and JSON output |
| example.json | Exact reproducible sample input |
| tests/test_core.py | Unit and edge-case coverage |

### Design decisions and trade-offs

1. The seasonal-naive baseline reuses weekly behavior. The trend-plus-weekday regression combines a linear trend and calendar weekday effects using a pure-Python linear solver.

2. Rolling-origin seven-day folds preserve temporal order: validation observations are not used to fit earlier folds. Model selection uses backtest error rather than visual preference.

3. MAE, RMSE and WAPE measure different error properties. A forecast is a point estimate; prediction intervals, holidays, promotions and stockout effects are not modeled.

### Reproducible setup

Requires Python 3.11+ and no third-party Python packages. Run from this project folder:

```bash
python main.py demo
python main.py run example.json
python -m unittest discover -s tests -v
```

CLI inputs are JSON objects, bounded to 1 MB. Supported domain errors produce a JSON error on stderr and a nonzero exit; inspect the message rather than treating a failed run as a result. The demo does not require a model key, network access or production data.

### Exact example input

```json
{
  "horizon": 7
}
```

### Core implementation interfaces

| Callable | Boundary |
|---|---|
| `solve(a, b)` | Implementation boundary; see source for validation and return structure. |
| `predict(values, horizon, method)` | Implementation boundary; see source for validation and return structure. |
| `run(p)` | Implementation boundary; see source for validation and return structure. |

The Python `run` result is JSON-serializable. Inspect the source and `main.py run example.json` output for the exact return keys; do not assume another project’s result schema.

### Test coverage and reproducibility

- `tests/test_core.py::test_seasonal`
- `tests/test_core.py::test_forecast`
- `tests/test_core.py::test_no_leakage_dates`
- `tests/test_core.py::test_bad_horizon`
- `tests/test_core.py::test_bad_dates`

5 named tests are present in this folder. Run the command above to reproduce the local test results. Provider calls are mocked; Docker build/run was not executed; no real cloud/model/production-cluster validation is claimed.

### Security and failure boundaries

Educational daily-demand model, not a promise of future business accuracy. Requires at least 42 consecutive daily nonnegative observations; irregular dates and missing values are rejected. Backtest selection can still overfit a short history. No holidays, exogenous regressors, probabilistic intervals or real retail data are included.

Never commit .env, real API keys, runtime databases, approval material or customer data. See SECURITY.md. A successful example demonstrates the included workflow, not safe internet deployment.

### Troubleshooting

- **Import error:** run from this project’s own folder; each project intentionally has its own core.py.
- **Invalid sample/schema:** start from example.json, then change one field at a time and read the returned validation message.
- **Port already in use:** stop the previous process or select another --port where server.py exists.
- **SQLite lock/state surprise:** close duplicate processes, confirm PROJECT_DB and back up before deliberate resets. Do not delete unrelated project data.
- **External dependency unavailable:** default demos run offline; live provider calls and container pulls require your own working access and may incur external costs.

### Known limitations

Educational daily-demand model, not a promise of future business accuracy. Requires at least 42 consecutive daily nonnegative observations; irregular dates and missing values are rejected. Backtest selection can still overfit a short history. No holidays, exogenous regressors, probabilistic intervals or real retail data are included.

### Extension roadmap — not implemented

Add prediction intervals, exogenous regressors, hierarchical reconciliation and calendar-aware missing-data policy; validate on real demand before decisions.
<!-- AH-INDEPTH-DOCS:END -->

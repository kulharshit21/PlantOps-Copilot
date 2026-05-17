# Predictive Maintenance Model Report

No trained artifact is committed. Run:

```bash
python ml/training/train_failure_model.py --data ml/data/ai4i2020.csv
```

If `ml/data/ai4i2020.csv` is missing, the script uses a tiny synthetic fallback only to validate the pipeline. Metrics from fallback data must not be presented as real model performance.

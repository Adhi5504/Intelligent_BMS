from _helpers import ACCENT, WARNING, CRITICAL, INK, MUTED

BENCH_ROWS = [
    ["XGBoost", ("94.19%", ACCENT, True), ("0.905", MUTED, False), ("0.462 ms", ACCENT, True), ("1.40 MB", MUTED, False), ("Yes", ACCENT, False), ("Deployed — 1-row input, 10-row context", ACCENT, True)],
    ["Transformer", ("95.11%", INK, False), ("0.918", MUTED, False), ("0.419 ms", MUTED, False), ("0.31 MB", MUTED, False), ("Warn", WARNING, False), ("+0.92% acc; 60 rows locked in", WARNING, False)],
    ["LSTM", ("87.03%", INK, False), ("0.776", MUTED, False), ("0.532 ms", MUTED, False), ("0.28 MB", MUTED, False), ("Warn", WARNING, False), ("Sequential, weakest F1", MUTED, False)],
    ["Random Forest", ("89.37%", INK, False), ("0.824", MUTED, False), ("33.770 ms", MUTED, False), ("176.41 MB", MUTED, False), ("No", CRITICAL, False), ("176 MB, 73× the latency", CRITICAL, False)],
    ["SVM (RBF)", ("88.53%", INK, False), ("0.807", MUTED, False), ("0.568 ms", MUTED, False), ("2.82 MB", MUTED, False), ("Yes", ACCENT, False), ("Would not scale past 20k rows", MUTED, False)],
    ["Rule-based BMS", ("22.09%", INK, False), ("0.224", MUTED, False), ("5 µs", MUTED, False), ("~0 MB", MUTED, False), ("Yes", ACCENT, False), ("0% recall on Weak Cell", CRITICAL, False)],
]

BENCH_FOOT = (
    "All six trained and scored on the identical 30,000-row held-out split with the same 51 features; latency is the "
    "median single-row prediction on a 4-core CPU, not a Pi 5. Both models sit behind the same 60-row pipeline buffer, "
    "but XGBoost consumes only the last row and its deepest feature is a 10-sample rolling window, so that 60 is a "
    "constant we chose; the Transformer consumes all 60 and its positional encoding fixes the length in the weights. "
    "SVM trained on a stratified 20k subsample: full-data RBF did not converge."
)

BENCH_NOTES = """
We did not argue about which model to use — we trained all six on the identical
split and measured them. Two rows matter. The bottom one: a conventional
rule-based BMS scores twenty-two percent, because cell one\u2019s chronic gap puts
eighty-four percent of healthy rows over the imbalance threshold. It false-alarms
constantly and never detects a weak cell at all. And the second row: the
Transformer edges us by under a point — but look at what it costs. Both models
sit behind the same sixty-row buffer in our pipeline. The difference is that
XGBoost only eats the last row of it, and its deepest feature is a ten-sample
rolling window, so that sixty is a constant we chose and could shorten to ten
tomorrow. The Transformer eats all sixty, and its positional encoding fixes that
length inside the weights — you cannot shorten it without retraining. On top of
that, torch is five times the runtime footprint of xgboost on the Pi, it gives no
per-feature attribution an engineer can audit, and it cannot be retrained from
the browser the way our configurator retrains XGBoost today. That is why it
ships.
"""

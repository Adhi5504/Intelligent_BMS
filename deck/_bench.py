from _helpers import ACCENT, WARNING, CRITICAL, INK, MUTED

BENCH_ROWS = [
    ["XGBoost", ("94.19%", ACCENT, True), ("0.905", MUTED, False), ("0.462 ms", ACCENT, True), ("1.40 MB", MUTED, False), ("Yes", ACCENT, False), ("Deployed — 1 row, no buffer", ACCENT, True)],
    ["Transformer", ("95.11%", INK, False), ("0.918", MUTED, False), ("0.419 ms", MUTED, False), ("0.31 MB", MUTED, False), ("Warn", WARNING, False), ("Edges accuracy; 60-row buffer", WARNING, False)],
    ["LSTM", ("87.03%", INK, False), ("0.776", MUTED, False), ("0.532 ms", MUTED, False), ("0.28 MB", MUTED, False), ("Warn", WARNING, False), ("Sequential, weakest F1", MUTED, False)],
    ["Random Forest", ("89.37%", INK, False), ("0.824", MUTED, False), ("33.770 ms", MUTED, False), ("176.41 MB", MUTED, False), ("No", CRITICAL, False), ("176 MB, 73× the latency", CRITICAL, False)],
    ["SVM (RBF)", ("88.53%", INK, False), ("0.807", MUTED, False), ("0.568 ms", MUTED, False), ("2.82 MB", MUTED, False), ("Yes", ACCENT, False), ("Would not scale past 20k rows", MUTED, False)],
    ["Rule-based BMS", ("22.09%", INK, False), ("0.224", MUTED, False), ("5 µs", MUTED, False), ("~0 MB", MUTED, False), ("Yes", ACCENT, False), ("0% recall on Weak Cell", CRITICAL, False)],
]

BENCH_FOOT = (
    "All six trained and scored on the identical 30,000-row held-out split with the same 51 features; latency is the "
    "median single-row prediction on a 4-core CPU, not a Pi 5. The Transformer additionally receives a 60-row lookback "
    "window — 60× the input per prediction — which is where its 0.92-point accuracy edge comes from, and also why it "
    "cannot run on our hardware. SVM trained on a stratified 20k subsample: full-data RBF did not converge."
)

BENCH_NOTES = """
We did not argue about which model to use — we trained all six on the identical
split and measured them. Two rows matter. The bottom one: a conventional
rule-based BMS scores twenty-two percent, because cell one\u2019s chronic gap puts
eighty-four percent of healthy rows over the imbalance threshold. It false-alarms
constantly and never detects a weak cell at all. And the second row: the
Transformer edges us by under a point — but only because it is fed a sixty-row
window, sixty times the input per prediction. On our hardware that window is
disqualifying. At one hertz it is blind for a full minute after every restart,
its positional encoding pins the input at exactly sixty rows, torch is five times
the runtime footprint of xgboost on the Pi, and it gives no per-feature
attribution an engineer can audit. XGBoost predicts from a single row, instantly,
explains itself, and retrains from the browser. That is why it ships.
"""

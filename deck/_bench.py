from _helpers import ACCENT, WARNING, CRITICAL, INK, MUTED

BENCH_ROWS = [
    ["XGBoost", ("94.19%", ACCENT, True), ("0.905", MUTED, False), ("0.462 ms", ACCENT, True), ("1.40 MB", MUTED, False), ("Yes", ACCENT, False), ("Deployed — 1 row, no buffer", ACCENT, True)],
    ["Transformer", ("95.11%", INK, False), ("0.918", MUTED, False), ("0.419 ms", MUTED, False), ("0.31 MB", MUTED, False), ("Warn", WARNING, False), ("Best accuracy; 60-row warm-up", WARNING, False)],
    ["LSTM", ("87.03%", INK, False), ("0.776", MUTED, False), ("0.532 ms", MUTED, False), ("0.28 MB", MUTED, False), ("Warn", WARNING, False), ("Sequential, weakest F1", MUTED, False)],
    ["Random Forest", ("89.37%", INK, False), ("0.824", MUTED, False), ("33.770 ms", MUTED, False), ("176.41 MB", MUTED, False), ("No", CRITICAL, False), ("176 MB, 73× the latency", CRITICAL, False)],
    ["SVM (RBF)", ("88.53%", INK, False), ("0.807", MUTED, False), ("0.568 ms", MUTED, False), ("2.82 MB", MUTED, False), ("Yes", ACCENT, False), ("Would not scale past 20k rows", MUTED, False)],
    ["Rule-based BMS", ("22.09%", INK, False), ("0.224", MUTED, False), ("5 µs", MUTED, False), ("~0 MB", MUTED, False), ("Yes", ACCENT, False), ("0% recall on Weak Cell", CRITICAL, False)],
]

BENCH_FOOT = (
    "All six trained and scored here on the identical 30,000-row held-out split with the same 51 features; "
    "latency is the median single-row prediction on a 4-core CPU, not a Pi 5. "
    "Sequence models additionally see a 60-row lookback. SVM trained on a stratified 20k subsample — "
    "full-data RBF did not converge in usable time, which is part of the verdict."
)

BENCH_NOTES = """
We did not argue about which model to use — we trained all six on the identical
split and measured them. The Transformer is actually the most accurate at 95.11
percent, a point ahead of XGBoost. We still shipped XGBoost, and here is the
honest reason: the Transformer needs a sixty-row lookback, which at one hertz
means a full minute of buffered data before it can say anything, plus a torch
runtime on the Pi and no feature attribution an engineer can interrogate.
XGBoost predicts from a single row, instantly, and tells you which features
drove it. Random Forest is 176 megabytes and seventy-three times slower for
worse accuracy. And look at the bottom row: a conventional rule-based BMS scores
twenty-two percent — because cell one's chronic gap puts eighty-four percent of
healthy rows over the imbalance threshold, so it false-alarms constantly and
still never detects a weak cell.
"""

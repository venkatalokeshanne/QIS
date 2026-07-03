"""
Shared Hilbert Transform engine (Ehlers' "MESA" cycle-measurement
algorithm, as popularized by TA-Lib's HT_* indicator family and MAMA).

All seven Hilbert-Transform-based indicators (ht_trendline, ht_sine,
ht_dcperiod, ht_dcphase, ht_phasor, ht_trendmode, mama) derive from the
SAME recursive smoothing/detrending/period-discriminator loop -- so it
lives here once and each indicator file just picks the column(s) it
needs, rather than re-deriving (and risking divergent bugs in) the
same feedback loop seven times.

This is a best-effort port of Ehlers' published algorithm (the one
widely replicated across open-source TA libraries). It has NOT been
diffed bar-for-bar against TA-Lib's C implementation (not available in
this environment) -- treat exact values as approximate, though the
shape/behavior (dominant cycle period, trend/cycle mode, sine/lead
sine crossovers) follows the documented algorithm.
"""

import numpy as np
import pandas as pd


def hilbert_transform(df: pd.DataFrame, fast_limit: float = 0.5, slow_limit: float = 0.05) -> pd.DataFrame:
    price = ((df["high"] + df["low"]) / 2).to_numpy(dtype=float)
    n = len(price)

    smooth = np.zeros(n)
    detrender = np.zeros(n)
    i1 = np.zeros(n)
    q1 = np.zeros(n)
    ji = np.zeros(n)
    jq = np.zeros(n)
    i2 = np.zeros(n)
    q2 = np.zeros(n)
    re = np.zeros(n)
    im = np.zeros(n)
    period = np.full(n, 15.0)
    smooth_period = np.full(n, 15.0)
    phase = np.zeros(n)
    dcphase = np.zeros(n)
    sine = np.zeros(n)
    leadsine = np.zeros(n)
    trendmode = np.zeros(n)
    trendline = price.copy()
    mama = price.copy()
    fama = price.copy()

    def p(arr, i, lag):
        j = i - lag
        return arr[j] if j >= 0 else arr[0]

    for i in range(n):
        if i < 6:
            continue

        smooth[i] = (4 * price[i] + 3 * p(price, i, 1) + 2 * p(price, i, 2) + p(price, i, 3)) / 10
        adj = 0.075 * period[i - 1] + 0.54

        detrender[i] = (
            0.0962 * smooth[i] + 0.5769 * p(smooth, i, 2) - 0.5769 * p(smooth, i, 4) - 0.0962 * p(smooth, i, 6)
        ) * adj

        q1[i] = (
            0.0962 * detrender[i] + 0.5769 * p(detrender, i, 2) - 0.5769 * p(detrender, i, 4) - 0.0962 * p(detrender, i, 6)
        ) * adj
        i1[i] = p(detrender, i, 3)

        ji[i] = (0.0962 * i1[i] + 0.5769 * p(i1, i, 2) - 0.5769 * p(i1, i, 4) - 0.0962 * p(i1, i, 6)) * adj
        jq[i] = (0.0962 * q1[i] + 0.5769 * p(q1, i, 2) - 0.5769 * p(q1, i, 4) - 0.0962 * p(q1, i, 6)) * adj

        i2_raw = i1[i] - jq[i]
        q2_raw = q1[i] + ji[i]
        i2[i] = 0.2 * i2_raw + 0.8 * i2[i - 1]
        q2[i] = 0.2 * q2_raw + 0.8 * q2[i - 1]

        re_raw = i2[i] * i2[i - 1] + q2[i] * q2[i - 1]
        im_raw = i2[i] * q2[i - 1] - q2[i] * i2[i - 1]
        re[i] = 0.2 * re_raw + 0.8 * re[i - 1]
        im[i] = 0.2 * im_raw + 0.8 * im[i - 1]

        if re[i] != 0 and im[i] != 0:
            new_period = 360.0 / np.degrees(np.arctan(im[i] / re[i]))
        else:
            new_period = period[i - 1]

        if new_period > 1.5 * period[i - 1]:
            new_period = 1.5 * period[i - 1]
        elif new_period < 0.67 * period[i - 1]:
            new_period = 0.67 * period[i - 1]
        new_period = min(max(new_period, 6.0), 50.0)
        period[i] = 0.2 * new_period + 0.8 * period[i - 1]
        smooth_period[i] = 0.33 * period[i] + 0.67 * smooth_period[i - 1]

        if i1[i] != 0:
            phase[i] = np.degrees(np.arctan(q1[i] / i1[i]))
        delta_phase = phase[i - 1] - phase[i]
        if delta_phase < 1:
            delta_phase = 1
        dcphase[i] = phase[i]

        sine[i] = np.sin(np.radians(phase[i]))
        leadsine[i] = np.sin(np.radians(phase[i] + delta_phase))

        trendmode[i] = 1.0 if smooth_period[i] > 0 and abs(smooth_period[i] - smooth_period[i - 1]) / max(smooth_period[i], 1e-9) < 0.15 else 0.0

        dc_period = int(round(smooth_period[i]))
        dc_period = max(dc_period, 1)
        lookback = min(dc_period, i)
        trendline[i] = price[i - lookback : i + 1].mean() if lookback > 0 else price[i]

        # MAMA's own adaptive alpha is phase-delta-based in Ehlers' original;
        # approximated here via the dominant cycle period, clamped to the
        # same [slow_limit, fast_limit] band.
        adaptive_alpha = fast_limit / max(smooth_period[i], 1.0)
        adaptive_alpha = min(max(adaptive_alpha, slow_limit), fast_limit)
        mama[i] = adaptive_alpha * price[i] + (1 - adaptive_alpha) * mama[i - 1]
        fama[i] = 0.5 * adaptive_alpha * mama[i] + (1 - 0.5 * adaptive_alpha) * fama[i - 1]

    idx = df.index
    return pd.DataFrame(
        {
            "dcperiod": period,
            "smooth_period": smooth_period,
            "dcphase": dcphase,
            "inphase": i2,
            "quadrature": q2,
            "sine": sine,
            "leadsine": leadsine,
            "trendmode": trendmode,
            "trendline": trendline,
            "mama": mama,
            "fama": fama,
        },
        index=idx,
    )

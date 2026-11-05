"""Procedural hype music + tonal SFX (no samples, no copyright). 48 kHz mono numpy."""
import math
import numpy as np
SR = 48000

def _env(n, a=0.003, r=None):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    if r: e *= np.exp(-np.arange(n) / (r * SR))
    return e

def kick(dur=0.32):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 28); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9) * 1.0 + np.sin(ph * 0.5) * np.exp(-t * 6) * 0.25

def clap(dur=0.22, seed=1):
    n = int(dur * SR); t = np.arange(n) / SR; r = np.random.default_rng(seed).standard_normal(n)
    r = np.diff(np.concatenate([[0], r]))                       # brighter
    tone = np.sin(2 * np.pi * 190 * t) * 0.3
    return (r * 0.12 + tone * 1.4) * np.exp(-t * 26)

def hat(dur=0.035, seed=2):
    """metallic tonal hat (sum of inharmonic square-ish partials) instead of noise"""
    n = int(dur * SR); t = np.arange(n) / SR
    x = sum(np.sign(np.sin(2 * np.pi * f * t)) for f in (5200, 6630, 7810, 9140)) / 4
    return x * np.exp(-t * 110) * 0.05

def saw(freq, dur, detune=0.006):
    n = int(dur * SR); t = np.arange(n) / SR; out = np.zeros(n)
    for dt in (-detune, 0, detune):
        out += 2 * ((t * freq * (1 + dt)) % 1) - 1
    return out / 3

def lowpass_fft(x, cutoff):
    if cutoff >= SR / 2: return x
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / cutoff) ** 6)
    return np.fft.irfft(X, len(x))

def pluck(freq, dur=0.25):
    n = int(dur * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * freq * t) + 0.4 * np.sin(4 * np.pi * freq * t)) * np.exp(-t * 14)

def riser(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 200 * (8 ** (t / dur)); ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * 0.5 + np.sin(ph * 1.5) * 0.25) * (t / dur) ** 2

def boom(dur=1.6):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 32 + 60 * np.exp(-t * 6); ph = 2 * np.pi * np.cumsum(f) / SR
    out = np.sin(ph) * np.exp(-t * 2.2)
    c = clap(0.3, 7); out[: len(c)] += c[: n]
    return out

def gun():
    n = int(0.5 * SR); t = np.arange(n) / SR
    crack = np.random.default_rng(5).standard_normal(n) * np.exp(-t * 60) * 0.6
    return crack + np.sin(2 * np.pi * 60 * t) * np.exp(-t * 7)

def tick(freq=1500):
    n = int(0.06 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * freq * t) * np.exp(-t * 60)

def beep(freq=880, dur=0.22):
    n = int(dur * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * freq * t) * np.minimum(1, (dur - t) * 40) * 0.8

def heartbeat():
    n = int(0.55 * SR); t = np.arange(n) / SR; x = np.sin(2 * np.pi * 50 * t) * np.exp(-t * 16)
    sh = int(0.19 * SR); x[sh:] += (np.sin(2 * np.pi * 46 * t) * np.exp(-t * 20))[: n - sh] * 0.7
    return x

def sting():
    """reveal stinger: rising major chord stab + boom"""
    out = np.zeros(int(1.6 * SR))
    for f in (220, 277.18, 329.63, 440):
        s = saw(f, 1.6, 0.004) * np.exp(-np.arange(int(1.6 * SR)) / SR * 2.5); out += s * 0.22
    out = lowpass_fft(out, 3500); b = boom(1.6); out[: len(b)] += b * 0.9
    return out

def place(buf, sig, t, gain=1.0):
    i = int(t * SR)
    if i < 0: sig = sig[-i:]; i = 0
    j = min(len(buf), i + len(sig))
    if i < len(buf) and j > i: buf[i:j] += sig[: j - i] * gain

def track(total, t_drop, t_slow0, t_slow1, t_board, bpm=140, root=110.0):
    """beat that drops at t_drop, muffles in slow-mo (t_slow0..t_slow1), lighter groove on the board."""
    n = int(total * SR); mus = np.zeros(n); beat = 60 / bpm
    prog = [0, -4, 3, -2]                          # A minor-ish: A F C G (semitones)
    k_, c_, h_ = kick(), clap(), hat()
    # pre-drop pad (tension) from 0 to drop
    pad_len = max(0.1, t_drop)
    pad = (np.sin(2 * np.pi * root * np.arange(int(pad_len * SR)) / SR) + 0.5 * np.sin(2 * np.pi * root * 1.5 * np.arange(int(pad_len * SR)) / SR))
    pad *= np.linspace(0.15, 0.45, len(pad)); place(mus, lowpass_fft(pad, 900), 0, 0.5)
    t = t_drop; i = 0
    end = total
    while t < end:
        bar = int(i // 16); note = root * 2 ** (prog[bar % 4] / 12)
        in_slow = t_slow0 <= t < t_slow1
        light = t >= t_board
        step = i % 16
        if in_slow:
            if step % 8 == 0: place(mus, k_, t, 0.5)
        else:
            if step % 4 == 0: place(mus, k_, t, 1.0 if not light else 0.7)
            if step % 8 == 4 and not light: place(mus, c_, t, 0.8)
            if step % 4 == 2: place(mus, hat(), t, 0.8)
            # bass on 8ths
            if step % 2 == 0:
                bs = lowpass_fft(saw(note / 2, beat / 2 * 0.95), 600) * _env(int(beat / 2 * 0.95 * SR), r=0.12)
                place(mus, bs, t, 0.55)
            # arp
            arp = [1, 1.5, 2, 1.5][step % 4] * note * 2
            if not light or step % 4 == 0: place(mus, pluck(arp, beat / 2), t, 0.22)
        t += beat / 4; i += 1
    # muffle slow-mo section
    a, b = int(t_slow0 * SR), int(t_slow1 * SR)
    if b > a: mus[a:b] = lowpass_fft(mus[a:b], 350) * 1.3
    return mus

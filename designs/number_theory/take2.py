import math
import numpy as np
import matplotlib.pyplot as plt


def prime_sieve(n: int) -> list[bool]:
    """Return a boolean list is_prime[0..n] using a simple sieve."""
    is_prime = [False, False] + [True] * (n - 1)
    for p in range(2, int(n**0.5) + 1):
        if is_prime[p]:
            is_prime[p * p : n + 1 : p] = [False] * (((n - p * p) // p) + 1)
    return is_prime


def goldbach_counts(limit_even: int) -> tuple[list[int], list[int]]:
    """Return (evens, counts) for 4 ≤ even ≤ limit_even."""
    is_prime = prime_sieve(limit_even)
    primes   = [i for i, flag in enumerate(is_prime) if flag]

    evens, counts = [], []
    for even in range(4, limit_even + 1, 2):
        c = 0
        for p in primes:
            if p > even // 2:
                break
            if is_prime[even - p]:
                c += 1
        evens.append(even)
        counts.append(c)
    return evens, counts


def moving_std(values: list[int], window: int = 10) -> list[float | None]:
    """Centered moving σ (population); None where the window doesn’t fit."""
    half = window // 2
    n    = len(values)
    out  = [None] * n
    for i in range(half, n - half):
        out[i] = float(np.std(values[i - half : i + half]))
    return out


def moving_avg(values: list[float | None], window: int = 10) -> list[float | None]:
    """Centered moving mean; skips windows containing None."""
    half = window // 2
    n    = len(values)
    out  = [None] * n
    for i in range(half, n - half):
        window_vals = values[i - half : i + half]
        if None in window_vals:
            continue
        out[i] = float(sum(window_vals) / window)
    return out


# ---------- OPTIONAL: turn the normalised series into sound ---------
# Install once:  pip install sounddevice soundfile
import numpy as np
import sounddevice as sd
#import soundfile as sf     # only needed if you want to write a .wav

def series_to_audio(values,
                    dur_per_step=0.012,          # seconds per data point
                    f_lo=220.0, f_hi=880.0,     # frequency range (A3 – A5)
                    sr=44_100):
    """Map a 1-D numeric sequence to a sine-wave sweep and return samples."""
    vals = np.asarray(values, dtype=float)
    # normalise 0‒1, protect against flat series
    vals = (vals - vals.min()) / max(np.ptp(vals), 1e-9)
    freqs = f_lo + vals * (f_hi - f_lo)

    samples = []
    t = np.linspace(0, dur_per_step, int(sr*dur_per_step), endpoint=False)
    for f in freqs:
        samples.append(np.sin(2*np.pi*f*t))
    return np.concatenate(samples)


def main() -> None:
    try:
        limit_even = int(input("Largest even number to test (≥ 4): "))
    except ValueError:
        print("❌  Please enter an integer.")
        return

    if limit_even < 4 or limit_even % 2:
        print("❌  Value must be an even integer ≥ 4.")
        return

    # ------------------------------------------------------------------
    # 1. Goldbach counts
    evens, counts = goldbach_counts(limit_even)

    # 2. Exponential fit  y = A·e^{B x}
    x = np.array(evens, dtype=float)
    y = np.array(counts, dtype=float)
    mask   = y > 0
    B, lnA = np.polyfit(x[mask], np.log(y[mask]), 1)
    A      = np.exp(lnA)
    fit_y  = A * np.exp(B * x)

    # 3. Moving σ, then σ-normalisation and second-level normalisation
    sigma   = moving_std(counts, window=10)
    ratio1  = [c/s if s else None for c, s in zip(counts, sigma)]
    mu      = moving_avg(ratio1, window=10)
    ratio2  = [r/m if r is not None and m is not None else None
               for r, m in zip(ratio1, mu)]

    # ------------------------------------------------------------------
    #  Primary plot: counts + exponential fit
    plt.figure(figsize=(10, 6))
    plt.plot(evens, counts, marker="o", linestyle="", label="Goldbach counts")
    plt.plot(evens, fit_y, linewidth=2,
             label=fr"Exponential fit: $y={A:.3f}\,e^{{{B:.3e}x}}$")
    plt.title(f"Goldbach partitions for even numbers 4 – {limit_even}")
    plt.xlabel("Even number")
    plt.ylabel("Number of prime pairs")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # ------------------------------------------------------------------
    #  Second plot: σ- and μ-normalised series
    ev2   = [e for e, r in zip(evens, ratio2) if r is not None]
    norm2 = [r for r in ratio2 if r is not None]

    if ev2:
        plt.figure(figsize=(10, 4))
        plt.plot(ev2, norm2, linestyle="-",
                 label=r"$\dfrac{(\,\text{count}/\sigma\,)}{\langle\,\text{count}/\sigma\,\rangle_{10}}$", linewidth = 0.5)
        plt.title("Double-normalised Goldbach counts (window = 10)")
        plt.xlabel("Even number")
        plt.ylabel("Normalised value")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
    else:
        print("⚠️  No points where both σ and μ windows fit.")

    plt.show()

        # Keep only the points where ratio2 is defined
    audio_series  = [r for r in ratio2 if r is not None]

    if audio_series:
        audio = series_to_audio(audio_series)
        #sd.play(audio, samplerate=44_100) #uncomment if you want to hear the audio
        sd.wait()                      # block until playback finishes

        # If you’d like a .wav file as well:
        # sf.write("goldbach_melody.wav", audio, 44_100)
    else:
        print("No valid data to sonify.")
    # --------------------------------------------------------------------
if __name__ == "__main__":
    main()


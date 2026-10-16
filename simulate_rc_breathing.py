import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def simulate_hbl22():
    # Calibrated to empirical multimeter measurements from lab report
    Vcc = 5.02            # Measured supply voltage (V)
    C1 = 47e-6            # 47 uF electrolytic capacitor (Farads)
    R_fixed = 10e3        # 10 kOhm fixed series resistance
    VR1_max = 50e3        # 50 kOhm potentiometer
    
    V_th_low = 1.70       # Lower Schmitt trigger threshold (V)
    V_th_high = 3.30      # Upper Schmitt trigger threshold (V)
    
    # Empirical current range measured across main 5.02V input: 45 mA to 65 mA
    I_min_mA = 45.0       # Minimum current at V_th_low (mA)
    I_max_mA = 65.0       # Peak current at V_th_high (mA)

    # 10 seconds simulation window, 1 ms resolution
    t = np.linspace(0, 10.0, 10000)
    dt = t[1] - t[0]

    settings = [
        (0.10, "10% (Fast Breathing)"),
        (0.50, "50% (Medium Breathing)"),
        (1.00, "100% (Slow Breathing)")
    ]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

    for ratio, label in settings:
        R_eff = R_fixed + (ratio * VR1_max)
        tau = R_eff * C1  # Time constant tau = R * C (seconds)

        Vc = np.zeros_like(t)
        Vc[0] = V_th_low
        charging = True

        for i in range(1, len(t)):
            if charging:
                Vc[i] = Vc[i-1] + ((Vcc - Vc[i-1]) / tau) * dt
                if Vc[i] >= V_th_high:
                    charging = False
            else:
                Vc[i] = Vc[i-1] + ((0.0 - Vc[i-1]) / tau) * dt
                if Vc[i] <= V_th_low:
                    charging = True

        # Map capacitor voltage Vc in [1.7V, 3.3V] to measured current [45 mA, 65 mA]
        norm_v = np.clip((Vc - V_th_low) / (V_th_high - V_th_low), 0.0, 1.0)
        I_total_mA = I_min_mA + norm_v * (I_max_mA - I_min_mA)

        ax1.plot(t, Vc, label=f"{label} (τ = {tau:.2f}s)")
        ax2.plot(t, I_total_mA, label=label)

    ax1.set_title("Capacitor Voltage $V_C(t)$ (Supply $V_{CC} = 5.02\\,\\mathrm{V}$)")
    ax1.set_ylabel("Voltage (V)")
    ax1.axhline(V_th_high, color='gray', linestyle='--', alpha=0.5, label="Upper Threshold (3.3V)")
    ax1.axhline(V_th_low, color='gray', linestyle=':', alpha=0.5, label="Lower Threshold (1.7V)")
    ax1.grid(True, alpha=0.4)
    ax1.legend(loc="upper right", fontsize=8)

    ax2.set_title("Total Circuit Current $I_{total}(t)$ (Empirical Range: 45–65 mA, $P \\approx 0.25\\,\\mathrm{W}$)")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Current (mA)")
    ax2.set_ylim(40, 70)
    ax2.grid(True, alpha=0.4)
    ax2.legend(loc="upper right", fontsize=8)

    plt.tight_layout()
    plt.savefig("breathing_waveforms.png", dpi=300)
    print("Simulation complete. Plot saved to breathing_waveforms.png")

if __name__ == "__main__":
    simulate_hbl22()
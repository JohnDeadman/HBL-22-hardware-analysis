import numpy as np
import matplotlib.pyplot as plt

# --- Circuit Parameters ---
VCC = 5.0                # Supply voltage (V)
V_ref = VCC * 0.5        # Reference voltage at non-inverting input (V)
C1 = 47e-6               # Timing capacitor (F)
VR1_max = 50e3           # Maximum potentiometer resistance (Ohms)
R_fixed = 10e3           # Fixed resistance in series with VR1 (Ohms)

# Schmitt trigger parameters
R3 = 100e3
R4 = 47e3
# The positive feedback gives switching thresholds.
# Simplifying LM358 output swing to 0V and VCC-1.5V as mentioned in README
V_OH = VCC - 1.5
V_OL = 0.0

# LED array and transistor parameters
R5 = 22.0                # LED current limiting resistor (Ohms)
V_LED = 2.0              # Forward voltage of Red LED (V) roughly
beta = 200               # S8050 typical beta
V_BE = 0.7               # Base-emitter drop (V)

# Calculate thresholds V_TH and V_TL
# Thresholds are formed by V_ref and feedback from Output
# Assuming op-amp output feeds to non-inverting input? Wait, README says:
# "One half of the LM358 acts as a Schmitt trigger (comparator with positive feedback via R3=100k and R4=47k)."
# Let's simplify the thresholds based on the time constant limits mentioned:
# Fast pulse ~ 0.47s with tau = 10k * 47uF = 0.47s
# V_C swings between two thresholds. Let's use standard Schmitt trigger approx
# Let V_TH = 3.3V, V_TL = 1.6V for typical triangle wave
V_TH = V_ref + (V_OH - V_ref) * (R4 / (R3 + R4))
V_TL = V_ref + (V_OL - V_ref) * (R4 / (R3 + R4))

# --- Simulation Setup ---
t_total = 10.0           # Total simulation time (s)
dt = 0.001               # Time step (s)
time = np.arange(0, t_total, dt)

# VR1 Settings to simulate
vr1_settings = [0.10, 0.50, 1.00] # 10%, 50%, 100%
labels = ['10% (Fast Breathing)', '50% (Medium Breathing)', '100% (Slow Breathing)']

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

for vr1_pct, label in zip(vr1_settings, labels):
    R_eff = R_fixed + vr1_pct * VR1_max

    # Initialize arrays
    V_C = np.zeros_like(time)
    I_LED = np.zeros_like(time)
    V_out = V_OH # Schmitt trigger initial state

    vc = V_TL # Start at lower threshold

    for i, t in enumerate(time):
        V_C[i] = vc

        # Determine Schmitt trigger output state
        if V_out == V_OH and vc >= V_TH:
            V_out = V_OL
        elif V_out == V_OL and vc <= V_TL:
            V_out = V_OH

        # RC Charge/Discharge Step
        # The capacitor charges toward V_out through R_eff
        dVc = (V_out - vc) / R_eff * dt
        vc += dVc

        # Calculate LED Current
        # The op-amp integrator output (V_C) drives the S8050 base
        # Emitter follower config: V_E = V_C - V_BE
        V_E = max(0, vc - V_BE)
        # Current through LEDs = (V_E - V_LED) / R5 if V_E > V_LED
        i_led = max(0, (V_E - V_LED) / R5)
        # Assuming we just map V_C to LED current directly as breathing effect:
        # S8050 current buffer allows V_C to drive the LEDs with current proportional to voltage
        # Since I_LED can be roughly modeled as (V_C - V_BE - V_LED) / R5
        # Let's use a simpler exponential relationship or just max(0, (vc - 1.5)/R5) to show the breathing
        I_LED[i] = max(0, (vc - 1.8) / R5) * 1000 # in mA

    ax1.plot(time, V_C, label=label)
    ax2.plot(time, I_LED, label=label)

ax1.set_title('Capacitor Voltage $V_C(t)$')
ax1.set_ylabel('Voltage (V)')
ax1.grid(True)
ax1.legend()

ax2.set_title('Total LED Array Current $I_{LED}(t)$')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Current (mA)')
ax2.grid(True)

plt.tight_layout()
plt.savefig('breathing_waveforms.png', dpi=300)
print("Simulation complete. Plot saved to breathing_waveforms.png")

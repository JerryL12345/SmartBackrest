import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import warnings

# ==========================================
# 0. Web App Setup
# ==========================================
st.set_page_config(page_title="Lumbar Cushion Optimizer", page_icon="🪑", layout="wide")
warnings.filterwarnings('ignore')

# Note: Removed Chinese font settings. English text will render perfectly on all servers.

# ==========================================
# 1. Title & Sidebar UI
# ==========================================
st.title("🪑 Dynamic Lumbar Cushion Parameter Explorer")
st.markdown("Based on a **Decoupled Unified Biomechanical Model** (Incorporating Real Non-linear Compression Mapping)")

st.sidebar.header("🕹️ Posture Input")
current_theta = st.sidebar.slider(
    "Adjust slider: Seat/Trunk Tilt Angle θ (°)", 
    min_value=70.0, max_value=110.0, value=70.0, step=1.0
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**🎯 Physics Correction Notes:**
* "Geometric Gap" and "Material Compression" are now strictly decoupled.
* Authentic stiffness requirements are softer than preliminary linear models.
* Safely retains residual thickness for structural back support.
""")

# ==========================================
# 2. Core Mathematics & Physics Engine
# ==========================================
G, h_pad, F_pad_max = 314.5, 0.11, 60.0
alpha_target = np.radians(30.0)
k_range = np.linspace(300, 3500, 200) 

# Risk angle without support
alpha_flat_deg = max(0, 15.0 - 0.5 * abs(90.0 - current_theta))
alpha_flat = np.radians(alpha_flat_deg)

# --- The Authentic Physical Logic ---
# Step 1: Geometric gap to restore the healthy 30° curve
target_gap = h_pad * np.sin(alpha_target - alpha_flat)

# Step 2: Actual required compression = Initial thickness - Residual thickness needed
required_compression = h_pad - target_gap

# Step 3: Derive true equivalent stiffness k (Hooke's Law: F = kx)
k_val = F_pad_max / required_compression

# Step 4: Calculate actual sacral angle variation across the stiffness spectrum
actual_compression = np.minimum(F_pad_max / k_range, h_pad)
actual_gap_filled = h_pad - actual_compression # True residual thickness
alpha_actual = alpha_flat + np.arcsin(actual_gap_filled / h_pad)

# Angle Deviation = Target Angle (30°) - Actual Angle
angle_dev_raw = np.degrees(alpha_target - alpha_actual)
angle_dev_abs = np.abs(angle_dev_raw)

# ==========================================
# 3. Main Dashboard (Metrics)
# ==========================================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Risk Sacral Angle (Unsupported)", value=f"{alpha_flat_deg:.1f}°")
with col2:
    st.metric(label="Target Lumbar Gap", value=f"{target_gap*100:.2f} cm")
with col3:
    st.metric(label="Actual Cushion Compression", value=f"{required_compression*100:.2f} cm")
with col4:
    st.metric(label="★ Recommended Stiffness (k)", value=f"{k_val:.0f} N/m", delta="Updates dynamically")

st.markdown("---")

# ==========================================
# 4. Advanced Physical Funnel Chart
# ==========================================
fig, ax = plt.subplots(figsize=(14, 7))

# Dynamic zones based on optimal k
zone_left, zone_right = k_val * 0.70, k_val * 1.50
ax.axvspan(300, zone_left, alpha=0.15, color='#ffcccc')    
ax.axvspan(zone_left, zone_right, alpha=0.15, color='#90EE90')   
ax.axvspan(zone_right, 3500, alpha=0.15, color='#ffffcc')   

text_x_soft = (300 + zone_left) / 2
text_x_opt = (zone_left + zone_right) / 2
text_x_hard = zone_right + (3500 - zone_right) * 0.35 

# Masking for physical signs
mask_soft = angle_dev_raw > 0  # Too soft: Actual angle < 30, Positive deviation
mask_hard = angle_dev_raw <= 0 # Too hard: Actual angle > 30, Negative deviation
idx_opt = np.argmin(angle_dev_abs)
mask_soft[idx_opt] = True
mask_hard[idx_opt] = True

# Plotting the V-curve and real physical extension
ax.plot(k_range[mask_soft], angle_dev_raw[mask_soft], color='#8B008B', linewidth=3.5, linestyle='-', label='Posterior Tilt')
ax.plot(k_range[mask_hard], angle_dev_abs[mask_hard], color='#8B008B', linewidth=3.5, linestyle='--', label='Anterior Tilt')
ax.plot(k_range[mask_hard], angle_dev_raw[mask_hard], color='#8B008B', linewidth=3.5, linestyle='-', alpha=0.6)

ax.set_ylim(-45, 45) 
ax.set_xlim(300, 3500)

bbox_style = dict(boxstyle='round,pad=0.6', alpha=0.9, edgecolor='gray')
ax.text(text_x_soft, 38, '[Too Soft]', fontsize=12, ha='center', va='center', bbox=dict(**bbox_style, facecolor='#ffe6e6'))
ax.text(text_x_opt, 38, '[Golden Sweet Spot]', fontsize=13, ha='center', va='center', fontweight='bold', bbox=dict(**bbox_style, facecolor='#ccffcc'))
ax.text(text_x_hard, 38, '[Too Hard]', fontsize=12, ha='center', va='center', bbox=dict(**bbox_style, facecolor='#ffffe6'))

ax.legend(loc='lower left', fontsize=12, framealpha=0.95)

# Mark the optimal point
ax.plot(k_val, angle_dev_abs[idx_opt], '*', color='#FF1493', markersize=40, zorder=10)

ax.set_xlabel('Equivalent Cushion Stiffness k (N/m)', fontsize=14, fontweight='bold')
ax.set_ylabel('Absolute Sacral Angle Deviation (|Δα|°)', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.4, linestyle='--', linewidth=1)

st.pyplot(fig)

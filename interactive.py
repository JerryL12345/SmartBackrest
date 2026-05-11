import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import warnings

# ==========================================
# 0. Web app setup
# ==========================================
st.set_page_config(page_title="Lumbar Cushion Simulation", page_icon="🪑", layout="wide")
warnings.filterwarnings('ignore')

# Font fallback settings
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# ==========================================
# 1. Title and sidebar UI
# ==========================================
st.title("🪑 Dynamic Lumbar Cushion Parameter Explorer")
st.markdown("Based on a **two-step unified biomechanics model** (anatomy + statics + material engineering)")

# Sidebar controls
st.sidebar.header("🕹️ Posture Input")
current_theta = st.sidebar.slider(
    "Adjust slider: seat/trunk tilt angle θ (°)", 
    min_value=70.0, max_value=110.0, value=70.0, step=1.0
)

# Sidebar notes
st.sidebar.markdown("---")
st.sidebar.markdown("""
**Parameter Guide:**
* **70°**: severe forward-leaning desk posture
* **90°**: standard upright sitting
* **110°**: reclined posture
""")

# ==========================================
# 2. Core mathematics and physical derivation
# ==========================================
G, h_pad, F_pad_max = 314.5, 0.11, 60.0
alpha_target = np.radians(30.0)
k_range = np.linspace(400, 4000, 200)

alpha_flat_deg = max(0, 15.0 - 0.5 * abs(90.0 - current_theta))
alpha_flat = np.radians(alpha_flat_deg)

delta_x = h_pad * np.sin(alpha_target - alpha_flat)
k_val = F_pad_max / delta_x

delta_x_actual = np.minimum(F_pad_max / k_range, h_pad)
alpha_actual = alpha_flat + np.arcsin(delta_x_actual / h_pad)
angle_dev_raw = np.degrees(alpha_target - alpha_actual)
angle_dev_abs = np.abs(angle_dev_raw)

# ==========================================
# 3. Main layout
# ==========================================
# Top KPI cards
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Risk sacral angle (no support)", value=f"{alpha_flat_deg:.1f}°")
with col2:
    st.metric(label="Required lumbar gap fill", value=f"{delta_x*100:.2f} cm")
with col3:
    st.metric(label="★ Recommended optimal stiffness k", value=f"{k_val:.0f} N/m", delta="Updates with sidebar input")

st.markdown("---")

# ==========================================
# 4. Dynamic analysis chart
# ==========================================
fig, ax = plt.subplots(figsize=(14, 7))

zone_left, zone_right = k_val * 0.75, k_val * 1.40
ax.axvspan(400, zone_left, alpha=0.15, color='#ffcccc')    
ax.axvspan(zone_left, zone_right, alpha=0.15, color='#90EE90')   
ax.axvspan(zone_right, 4000, alpha=0.15, color='#ffffcc')   

text_x_soft = (400 + zone_left) / 2
text_x_opt = (zone_left + zone_right) / 2
text_x_hard = zone_right + (4000 - zone_right) * 0.35 

mask_soft = angle_dev_raw < 0  
mask_hard = angle_dev_raw >= 0 
idx_opt = np.argmin(angle_dev_abs)
mask_soft[idx_opt] = True
mask_hard[idx_opt] = True

ax.plot(k_range[mask_soft], angle_dev_abs[mask_soft], color='#8B008B', linewidth=3.5, linestyle='--', label='Negative folded: support collapse / posterior pelvic tilt')
ax.plot(k_range[mask_hard], angle_dev_abs[mask_hard], color='#8B008B', linewidth=3.5, linestyle='-', label='Positive: over-pushing / anterior pelvic tilt')
ax.plot(k_range[mask_soft], angle_dev_raw[mask_soft], color='#8B008B', linewidth=3.5, linestyle='-')

ax.set_ylim(-75, 85) 
ax.set_xlim(400, 4000)

bbox_style = dict(boxstyle='round,pad=0.6', alpha=0.9, edgecolor='gray')
ax.text(text_x_soft, 75, '[Too Soft]\nSupport collapse, high posterior shear', fontsize=12, ha='center', va='center', bbox=dict(**bbox_style, facecolor='#ffe6e6'))
ax.text(text_x_opt, 75, '[Golden Comfort Zone]\nMaintain healthy 30° angle', fontsize=13, ha='center', va='center', fontweight='bold', bbox=dict(**bbox_style, facecolor='#ccffcc'))
ax.text(text_x_hard, 75, '[Too Hard]\nExcessive push-back, reverse stress', fontsize=12, ha='center', va='center', bbox=dict(**bbox_style, facecolor='#ffffe6'))

ax.legend(loc='upper right', fontsize=12, framealpha=0.95)

# Mark optimal point
ax.plot(k_val, angle_dev_abs[idx_opt], '*', color='#FF1493', markersize=40, zorder=10)

ax.set_xlabel('Equivalent cushion stiffness k (N/m)', fontsize=14, fontweight='bold')
ax.set_ylabel('Sacral angle deviation (Δα°)', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.4, linestyle='--', linewidth=1)

# Render chart in app
st.pyplot(fig)
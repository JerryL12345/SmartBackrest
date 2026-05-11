import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import warnings

# ==========================================
# 0. 网页基础设置
# ==========================================
st.set_page_config(page_title="护腰靠垫推演系统", page_icon="🪑", layout="wide")
warnings.filterwarnings('ignore')

# 解决 Mac/Windows 本地中文字体问题
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# ==========================================
# 1. 网页标题与侧边栏 UI
# ==========================================
st.title("🪑 护腰靠垫参数动态推演系统")
st.markdown("基于 **解耦统一的两步走生物力学模型** (解剖学 + 静力学 + 材料学)")

# 将交互滑块移入漂亮的侧边栏
st.sidebar.header("🕹️ 用户姿势输入")
current_theta = st.sidebar.slider(
    "请拖动滑块：座椅/躯干倾斜角 θ (°)", 
    min_value=70.0, max_value=110.0, value=70.0, step=1.0
)

# 侧边栏说明
st.sidebar.markdown("---")
st.sidebar.markdown("""
**参数说明：**
* **70°**: 严重前倾伏案
* **90°**: 标准端坐
* **110°**: 后仰/葛优躺
""")

# ==========================================
# 2. 核心数学与物理推导
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
# 3. 网页主界面展示 (分列排版)
# ==========================================
# 顶部的三大核心数据指标看板 (KPI 风格)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="无支撑时危险骶骨角", value=f"{alpha_flat_deg:.1f}°")
with col2:
    st.metric(label="需填补的腰窝空隙", value=f"{delta_x*100:.2f} cm")
with col3:
    st.metric(label="★ 推荐最佳弹性系数 k", value=f"{k_val:.0f} N/m", delta="点击侧边栏动态更新")

st.markdown("---")

# ==========================================
# 4. 生成动态分析图表
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

ax.plot(k_range[mask_soft], angle_dev_abs[mask_soft], color='#8B008B', linewidth=3.5, linestyle='--', label='负值翻折：支撑塌陷/骨盆后倾')
ax.plot(k_range[mask_hard], angle_dev_abs[mask_hard], color='#8B008B', linewidth=3.5, linestyle='-', label='正值：过度顶推/骨盆前倾')
ax.plot(k_range[mask_soft], angle_dev_raw[mask_soft], color='#8B008B', linewidth=3.5, linestyle='-')

ax.set_ylim(-75, 85) 
ax.set_xlim(400, 4000)

bbox_style = dict(boxstyle='round,pad=0.6', alpha=0.9, edgecolor='gray')
ax.text(text_x_soft, 75, '【材料过软】\n支撑塌陷，后倾剪切力大', fontsize=12, ha='center', va='center', bbox=dict(**bbox_style, facecolor='#ffe6e6'))
ax.text(text_x_opt, 75, '【黄金舒适区】\n维持 30° 健康角', fontsize=13, ha='center', va='center', fontweight='bold', bbox=dict(**bbox_style, facecolor='#ccffcc'))
ax.text(text_x_hard, 75, '【材料过硬】\n过度顶推，产生反向应力', fontsize=12, ha='center', va='center', bbox=dict(**bbox_style, facecolor='#ffffe6'))

ax.legend(loc='upper right', fontsize=12, framealpha=0.95)

# 标注最优点
ax.plot(k_val, angle_dev_abs[idx_opt], '*', color='#FF1493', markersize=40, zorder=10)

ax.set_xlabel('靠垫材料等效弹性系数 k (N/m)', fontsize=14, fontweight='bold')
ax.set_ylabel('骶骨角度偏差值 (Δα°)', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.4, linestyle='--', linewidth=1)

# 在网页上渲染这张图
st.pyplot(fig)
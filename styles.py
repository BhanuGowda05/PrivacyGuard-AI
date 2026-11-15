"""
styles.py - Custom styling and CSS for PrivacyGuard
Navy Blue (#0A192F, #112240), Crisp White (#FFFFFF, #E6F1FF), and Vibrant Teal (#64FFDA, #00E5FF, #0D9488)
"""

def get_custom_css():
    return """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

    /* Global Base */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main container styling */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1200px;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0B1528 !important;
        border-right: 1px solid rgba(0, 229, 255, 0.15);
    }

    section[data-testid="stSidebar"] div[class*="block-container"] {
        padding-top: 2rem;
    }

    /* Sidebar Navigation Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease-in-out;
    }

    /* Top Navigation bar / Banner */
    .cyber-header {
        background: linear-gradient(135deg, #0A192F 0%, #172A45 50%, #0B192E 100%);
        border: 1px solid rgba(0, 229, 255, 0.25);
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.8rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    .cyber-header-title {
        color: #FFFFFF;
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .cyber-header-subtitle {
        color: #8892B0;
        font-size: 0.95rem;
        margin-top: 0.3rem;
        margin-bottom: 0;
    }

    /* Status Pill */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(0, 229, 255, 0.1);
        border: 1px solid #00E5FF;
        color: #00E5FF;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        background-color: #00E5FF;
        border-radius: 50%;
        box-shadow: 0 0 10px #00E5FF;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(1.1); }
        100% { opacity: 1; transform: scale(1); }
    }

    /* Stat Metric Cards */
    .stat-card {
        background: #112240;
        border: 1px solid rgba(136, 146, 176, 0.2);
        border-top: 3px solid #00E5FF;
        border-radius: 10px;
        padding: 1.25rem 1.2rem;
        box-shadow: 0 4px 20px rgba(2, 12, 27, 0.5);
        transition: transform 0.2s ease, border-color 0.2s ease;
        margin-bottom: 1rem;
    }

    .stat-card:hover {
        transform: translateY(-3px);
        border-color: #00E5FF;
    }

    .stat-label {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #8892B0;
        margin-bottom: 0.4rem;
    }

    .stat-value {
        font-size: 2.1rem;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.1;
        font-family: 'JetBrains Mono', monospace;
    }

    .stat-sub {
        font-size: 0.8rem;
        color: #64FFDA;
        margin-top: 0.4rem;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* Action Cards */
    .action-card {
        background: linear-gradient(145deg, #112240 0%, #1A365D 100%);
        border: 1px solid rgba(0, 229, 255, 0.3);
        border-radius: 12px;
        padding: 1.8rem;
        box-shadow: 0 8px 24px rgba(2, 12, 27, 0.4);
        margin-bottom: 1.2rem;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .action-card-icon {
        font-size: 2.2rem;
        margin-bottom: 1rem;
        display: inline-block;
        background: rgba(0, 229, 255, 0.15);
        border: 1px solid rgba(0, 229, 255, 0.3);
        width: 54px;
        height: 54px;
        line-height: 54px;
        text-align: center;
        border-radius: 12px;
    }

    .action-card-title {
        color: #FFFFFF;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .action-card-desc {
        color: #A8B2D1;
        font-size: 0.92rem;
        line-height: 1.5;
        margin-bottom: 1.5rem;
        flex-grow: 1;
    }

    /* Workflow Cards */
    .workflow-container {
        background: #0D1D38;
        border: 1px solid rgba(136, 146, 176, 0.25);
        border-radius: 12px;
        padding: 1.6rem;
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }

    .workflow-step {
        background: #112240;
        border-left: 3px solid #64FFDA;
        border-radius: 6px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.75rem;
    }

    .workflow-step-num {
        color: #64FFDA;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 0.2rem;
    }

    .workflow-step-title {
        color: #FFFFFF;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }

    .workflow-step-desc {
        color: #8892B0;
        font-size: 0.88rem;
        line-height: 1.4;
        margin: 0;
    }

    /* Activity Table Card */
    .activity-container {
        background: #0B192E;
        border: 1px solid rgba(136, 146, 176, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1.5rem;
    }

    .sample-tag {
        background: rgba(255, 171, 0, 0.15);
        border: 1px solid #FFAB00;
        color: #FFC043;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 12px;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }

    /* Staged Data & Preview Containers */
    .preview-box {
        background: #081220;
        border: 1px solid rgba(0, 229, 255, 0.3);
        border-radius: 8px;
        padding: 1.2rem;
        max-height: 320px;
        overflow-y: auto;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #E6F1FF;
        line-height: 1.6;
        white-space: pre-wrap;
        word-break: break-word;
    }

    .badge-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(0, 229, 255, 0.12);
        border: 1px solid rgba(0, 229, 255, 0.3);
        color: #00E5FF;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .stage-notice {
        background: linear-gradient(90deg, rgba(0, 229, 255, 0.1) 0%, rgba(100, 255, 218, 0.05) 100%);
        border: 1px solid #00E5FF;
        border-left: 4px solid #00E5FF;
        border-radius: 8px;
        padding: 1rem 1.4rem;
        margin-bottom: 1.5rem;
    }

    /* Step 3: Detection Badges & Cards */
    .risk-banner {
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 12px;
    }

    .risk-critical {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid #EF4444;
        border-left: 5px solid #EF4444;
    }

    .risk-high {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid #F59E0B;
        border-left: 5px solid #F59E0B;
    }

    .risk-safe {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid #10B981;
        border-left: 5px solid #10B981;
    }

    .category-box {
        background: #112240;
        border: 1px solid rgba(136, 146, 176, 0.25);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }

    /* Step 5 & 6: Masking and Comparison Containers */
    .protected-box {
        background: #061A24;
        border: 1px solid #10B981;
        border-left: 4px solid #10B981;
        border-radius: 8px;
        padding: 1.2rem;
        max-height: 380px;
        overflow-y: auto;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #A7F3D0;
        line-height: 1.65;
        white-space: pre-wrap;
        word-break: break-word;
    }

    .original-box {
        background: #1A0D15;
        border: 1px solid #F43F5E;
        border-left: 4px solid #F43F5E;
        border-radius: 8px;
        padding: 1.2rem;
        max-height: 380px;
        overflow-y: auto;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #FECDD3;
        line-height: 1.65;
        white-space: pre-wrap;
        word-break: break-word;
    }

    .download-card {
        background: linear-gradient(135deg, #112240 0%, #0F2A4A 100%);
        border: 1px solid rgba(0, 229, 255, 0.3);
        border-radius: 10px;
        padding: 1.25rem;
        text-align: center;
        margin-bottom: 1rem;
    }

    /* Side-by-Side Comparison Containers (Step 5 & 6) */
    .compare-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
    }

    .compare-card {
        background: #081220;
        border: 1px solid rgba(136, 146, 176, 0.25);
        border-radius: 8px;
        padding: 1.2rem;
    }

    .compare-card-protected {
        border-color: rgba(100, 255, 218, 0.4);
        box-shadow: 0 0 15px rgba(100, 255, 218, 0.08);
    }

    .download-card {
        background: linear-gradient(145deg, #112240 0%, #172A45 100%);
        border: 1px solid rgba(0, 229, 255, 0.3);
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        transition: transform 0.2s ease;
    }

    @media (max-width: 768px) {
        .compare-container {
            grid-template-columns: 1fr;
        }
    }

    .explainer-box {
        background: #0B192E;
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 10px;
        padding: 1.4rem;
        margin-top: 1.5rem;
    }

    /* Navigation item styling */
    .nav-btn-active {
        background-color: #172A45 !important;
        border-left: 3px solid #00E5FF !important;
        color: #00E5FF !important;
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .cyber-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
        }
        .stat-value {
            font-size: 1.7rem;
        }
    }
    </style>
    """

def get_logo_html(size=44):
    """Returns SVG logo combining Shield and Lock with teal and navy gradient."""
    return f"""
    <div style="display: flex; align-items: center; gap: 12px;">
        <svg width="{size}" height="{size}" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="shieldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#00E5FF" />
                    <stop offset="60%" stop-color="#0077B6" />
                    <stop offset="100%" stop-color="#03045E" />
                </linearGradient>
                <linearGradient id="lockGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#FFFFFF" />
                    <stop offset="100%" stop-color="#64FFDA" />
                </linearGradient>
                <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="3" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
            </defs>
            <!-- Shield Path -->
            <path d="M50 8 L85 24 V50 C85 71.5 69.5 89 50 94 C30.5 89 15 71.5 15 50 V24 L50 8 Z" 
                  fill="url(#shieldGrad)" stroke="#00E5FF" stroke-width="2.5" filter="url(#glow)"/>
            <!-- Inner Shield Accent -->
            <path d="M50 16 L78 29 V50 C78 67 65.5 81.5 50 86 C34.5 81.5 22 67 22 50 V29 L50 16 Z" 
                  fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="1.5"/>
            <!-- Lock Shackle -->
            <path d="M42 42 V35 C42 30.5 45.5 27 50 27 C54.5 27 58 30.5 58 35 V42" 
                  fill="none" stroke="url(#lockGrad)" stroke-width="3.5" stroke-linecap="round"/>
            <!-- Lock Body -->
            <rect x="37" y="42" width="26" height="22" rx="4" 
                  fill="url(#lockGrad)" stroke="#0B1528" stroke-width="1.5"/>
            <!-- Keyhole -->
            <circle cx="50" cy="51" r="2.5" fill="#0B1528"/>
            <path d="M50 53.5 V58" stroke="#0B1528" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <div>
            <div style="font-size: 1.35rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.3px; line-height: 1.1;">
                Privacy<span style="color: #00E5FF;">Guard</span>
            </div>
            <div style="font-size: 0.72rem; color: #8892B0; letter-spacing: 0.6px; text-transform: uppercase; font-weight: 600;">
                AI Data Protection
            </div>
        </div>
    </div>
    """

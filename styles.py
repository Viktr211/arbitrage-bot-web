# styles.py
def get_styles():
    return """
    <style>
        .stApp { background: linear-gradient(180deg, #001a33 0%, #003087 100%); color: white; }
        .main-header { font-size: 32px; font-weight: bold; color: #00D4FF; text-align: center; margin-bottom: 10px; }
        .status-dot { display: inline-block; width: 16px; height: 16px; border-radius: 50%; margin-right: 8px; }
        .status-running { background-color: #00FF88; box-shadow: 0 0 12px #00FF88; animation: pulse 2s infinite; }
        .status-stopped { background-color: #FF4444; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
        .stButton>button { border-radius: 30px; height: 42px; font-weight: bold; }
        .token-card { background: rgba(0,100,200,0.25); border-radius: 12px; padding: 12px; margin: 6px 0; text-align: center; }
    </style>
    """

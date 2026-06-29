"""
╔═══════════════════════════════════════════════════════════════╗
║                    JOTA TRADES DASHBOARD                      ║
║              Trading Bot Performance Analytics                 ║
╚═══════════════════════════════════════════════════════════════╝

Dashboard público que muestra el rendimiento del bot de trading.
Conecta con Google Sheets para datos en tiempo real.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import StringIO
from datetime import datetime
import os

# =============================================
# CONFIGURACIÓN
# =============================================

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def get_config(key: str, default: str = "") -> str:
    """Obtiene config de st.secrets (cloud) o env vars (local)"""
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except:
        return os.getenv(key, default)

SHEET_ID = get_config("GOOGLE_SHEET_ID", "")
SHEET_GID = get_config("GOOGLE_SHEET_GID", "0")
INITIAL_BALANCE = float(get_config("INITIAL_BALANCE", "10000"))

# Links de Telegram
TELEGRAM_PUBLICO = "https://t.me/+k-5GG4RJCE0zZWNh"
TELEGRAM_VIP = "https://t.me/JOTAtrades"

# Colores del tema JOTAtrades
COLORS = {
    "bg_dark": "#0a0a0c",
    "bg_card": "#0f0f12",
    "orange": "#f97316",
    "orange_light": "#fb923c",
    "green": "#22c55e",
    "red": "#ef4444",
    "gray": "#6b7280",
    "gray_dark": "#1f1f23",
    "white": "#ffffff",
}

# =============================================
# CONFIGURACIÓN DE PÁGINA
# =============================================

st.set_page_config(
    page_title="JOTAtrades | Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================================
# CSS PERSONALIZADO
# =============================================

st.markdown("""
<style>
    .stApp {
        background-color: #0a0a0c;
    }
    
    header[data-testid="stHeader"] {
        background-color: #0a0a0c;
        border-bottom: 1px solid #1f1f23;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #0f0f12;
        border-right: 1px solid #1f1f23;
    }
    
    div[data-testid="stMetric"] {
        background-color: #0f0f12;
        border: 1px solid #1f1f23;
        border-radius: 12px;
        padding: 16px;
    }
    
    div[data-testid="stMetric"] label {
        color: #6b7280 !important;
        font-size: 12px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }
    
    h1, h2, h3 {
        color: #ffffff !important;
    }
    
    p, span, label {
        color: #9ca3af;
    }
    
    .stDataFrame {
        border: 1px solid #1f1f23;
        border-radius: 12px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    hr {
        border-color: #1f1f23;
        margin: 24px 0;
    }
    
    /* Botones CTA */
    .cta-container {
        display: flex;
        justify-content: center;
        gap: 16px;
        flex-wrap: wrap;
        margin: 20px 0;
    }
    
    .cta-button {
        padding: 14px 28px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: 700;
        font-size: 15px;
        transition: all 0.2s ease;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    
    .cta-primary {
        background: linear-gradient(135deg, #f97316, #ea580c);
        color: white !important;
        box-shadow: 0 4px 15px rgba(249, 115, 22, 0.3);
    }
    
    .cta-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(249, 115, 22, 0.4);
    }
    
    .cta-secondary {
        background: #1f1f23;
        color: #f97316 !important;
        border: 2px solid #f97316;
    }
    
    .cta-secondary:hover {
        background: #f97316;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


# =============================================
# FUNCIONES DE DATOS
# =============================================

@st.cache_data(ttl=60)
def load_data_from_sheets(sheet_id: str, gid: str = "0") -> pd.DataFrame:
    """Carga datos desde Google Sheets público."""
    if not sheet_id:
        return pd.DataFrame()
    
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {str(e)}")
        return pd.DataFrame()


def process_trades(df: pd.DataFrame) -> pd.DataFrame:
    """
    Procesa los datos del bot.
    
    Columnas del sheet:
    Tyme | Symbol | TF | Preset | Side | Entry | TP 1 | SL | Estado | (vacío) | Status | % | Final | % | Msg ID
    
    Ejemplo:
    2026-06-28 12:00:45 | FET/USDT | 30m | FET-30m-V1 | SHORT | 0.1725 | 0.1680... | 0.1769... | Cerrada | | SL | -2.61% | 1933 | . |
    """
    if df.empty:
        return df
    
    # Debug: mostrar columnas originales
    # st.write("Columnas originales:", df.columns.tolist())
    
    # Limpiar nombres de columnas (espacios extra, etc)
    df.columns = df.columns.str.strip()
    
    # Buscar la columna de porcentaje (puede ser "%" o tener variaciones)
    pnl_col = None
    for col in df.columns:
        if col == '%' or col.strip() == '%':
            # Verificar si tiene datos de porcentaje
            sample = df[col].dropna().astype(str).head(5)
            if any('%' in str(v) or any(c.isdigit() for c in str(v)) for v in sample):
                pnl_col = col
                break
    
    # Renombrar columnas
    rename_map = {
        'Tyme': 'datetime',
        'Symbol': 'symbol',
        'TF': 'timeframe',
        'Preset': 'preset',
        'Side': 'side',
        'Entry': 'entry',
        'TP 1': 'tp',
        'SL': 'sl',
        'Estado': 'estado',
        'Status': 'status',
        'Final': 'final',
        'Msg ID': 'msg_id',
    }
    
    # Agregar mapeo de la columna % si la encontramos
    if pnl_col:
        rename_map[pnl_col] = 'pnl_pct'
    
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    
    # Si no encontramos pnl_pct, buscar columnas que contengan valores de porcentaje
    if 'pnl_pct' not in df.columns:
        for col in df.columns:
            if df[col].astype(str).str.contains('%').any():
                df['pnl_pct'] = df[col]
                break
    
    # Convertir datetime
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
        df['date'] = df['datetime'].dt.date
    
    # Convertir % a número (-2.61% -> -2.61)
    if 'pnl_pct' in df.columns:
        df['pnl_pct'] = (
            df['pnl_pct']
            .astype(str)
            .str.replace('%', '', regex=False)
            .str.replace(',', '.', regex=False)
            .str.strip()
        )
        df['pnl_pct'] = pd.to_numeric(df['pnl_pct'], errors='coerce')
    
    # Determinar WIN/LOSS basado en Status o pnl
    if 'status' in df.columns:
        df['is_win'] = df['status'].astype(str).str.upper().str.contains('TP|WIN|PROFIT|GANADO', na=False)
        df['is_loss'] = df['status'].astype(str).str.upper().str.contains('SL|LOSS|PERDIDO|STOP', na=False)
    elif 'pnl_pct' in df.columns:
        df['is_win'] = df['pnl_pct'] > 0
        df['is_loss'] = df['pnl_pct'] < 0
    
    # Convertir valores numéricos
    for col in ['entry', 'tp', 'sl', 'final']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
    
    # Filtrar solo trades cerrados
    if 'estado' in df.columns:
        df = df[df['estado'].astype(str).str.upper().str.contains('CERRAD|CLOSED|COMPLETE', na=False)]
    
    # Ordenar por fecha
    if 'datetime' in df.columns:
        df = df.sort_values('datetime', ascending=True)
    
    return df


def calculate_metrics(df: pd.DataFrame, initial_balance: float) -> dict:
    """Calcula todas las métricas de trading."""
    empty_metrics = {
        "total_trades": 0, "wins": 0, "losses": 0, "win_rate": 0,
        "profit_factor": 0, "total_pnl_pct": 0, "avg_win": 0, "avg_loss": 0,
        "max_drawdown": 0, "current_balance": initial_balance, "best_trade": 0,
        "worst_trade": 0, "avg_trade": 0, "consecutive_wins": 0, "consecutive_losses": 0,
    }
    
    if df.empty or 'pnl_pct' not in df.columns:
        return empty_metrics
    
    valid_trades = df[df['pnl_pct'].notna()].copy()
    if valid_trades.empty:
        return empty_metrics
    
    total_trades = len(valid_trades)
    wins = valid_trades[valid_trades['pnl_pct'] > 0]
    losses = valid_trades[valid_trades['pnl_pct'] < 0]
    
    win_count = len(wins)
    loss_count = len(losses)
    win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
    
    total_pnl_pct = valid_trades['pnl_pct'].sum()
    avg_win = wins['pnl_pct'].mean() if len(wins) > 0 else 0
    avg_loss = losses['pnl_pct'].mean() if len(losses) > 0 else 0
    
    gross_profit = wins['pnl_pct'].sum() if len(wins) > 0 else 0
    gross_loss = abs(losses['pnl_pct'].sum()) if len(losses) > 0 else 0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (999 if gross_profit > 0 else 0)
    
    # Balance y Drawdown
    cumulative_pnl = valid_trades['pnl_pct'].cumsum()
    balance_series = initial_balance * (1 + cumulative_pnl / 100)
    current_balance = balance_series.iloc[-1] if len(balance_series) > 0 else initial_balance
    
    rolling_max = balance_series.expanding().max()
    drawdown = (balance_series - rolling_max) / rolling_max * 100
    max_drawdown = drawdown.min() if len(drawdown) > 0 else 0
    
    best_trade = valid_trades['pnl_pct'].max()
    worst_trade = valid_trades['pnl_pct'].min()
    avg_trade = valid_trades['pnl_pct'].mean()
    
    # Rachas
    consecutive_wins = 0
    consecutive_losses = 0
    current_streak = 0
    last_was_win = None
    
    for pnl in valid_trades['pnl_pct']:
        is_win = pnl > 0
        if last_was_win is None or is_win == last_was_win:
            current_streak += 1
        else:
            current_streak = 1
        
        if is_win:
            consecutive_wins = max(consecutive_wins, current_streak)
        else:
            consecutive_losses = max(consecutive_losses, current_streak)
        
        last_was_win = is_win
    
    return {
        "total_trades": total_trades,
        "wins": win_count,
        "losses": loss_count,
        "win_rate": round(win_rate, 1),
        "profit_factor": round(profit_factor, 2),
        "total_pnl_pct": round(total_pnl_pct, 2),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "max_drawdown": round(max_drawdown, 2),
        "current_balance": round(current_balance, 2),
        "best_trade": round(best_trade, 2),
        "worst_trade": round(worst_trade, 2),
        "avg_trade": round(avg_trade, 2),
        "consecutive_wins": consecutive_wins,
        "consecutive_losses": consecutive_losses,
    }


# =============================================
# GRÁFICOS
# =============================================

def create_equity_curve(df: pd.DataFrame, initial_balance: float) -> go.Figure:
    """Gráfico de evolución del balance."""
    fig = go.Figure()
    
    if df.empty or 'pnl_pct' not in df.columns:
        return fig
    
    valid_trades = df[df['pnl_pct'].notna()].copy()
    if valid_trades.empty:
        return fig
    
    if 'datetime' in valid_trades.columns:
        valid_trades = valid_trades.sort_values('datetime')
    
    cumulative_pnl = valid_trades['pnl_pct'].cumsum()
    balance = initial_balance * (1 + cumulative_pnl / 100)
    
    x_data = valid_trades['datetime'].tolist() if 'datetime' in valid_trades.columns else list(range(len(valid_trades)))
    
    fig.add_trace(go.Scatter(
        x=x_data,
        y=balance,
        mode='lines',
        fill='tozeroy',
        line=dict(color=COLORS["orange"], width=2),
        fillcolor='rgba(249, 115, 22, 0.1)',
        name='Balance',
        hovertemplate='<b>%{x}</b><br>Balance: $%{y:,.2f}<extra></extra>'
    ))
    
    # Línea de balance inicial
    fig.add_hline(y=initial_balance, line_dash="dash", line_color=COLORS["gray"], 
                  annotation_text=f"Inicial: ${initial_balance:,.0f}")
    
    fig.update_layout(
        plot_bgcolor=COLORS["bg_card"],
        paper_bgcolor=COLORS["bg_card"],
        font=dict(color=COLORS["gray"]),
        xaxis=dict(showgrid=True, gridcolor=COLORS["gray_dark"], linecolor=COLORS["gray_dark"]),
        yaxis=dict(showgrid=True, gridcolor=COLORS["gray_dark"], linecolor=COLORS["gray_dark"], tickprefix="$"),
        margin=dict(l=0, r=0, t=10, b=0),
        height=300,
        showlegend=False,
    )
    
    return fig


def create_daily_pnl_chart(df: pd.DataFrame) -> go.Figure:
    """Gráfico de barras de P&L diario."""
    fig = go.Figure()
    
    if df.empty or 'pnl_pct' not in df.columns or 'date' not in df.columns:
        return fig
    
    daily_pnl = df.groupby('date')['pnl_pct'].sum().reset_index()
    daily_pnl.columns = ['date', 'pnl']
    
    colors = [COLORS["green"] if x >= 0 else COLORS["red"] for x in daily_pnl['pnl']]
    
    fig.add_trace(go.Bar(
        x=daily_pnl['date'],
        y=daily_pnl['pnl'],
        marker_color=colors,
        hovertemplate='<b>%{x}</b><br>P&L: %{y:+.2f}%<extra></extra>'
    ))
    
    fig.add_hline(y=0, line_dash="solid", line_color=COLORS["gray_dark"], line_width=1)
    
    fig.update_layout(
        plot_bgcolor=COLORS["bg_card"],
        paper_bgcolor=COLORS["bg_card"],
        font=dict(color=COLORS["gray"]),
        xaxis=dict(showgrid=False, linecolor=COLORS["gray_dark"]),
        yaxis=dict(showgrid=True, gridcolor=COLORS["gray_dark"], linecolor=COLORS["gray_dark"], ticksuffix="%"),
        margin=dict(l=0, r=0, t=10, b=0),
        height=300,
        showlegend=False,
    )
    
    return fig


def create_win_loss_donut(metrics: dict) -> go.Figure:
    """Donut chart de wins vs losses."""
    fig = go.Figure()
    
    wins = metrics.get("wins", 0)
    losses = metrics.get("losses", 0)
    
    if wins == 0 and losses == 0:
        return fig
    
    fig.add_trace(go.Pie(
        values=[wins, losses],
        labels=['✅ Wins', '❌ Losses'],
        hole=0.65,
        marker=dict(colors=[COLORS["green"], COLORS["red"]]),
        textinfo='none',
        hovertemplate='<b>%{label}</b><br>%{value} trades<br>%{percent}<extra></extra>'
    ))
    
    fig.update_layout(
        plot_bgcolor=COLORS["bg_card"],
        paper_bgcolor=COLORS["bg_card"],
        font=dict(color=COLORS["gray"]),
        margin=dict(l=0, r=0, t=0, b=0),
        height=200,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(color=COLORS["white"], size=12)),
        annotations=[dict(
            text=f'<b>{metrics.get("win_rate", 0)}%</b>',
            x=0.5, y=0.5,
            font=dict(size=28, color=COLORS["orange"], family="Arial"),
            showarrow=False
        )]
    ))
    
    return fig


def create_symbols_chart(df: pd.DataFrame) -> go.Figure:
    """Gráfico de rendimiento por símbolo."""
    fig = go.Figure()
    
    if df.empty or 'symbol' not in df.columns or 'pnl_pct' not in df.columns:
        return fig
    
    symbol_stats = df.groupby('symbol').agg({
        'pnl_pct': ['sum', 'count']
    }).reset_index()
    symbol_stats.columns = ['symbol', 'pnl', 'trades']
    symbol_stats = symbol_stats.sort_values('pnl', ascending=True).tail(10)
    
    colors = [COLORS["green"] if x >= 0 else COLORS["red"] for x in symbol_stats['pnl']]
    
    fig.add_trace(go.Bar(
        x=symbol_stats['pnl'],
        y=symbol_stats['symbol'],
        orientation='h',
        marker_color=colors,
        text=[f"{t} trades" for t in symbol_stats['trades']],
        textposition='inside',
        textfont=dict(color='white', size=10),
        hovertemplate='<b>%{y}</b><br>P&L: %{x:+.2f}%<br>%{text}<extra></extra>'
    ))
    
    fig.add_vline(x=0, line_dash="solid", line_color=COLORS["gray_dark"], line_width=1)
    
    fig.update_layout(
        plot_bgcolor=COLORS["bg_card"],
        paper_bgcolor=COLORS["bg_card"],
        font=dict(color=COLORS["gray"]),
        xaxis=dict(showgrid=True, gridcolor=COLORS["gray_dark"], ticksuffix="%"),
        yaxis=dict(showgrid=False),
        margin=dict(l=0, r=0, t=10, b=0),
        height=300,
        showlegend=False,
    )
    
    return fig


# =============================================
# INTERFAZ PRINCIPAL
# =============================================

def main():
    # Header con logo
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0 30px 0;">
        <h1 style="font-size: 48px; font-weight: 900; margin: 0; letter-spacing: -2px;">
            JOTA<span style="color: #f97316;">TRADES</span>
        </h1>
        <p style="color: #6b7280; font-size: 14px; margin-top: 8px;">
            📊 Bot Performance Dashboard • Transparencia Total
        </p>
        <div style="margin-top: 12px;">
            <span style="background: #0f0f12; border: 1px solid #1f1f23; padding: 6px 12px; border-radius: 20px; font-size: 12px; color: #22c55e;">
                🟢 En vivo
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar configuración
    if not SHEET_ID:
        st.warning("⚠️ No hay Sheet ID configurado.")
        st.code("""
# Crear archivo .env con:
GOOGLE_SHEET_ID=tu_sheet_id_aqui
INITIAL_BALANCE=10000
        """)
        st.stop()
    
    # Cargar datos
    with st.spinner("📡 Conectando con el bot..."):
        raw_df = load_data_from_sheets(SHEET_ID, SHEET_GID)
    
    if raw_df.empty:
        st.error("❌ No se pudieron cargar los datos. Verificá que el Sheet sea público.")
        st.stop()
    
    # Procesar
    df = process_trades(raw_df)
    metrics = calculate_metrics(df, INITIAL_BALANCE)
    
    # =========================================
    # KPIs PRINCIPALES
    # =========================================
    
    st.markdown("### 📈 Rendimiento del Bot")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Trades",
            value=metrics["total_trades"],
            delta=f"{metrics['wins']}W / {metrics['losses']}L"
        )
    
    with col2:
        wr_color = "🟢" if metrics['win_rate'] >= 50 else "🔴"
        st.metric(
            label="Win Rate",
            value=f"{metrics['win_rate']}%",
            delta=wr_color
        )
    
    with col3:
        pf = metrics['profit_factor']
        pf_display = "∞" if pf >= 999 else f"{pf:.2f}"
        pf_status = "🔥" if pf >= 1.5 else ("✅" if pf >= 1 else "⚠️")
        st.metric(
            label="Profit Factor",
            value=pf_display,
            delta=pf_status
        )
    
    with col4:
        pnl = metrics['total_pnl_pct']
        pnl_color = "normal" if pnl >= 0 else "inverse"
        st.metric(
            label="P&L Total",
            value=f"{pnl:+.2f}%",
            delta=f"${metrics['current_balance'] - INITIAL_BALANCE:+,.2f}",
            delta_color=pnl_color
        )
    
    with col5:
        dd = metrics['max_drawdown']
        dd_status = "Controlado" if dd > -10 else ("Moderado" if dd > -20 else "Alto")
        st.metric(
            label="Max Drawdown",
            value=f"{dd:.2f}%",
            delta=dd_status,
            delta_color="off"
        )
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # =========================================
    # GRÁFICOS
    # =========================================
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("### 💰 Evolución del Balance")
        fig_equity = create_equity_curve(df, INITIAL_BALANCE)
        st.plotly_chart(fig_equity, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown("### 📊 P&L por Día")
        fig_daily = create_daily_pnl_chart(df)
        st.plotly_chart(fig_daily, use_container_width=True, config={'displayModeBar': False})
    
    with col_right:
        st.markdown("### 🎯 Win Rate")
        fig_donut = create_win_loss_donut(metrics)
        st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown("### 📋 Estadísticas")
        
        # Stats en formato más visual
        st.markdown(f"""
        <div style="background: #0f0f12; border: 1px solid #1f1f23; border-radius: 12px; padding: 16px;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                <div style="text-align: center; padding: 10px; background: rgba(34, 197, 94, 0.1); border-radius: 8px;">
                    <p style="color: #6b7280; font-size: 11px; margin: 0;">AVG WIN</p>
                    <p style="color: #22c55e; font-size: 18px; font-weight: 700; margin: 4px 0 0 0;">+{metrics['avg_win']:.2f}%</p>
                </div>
                <div style="text-align: center; padding: 10px; background: rgba(239, 68, 68, 0.1); border-radius: 8px;">
                    <p style="color: #6b7280; font-size: 11px; margin: 0;">AVG LOSS</p>
                    <p style="color: #ef4444; font-size: 18px; font-weight: 700; margin: 4px 0 0 0;">{metrics['avg_loss']:.2f}%</p>
                </div>
                <div style="text-align: center; padding: 10px; background: rgba(34, 197, 94, 0.1); border-radius: 8px;">
                    <p style="color: #6b7280; font-size: 11px; margin: 0;">BEST TRADE</p>
                    <p style="color: #22c55e; font-size: 18px; font-weight: 700; margin: 4px 0 0 0;">+{metrics['best_trade']:.2f}%</p>
                </div>
                <div style="text-align: center; padding: 10px; background: rgba(239, 68, 68, 0.1); border-radius: 8px;">
                    <p style="color: #6b7280; font-size: 11px; margin: 0;">WORST TRADE</p>
                    <p style="color: #ef4444; font-size: 18px; font-weight: 700; margin: 4px 0 0 0;">{metrics['worst_trade']:.2f}%</p>
                </div>
                <div style="text-align: center; padding: 10px; background: rgba(249, 115, 22, 0.1); border-radius: 8px;">
                    <p style="color: #6b7280; font-size: 11px; margin: 0;">RACHA WINS</p>
                    <p style="color: #f97316; font-size: 18px; font-weight: 700; margin: 4px 0 0 0;">{metrics['consecutive_wins']}</p>
                </div>
                <div style="text-align: center; padding: 10px; background: rgba(249, 115, 22, 0.1); border-radius: 8px;">
                    <p style="color: #6b7280; font-size: 11px; margin: 0;">RACHA LOSSES</p>
                    <p style="color: #f97316; font-size: 18px; font-weight: 700; margin: 4px 0 0 0;">{metrics['consecutive_losses']}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # =========================================
    # POR SÍMBOLO
    # =========================================
    
    st.markdown("### 🏆 Rendimiento por Par")
    fig_symbols = create_symbols_chart(df)
    st.plotly_chart(fig_symbols, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # =========================================
    # HISTORIAL
    # =========================================
    
    st.markdown("### 📜 Últimos Trades")
    
    if not df.empty:
        # Columnas a mostrar
        display_cols = []
        col_names = []
        
        if 'datetime' in df.columns:
            display_cols.append('datetime')
            col_names.append('Fecha')
        if 'symbol' in df.columns:
            display_cols.append('symbol')
            col_names.append('Par')
        if 'side' in df.columns:
            display_cols.append('side')
            col_names.append('Lado')
        if 'pnl_pct' in df.columns:
            display_cols.append('pnl_pct')
            col_names.append('P&L')
        if 'status' in df.columns:
            display_cols.append('status')
            col_names.append('Resultado')
        
        if display_cols:
            display_df = df[display_cols].copy()
            display_df = display_df.sort_values('datetime', ascending=False).head(30) if 'datetime' in display_df.columns else display_df.head(30)
            
            # Formatear
            if 'datetime' in display_df.columns:
                display_df['datetime'] = display_df['datetime'].dt.strftime('%d/%m %H:%M')
            if 'pnl_pct' in display_df.columns:
                display_df['pnl_pct'] = display_df['pnl_pct'].apply(lambda x: f"{x:+.2f}%" if pd.notna(x) else "-")
            
            display_df.columns = col_names
            
            st.dataframe(display_df, use_container_width=True, hide_index=True, height=350)
    
    # =========================================
    # CTA - CALL TO ACTION
    # =========================================
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="text-align: center; padding: 40px 20px; background: linear-gradient(180deg, #0f0f12 0%, #0a0a0c 100%); border-radius: 16px; border: 1px solid #1f1f23; margin: 20px 0;">
        <h2 style="color: white; font-size: 28px; margin: 0 0 8px 0;">¿Querés estas señales?</h2>
        <p style="color: #6b7280; font-size: 15px; margin: 0 0 24px 0;">
            Únete a nuestra comunidad y recibí las señales del bot en tiempo real
        </p>
        
        <div class="cta-container">
            <a href="{TELEGRAM_PUBLICO}" target="_blank" class="cta-button cta-primary">
                📢 Grupo Público (Gratis)
            </a>
            <a href="{TELEGRAM_VIP}" target="_blank" class="cta-button cta-secondary">
                💎 Acceso VIP
            </a>
            <a href="{TELEGRAM_VIP}" target="_blank" class="cta-button cta-secondary">
                📊 Sigma Quant
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0; margin-top: 20px;">
        <p style="color: #3f3f46; font-size: 12px; margin: 0;">
            JOTAtrades © 2025 • Los resultados pasados no garantizan resultados futuros
        </p>
        <p style="color: #27272a; font-size: 11px; margin: 8px 0 0 0;">
            Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')} UTC
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Botón refresh
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Actualizar Datos", use_container_width=True, type="secondary"):
            st.cache_data.clear()
            st.rerun()


if __name__ == "__main__":
    main()

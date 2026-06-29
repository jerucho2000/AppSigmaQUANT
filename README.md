# 📊 JOTAtrades Dashboard

**Dashboard de rendimiento del bot de trading** — Muestra métricas en tiempo real conectando con Google Sheets.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40-red?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- 📈 **Equity Curve** — Evolución del balance en tiempo real
- 📊 **P&L Diario** — Gráfico de barras verde/rojo por día
- 🎯 **Win Rate** — Donut chart con porcentaje de aciertos
- 📉 **Drawdown** — Máxima caída desde el pico
- 🏆 **Análisis por Símbolo** — Rendimiento por par/activo
- 📜 **Historial** — Tabla de últimos 50 trades
- 🔄 **Auto-refresh** — Datos siempre actualizados
- 🌙 **Tema Oscuro** — Look profesional tipo Bloomberg

---

## 🚀 Instalación Rápida

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/jotatrades-dashboard.git
cd jotatrades-dashboard
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar tu Google Sheet

```bash
# Copiar el archivo de ejemplo
cp .env.example .env
```

Abrir `.env` y pegar tu Sheet ID:

```env
GOOGLE_SHEET_ID=1ABC123xyz...
GOOGLE_SHEET_GID=0
INITIAL_BALANCE=10000
```

### 5. Correr el dashboard

```bash
streamlit run app.py
```

Se abre en `http://localhost:8501` 🎉

---

## 📋 Formato del Google Sheet

Tu Google Sheet debe tener estas columnas en la **Fila 1**:

| Tyme | Symbol | TF | Preset | Side | Entry | TP 1 | SL | Estado | Score | Status | Recorrido | Final | % | Msg ID |
|------|--------|-----|--------|------|-------|------|-----|--------|-------|--------|-----------|-------|-----|--------|

**Importante:**
- La columna `%` debe tener el porcentaje de ganancia/pérdida de cada trade
- La columna `Status` debe indicar WIN/LOSS (o similar)
- El Sheet debe ser **PÚBLICO** (Compartir → Cualquier persona con el enlace → Lector)

---

## ☁️ Deploy en Streamlit Cloud (Gratis)

### 1. Subir a GitHub

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Ir a [share.streamlit.io](https://share.streamlit.io)

1. Click en **"New app"**
2. Conectar tu repositorio de GitHub
3. Seleccionar `app.py` como archivo principal
4. En **"Advanced settings"** agregar los secrets:

```toml
GOOGLE_SHEET_ID = "tu_sheet_id_aqui"
GOOGLE_SHEET_GID = "0"
INITIAL_BALANCE = "10000"
```

5. Click en **Deploy** 🚀

En 2-3 minutos tenés tu URL pública: `https://tu-app.streamlit.app`

---

## 🔧 Configuración

| Variable | Descripción | Default |
|----------|-------------|---------|
| `GOOGLE_SHEET_ID` | ID de tu Google Sheet | (requerido) |
| `GOOGLE_SHEET_GID` | ID de la pestaña (tab) | `0` |
| `INITIAL_BALANCE` | Balance inicial en USD | `10000` |

---

## 📁 Estructura

```
jotatrades-dashboard/
├── app.py              # Aplicación principal
├── requirements.txt    # Dependencias Python
├── .env.example        # Template de configuración
├── .gitignore          # Archivos ignorados
└── README.md           # Este archivo
```

---

## 🛠 Tech Stack

- **Python 3.9+**
- **Streamlit** — Framework web
- **Pandas** — Procesamiento de datos
- **Plotly** — Gráficos interactivos
- **Google Sheets** — Fuente de datos

---

## 📞 Contacto

**JOTAtrades**
- 🚀 VIP: [Link al VIP]
- 📊 Sigma Quant: [Link al producto]
- 📱 Telegram: [@jotatrades]

---

## 📄 Licencia

MIT © 2025 JOTAtrades

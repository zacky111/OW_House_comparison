VISUAL_MD = """
<style>

/* =========================
   GLOBAL / THEME
========================= */

:root {
    --bg-main: #0E1117;
    --bg-card: #1B1F2A;
    --bg-input: #24283A;
    --border-soft: #2F3446;

    --accent: #66B2FF;
    --accent-strong: #1493FF;
    --accent-soft: rgba(102,178,255,0.15);

    --text-main: #EAEAEA;
    --text-muted: #AAB2C8;
}

html, body, [class*="css"] {
    background-color: var(--bg-main);
    color: var(--text-main);
    font-family: 'Poppins', sans-serif;
}

/* Ukrycie Streamlit chrome */
#MainMenu, footer, header {
    visibility: hidden;
}

/* =========================
   TYPOGRAPHY
========================= */

h1 {
    font-size: 2.2rem;
    font-weight: 700;
    letter-spacing: 0.5px;
}

h2 {
    font-size: 1.6rem;
    font-weight: 600;
}

h3 {
    font-size: 1.2rem;
    font-weight: 500;
    color: var(--accent);
}

p {
    color: var(--text-muted);
}

/* =========================
   CARDS / SECTIONS
========================= */

div[data-testid="stForm"],
section[data-testid="stSidebar"] > div,
.block-container > div {
    background: linear-gradient(
        180deg,
        var(--bg-card),
        rgba(27,31,42,0.95)
    );
    border-radius: 16px;
    padding: 1.6rem;
    border: 1px solid var(--border-soft);
    box-shadow: 0 12px 30px rgba(0,0,0,0.4);
    margin-bottom: 1.5rem;
}

/* =========================
   TABS
========================= */

.stTabs [data-baseweb="tab"] {
    font-size: 15px;
    font-weight: 500;
    color: var(--text-muted);
    padding: 10px 18px;
    border-radius: 10px;
    transition: all 0.25s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--accent);
    background-color: var(--accent-soft);
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent-strong);
    background-color: rgba(20,147,255,0.18);
    box-shadow: inset 0 -3px 0 var(--accent-strong);
}

/* =========================
   INPUTS / SELECTS
========================= */

.stNumberInput input,
.stTextInput input,
.stSelectbox div[data-baseweb="select"],
.stMultiSelect div[data-baseweb="select"] {
    background-color: var(--bg-input) !important;
    color: var(--text-main) !important;
    border-radius: 10px;
    border: 1px solid var(--border-soft);
    transition: 0.2s ease;
}

.stNumberInput input:focus,
.stTextInput input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 2px rgba(102,178,255,0.25);
}

/* Labels */
label {
    color: var(--text-muted) !important;
    font-size: 0.9rem;
}

/* =========================
   BUTTONS – SOLID & READABLE
========================= */

.stButton > button {
    background-color: #E6F0FF !important; /* JASNE, JEDNOLITE */
    color: #0E1117 !important;           /* CIEMNY TEKST */
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.4rem;
    font-weight: 700;
    letter-spacing: 0.2px;
    box-shadow: none !important;         /* KLUCZOWE */
    opacity: 1 !important;               /* KLUCZOWE */
}

/* WYMUSZENIE TEKSTU */
.stButton > button * {
    color: #0E1117 !important;
    opacity: 1 !important;
}

/* Hover – minimalny, bez gradientu */
.stButton > button:hover {
    background-color: #66B2FF !important;
}

/* Active */
.stButton > button:active {
    background-color: #1493FF !important;
}

/* Disabled */
.stButton > button:disabled {
    background-color: #3A3F55 !important;
    color: #999 !important;
}


/* =========================
   DATAFRAMES / TABLES
========================= */

[data-testid="stDataFrame"] {
    background-color: var(--bg-card);
    border-radius: 14px;
    padding: 10px;
    border: 1px solid var(--border-soft);
}

/* =========================
   ALERTS
========================= */

.stAlert {
    border-radius: 12px;
    border: 1px solid var(--border-soft);
}

/* =========================
   SCROLLBAR
========================= */

::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-track {
    background: #111420;
}
::-webkit-scrollbar-thumb {
    background: #2F80ED;
    border-radius: 10px;
}

</style>
"""


old = """
<style>
/* === DARK MODE === */
body {
    background-color: #0E1117;
    color: #EEE;
    font-family: 'Poppins', sans-serif;
}

/* Nagłówki */
h1, h2, h3 {
    color: #F5F5F5;
    font-weight: 600;
}

/* Zakładki */
.stTabs [data-baseweb="tab"] {
    font-size: 16px;
    font-weight: 500;
    color: #B0C4DE;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #66B2FF;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #66B2FF;
    border-bottom: 3px solid #66B2FF;
}

/* Formularze i kontenery */
div[data-testid="stForm"] {
    background-color: #1E1E26;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 0 8px rgba(0,0,0,0.5);
    color: #EEE;
}

/* Pola wejściowe i selecty */
.stNumberInput input, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
    background-color: #2B2B36 !important;
    color: #EEE !important;
    border-radius: 6px;
    border: 1px solid #3C3C4A;
}

/* Etykiety pól */
label {
    color: #B0C4DE !important;
}

/* Przyciski */
.stButton>button {
    background-color: #007ACC;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.2rem;
    font-weight: 600;
    transition: 0.3s;
}
.stButton>button:hover {
    background-color: #1493FF;
}

/* Tabele */
[data-testid="stDataFrame"] {
    background-color: #1E1E26;
    color: #EEE;
    border-radius: 10px;
    padding: 10px;
}
</style>
"""
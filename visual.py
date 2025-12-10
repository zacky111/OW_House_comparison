VISUAL_MD = """
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
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="ONPE - Análisis de Participación 2021",
    page_icon="🏛️",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #003B6E; }
    h1, h2, h3 { color: #002D5A; font-family: 'Helvetica', sans-serif; }
    .stMetric { background-color: #ffffff; border-top: 4px solid #002D5A; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ ANÁLISIS DE ELECCIONES DE LA ONPE 2021")
st.markdown("#### Reporte de Participación Ciudadana y Actas Procesadas")
st.divider()

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/jmcastagnetto/2021-elecciones-generales-peru-datos-de-onpe/refs/heads/main/presidencial-datos-generales.csv"
    df = pd.read_csv(url)
    
    # Limpieza 
    df = df.dropna(subset=['ubigeo'])
    
    cols_num = ['ELECTORES_HABIL', 'TOT_CIUDADANOS_VOTARON', 'POR_CIUDADANOS_VOTARON', 'ACTAS_PROCESADAS']
    for col in cols_num:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

try:
    df = load_data()

    #  Filtros 
    st.sidebar.header("Filtros por departamentos")
    lista_deps = sorted(df['departamento'].unique())
    dep_sel = st.sidebar.selectbox("Seleccione Departamento:", lista_deps)

    df_filtered = df[df['departamento'] == dep_sel]

    #  Métricas Principales
    st.markdown(f"### Resumen de Participación: {dep_sel}")
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.metric("Total Electores Hábiles en el departamento", f"{int(df_filtered['ELECTORES_HABIL'].sum()):,}")
    with c2:
        total_votos = df_filtered['TOT_CIUDADANOS_VOTARON'].sum()
        st.metric("Ciudadanos que Votaron", f"{int(total_votos):,}")
    with c3:
        participacion_media = df_filtered['POR_CIUDADANOS_VOTARON'].mean()
        st.metric("% Participación Promedio", f"{participacion_media:.2f}%")
    with c4:

        actas = df_filtered['ACTAS_PROCESADAS'].sum()
        st.metric("Total Actas Procesadas", f"{int(actas):,}")

    st.divider()

    # --- PARTE 3: Visualización de Resultados ---
    col_izq, col_der = st.columns(2)

    with col_izq:
        st.write("**Participación por Provincia**")
        prov_votos = df_filtered.groupby('provincia')['TOT_CIUDADANOS_VOTARON'].sum().sort_values(ascending=False).head(10)
        fig1, ax1 = plt.subplots()
        sns.barplot(x=prov_votos.values, y=prov_votos.index, palette="Blues_r", ax=ax1)
        ax1.set_xlabel("Número de Votantes")
        st.pyplot(fig1)

    with col_der:
        st.write("**Actas procesadas post conteo al 100%**")
        procesadas = df_filtered['ACTAS_PROCESADAS'].sum()
        pendientes = df_filtered['POR_PROCESAR'].sum() if 'POR_PROCESAR' in df.columns else 0
        
        fig2, ax2 = plt.subplots()
        ax2.pie([procesadas, pendientes], labels=['Procesadas', 'Pendientes'], 
                autopct='%1.1f%%', colors=['#002D5A', '#A0C4FF'], startangle=90)
        ax2.axis('equal')
        st.pyplot(fig2)

    with st.expander("  Ubigeos y Macroregiones"):
        st.dataframe(
            df_filtered[['ubigeo', 'provincia', 'distrito', 'TOT_CIUDADANOS_VOTARON', 'macroregion_inei']], 
            use_container_width=True
        )

except Exception as e:
    st.error(f"Error al procesar columnas: {e}")
    st.info("Verifica que el archivo contenga las columnas: ELECTORES_HABIL, TOT_CIUDADANOS_VOTARON")
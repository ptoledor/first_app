#Needed
#pip install uvicorn gunicorn fastapi pydantic
#run: streamlit run app.py

import streamlit as st
import pandas as pd
import numpy as np
import xlsxwriter
import openpyxl


# Configuracion inicial --------------------------------------------------
with st.sidebar:
    st.image('https://www.ucsc.cl/wp-content/themes/ucsc-3-0/img/logo-ucsc.svg')
    st.title('Equating para muestras pequeñas')
    choice = st.radio('Opciones', ['Home', 'Diseño de prueba', 'Asignacion', 'Equating', 'Lab'])
    st.info('By PTR')

# HOME ------------------------------------------------------------
if choice == 'Home':
    st.write('Pagina de inicio')



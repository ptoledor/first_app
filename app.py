#Needed
#pip install uvicorn gunicorn fastapi pydantic
#run: streamlit run app.py

import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import pandas as pd
import xlsxwriter
import openpyxl
import numpy as np
import os
import io
import new_equating as neq


# Configuracion inicial --------------------------------------------------
with st.sidebar:
    st.image('https://www.ucsc.cl/wp-content/themes/ucsc-3-0/img/logo-ucsc.svg')
    st.title('Equating para muestras pequeñas')
    choice = st.radio('Opciones', ['Home', 'Diseño de prueba', 'Asignacion', 'Equating', 'Lab'])
    st.info('By PTR')


# Variables de Session State ---------------------------------------
if 'alumnos' not in st.session_state:
    st.session_state['alumnos'] = 0

if 'modulos' not in st.session_state:
    st.session_state['modulos'] = 0

if 'pr' not in st.session_state:
    st.session_state['pr'] = 0

# if ('qa' not in st.session_state) and ('qm' not in st.session_state):
#     st.session_state['qm'] = [0 for _ in range(20)]
#     st.session_state['qa'] = [0 for _ in range(20)]

if 'gate02' not in st.session_state:
    st.session_state['gate02'] = [False for _ in range(5)]

if 'gate03' not in st.session_state:
    st.session_state['gate03'] = [False for _ in range(5)]

# HOME ------------------------------------------------------------
if choice == 'Home':
    st.write('Pagina de inicio')


# 02 DISEÑO ------------------------------------------------------------
if choice == 'Diseño de prueba':

    st.subheader('Diseño de prueba')

    with st.form(key='form0201'):
        st.session_state['alumnos'] = st.number_input('Ingrese cantidad de estudiantes', step=1, min_value=0, value=st.session_state['alumnos'])
        st.session_state['modulos'] = st.number_input('Ingrese cantidad de modulos', step=1, min_value=0, max_value=20, value=st.session_state['modulos'])
        st.session_state['pr'] = st.number_input('Ingrese cantidad de preguntas a responder en el examen', step=1, min_value=0, value=st.session_state['pr'])
        st.session_state['gate02'][0] = st.form_submit_button()
    

    if (st.session_state['modulos'] > st.session_state['pr']) and st.session_state['gate02'][0]:
        st.error('Los modulos son mayores a las preguntas!')
        st.stop()
    
    if st.session_state['gate02'][0]:
        st.subheader('Indicaciones')
        neq.diseno_prueba(st.session_state['alumnos'], st.session_state['modulos'], st.session_state['pr'], verbose=True)

       
# 03 ASIGNACION ------------------------------------------------------------
if choice == 'Asignacion':

    st.subheader('Asignación preguntas-estudiante')

    with st.form(key='form0301'):
        st.session_state['alumnos'] = st.number_input(label='Ingrese cantidad de estudiantes', 
                                                        step=1, 
                                                        min_value=0,
                                                        value=st.session_state['alumnos'])
        st.session_state['modulos'] = st.number_input(label='Ingrese cantidad de módulos',
                                                        step=1, 
                                                        min_value=0, max_value=20,
                                                        value=st.session_state['modulos'])
        st.form_submit_button()

    if st.session_state['FormSubmitter:form0301-Submit']:
        st.session_state['gate03'] = [False for _ in range(5)]
        st.session_state['gate03'][0] = True
        
    if st.session_state['gate03'][0]:
        st.success('Ingresa detalladamente la informacion de preguntas por modulo')
        qm = [0 for _ in range(st.session_state['modulos'])]
        qa = [0 for _ in range(st.session_state['modulos'])]

        with st.form(key='form0302'):
            for mod in range(st.session_state['modulos']):
                qm[mod] = st.number_input(f'Modulo {mod+1}: Preguntas ',            step=1, min_value=0)
                qa[mod] = st.number_input(f'Modulo {mod+1}: Preguntas a responder', step=1, min_value=0)
            st.form_submit_button()

        if st.session_state['FormSubmitter:form0302-Submit']:
            st.session_state['gate03'][1] = True
        
        if st.session_state['gate03'][1]:
            st.session_state['qm'] = qm
            st.session_state['qa'] = qa
        
            for mod in range(st.session_state['modulos']):
                if qm[mod] <= 0:
                    st.error(f'Modulo {mod+1}: Preguntas, No puede ser 0 o negativo')
                    st.stop()
                elif qa[mod] <= 0:
                    st.error(f'Modulo {mod+1}: Preguntas a responder, No puede ser 0')
                    st.stop()
                elif qa[mod] > qm[mod]:
                    st.error(f'Modulo {mod+1}: Preguntas no puede ser menor a Preguntas-a-responder')
                    st.stop()
                
            #Datos de la combinatoria   
            len_comb = neq.combinaciones_totales(st.session_state['modulos'], qm, qa)

            #Seleccion de metodos de asignación y generación de la asignación
            st.success('¿Que método de asignación desea usar?')
            par_selectbox1 = st.selectbox('Elige uno', ['...', 'Aleatorio', 'Aleatorio++', 'Heurístico'])

            if par_selectbox1 != '...':
                combs = neq.matriz_combinacions(len_comb, st.session_state['modulos'], qm, qa)
                
                if par_selectbox1 == 'Aleatorio':
                    asignacion = neq.asignacion_aleatoria(st.session_state['alumnos'], combs)

                elif par_selectbox1 == 'Aleatorio++':
                    slider0301 = st.slider(label='Numero de muestreos', min_value=1, value=5)
                    score_aux= np.inf

                    for _ in range(slider0301):
                        asignacion_aux = neq.asignacion_aleatoria_plus(st.session_state['alumnos'], combs)

                        if neq.get_score(asignacion_aux) < score_aux:
                            score_aux = neq.get_score(asignacion_aux)
                            asignacion = asignacion_aux.copy(deep=True)

                elif par_selectbox1 == 'Heurístico':
                    st.error('No programado')
                    st.stop()

                #Mostrar puntaje de la matriz
                score = neq.get_score(asignacion)
                st.info(f'El score de la matriz de asignacion es : {score}')

                #Descargar asignacion
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    asignacion.to_excel(writer, sheet_name='asignacion')
                    asignacion.to_excel(writer, sheet_name='puntajes')
                    writer.close()

                st.download_button(label='Descargar Asignacion', data=output, file_name='asignacion.xlsx', mime='application/vnd.ms-excel')
                
                #Mostrar tabla
                st.table(asignacion)


# EQUATING ------------------------------------------------------------
if choice == 'Equating':
    st.subheader('Equating')
    st.info('La matriz debe tener index (identificacion de alumnos) y header (identificación de preguntas)')

    #Upload
    file = st.file_uploader('Sube la matriz de asignación y la matriz de puntajes')
    if file:
        evaluacion = pd.read_excel(file)

        eval_alumnos = evaluacion.shape[0]
        eval_preguntas = evaluacion.shape[1] - 1

        st.success(f'La matriz tiene {eval_alumnos} alumnos y {eval_preguntas} preguntas.')
        st.dataframe(evaluacion)

        evaluacion_alumnos = evaluacion[evaluacion.columns[0]]
        evaluacion = evaluacion.drop(columns=[evaluacion.columns[0]])

        asig = evaluacion.copy(deep=True)
        asig = asig.mask(asig > 0, 1)
        st.dataframe(asig)


        dificultad = neq.estimador_dificultad(eval_alumnos, eval_preguntas, asig, evaluacion)
        st.success('Dificultades estimadas por pregunta')
        st.write(dificultad)

        with st.form(key='form0401'):
            puntaje_max = st.number_input(f'Puntaje máximo',  min_value=0)
            puntaje_min = st.number_input(f'Puntaje mínimo',  min_value=0)
            st.form_submit_button()
        
        st.success('Puntajes corregidos')



# Lab ------------------------------------------------------------
if choice == 'Lab':
    st.subheader('Equating')
    st.info('La matriz debe tener index (identificacion de alumnos) y header (identificación de preguntas)')

    # with st.form(key='form0501'):
    #     puntaje_max = st.number_input(f'Puntaje máximo',  min_value=0)
    #     puntaje_min = st.number_input(f'Puntaje mínimo',  min_value=0)
    #     st.form_submit_button()

    #Upload
    file = st.file_uploader('Sube la matriz de asignación y la matriz de puntajes')
    if file:
        evaluacion = pd.read_excel(file)

        eval_alumnos = evaluacion.shape[0]
        eval_preguntas = evaluacion.shape[1] - 1

        st.success(f'La matriz tiene {eval_alumnos} alumnos y {eval_preguntas} preguntas.')
        st.dataframe(evaluacion)

        evaluacion_alumnos = evaluacion[evaluacion.columns[0]]
        evaluacion = evaluacion.drop(columns=[evaluacion.columns[0]])
        evaluacion = evaluacion - 1

        qa = st.slider('Ingrese preguntas a contestar', min_value=1, max_value=eval_preguntas)

        #Matriz de asignacion
        len_comb = neq.combinaciones_totales(1, [eval_preguntas], [qa])
        combs = neq.matriz_combinacions(len_comb, 1, [eval_preguntas], [qa])
        score_aux= np.inf
        for _ in range(100):
            asignacion_aux = neq.asignacion_aleatoria_plus(eval_alumnos, combs)
        if neq.get_score(asignacion_aux) < score_aux:
            score_aux = neq.get_score(asignacion_aux)
            asignacion = asignacion_aux.copy(deep=True)

        st.dataframe(asignacion)


        dificultad = neq.estimador_dificultad(eval_alumnos, eval_preguntas, asignacion, evaluacion)
        st.success('Dificultades estimadas por pregunta')
        st.write(dificultad)

        par_selectbox0501 = st.selectbox('Elige un método de corrección', ['...', 'Normal', 'Solo Aumentos'])

        if par_selectbox0501 == 'Normal':
            st.success('Puntajes corregidos')
            corr = neq.corregir_puntajes_normal(eval_preguntas, eval_alumnos, asignacion, evaluacion, dificultad)

        elif par_selectbox0501 == 'Solo Aumentos':
            st.success('Puntajes corregidos')
            corr = neq.corregir_puntajes_aumentos(eval_preguntas, eval_alumnos, asignacion, evaluacion, dificultad)
        
        st.dataframe(corr)

        error_sin_corr = round(corr['error_sin_corr'].sum(),2)
        error_corr = round(corr['error_corr'].sum(),2)

        st.info(f'Error sin corrección: {error_sin_corr}, Error con corrección: {error_corr}')
        st.button(label='Refresh')

        confusion = corr.groupby(['Confusion'], as_index=False).agg(Cantidad=('Confusion','count'))
        st.table(confusion)


        neq.grafico_confusion2(corr)




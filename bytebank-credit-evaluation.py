import streamlit as st
import pandas as pd
from joblib import load
from utils import Transformer

def validar_dados(dict_respostas):
    if dict_respostas['years_working'] != 0 and dict_respostas['years_unemployed'] != 0:
        st.warning('Dados de emprego/desemprego incompatíveis.')
        return False
    return True

def validar_negacao(dict_respostas):
    modelo = load('objects/model.joblib')
    features = load('objects/features.joblib')

    if dict_respostas['years_working'] > 0:
        dict_respostas['years_working'] = dict_respostas['years_working'] * -1

    respostas = []
    for coluna in features:
        respostas.append(dict_respostas[coluna])

    df_novo_cliente = pd.DataFrame(data=[respostas], columns=features)

    negacao = modelo.predict(df_novo_cliente)[0]

    return negacao

def estilo_local(nome_do_arquivo):
    with open(nome_do_arquivo) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
estilo_local("style.css")

st.image("img/bytebank_logo_white.png")
st.markdown("<h1 style='text-align: center; color: black;'>💳 Avaliação de Crédito Bytebank 💳</h1>", unsafe_allow_html=True)

st.markdown("Bem-vindo à **Avaliação de Crédito Bytebank**. Preencha as informações abaixo e clique em **Avaliar Crédito** para verificar se seu crédito será <span style='color: green'>aprovado</span> ou <span style='color: red'>negado</span> no Bytebank.", unsafe_allow_html=True)

st.caption("**Aviso:** Bytebank é um banco fictício para fins educacionais apenas. A avaliação é feita com um modelo de machine learning. Mais detalhes podem ser encontrados [aqui no repositório do projeto](https://github.com/diascarolina/credit-scoring-streamlit).")

expander_1 = st.expander("👤 Informações Pessoais")

expander_2 = st.expander("💼 Informações Profissionais")

expander_3 = st.expander("👥 Informações Familiares")

dict_respostas = {}
lista_de_categorias = load("objects/categories_list.joblib")

with expander_1:
    col1_form, col2_form = st.columns(2)

    dict_respostas['age'] = col1_form.slider('Qual sua idade?', help='O controle deslizante pode ser movido usando as teclas de seta.', min_value=0, max_value=100, step=1)

    dict_respostas['education_type'] = col1_form.selectbox('Qual seu nível de escolaridade?', lista_de_categorias['education_type'])

    dict_respostas['marital_status'] = col1_form.selectbox('Qual seu estado civil?', lista_de_categorias['marital_status'])

    dict_respostas['own_car'] = 1 if col2_form.selectbox('Você possui um carro?', ['Sim', 'Não']) == 'Sim' else 0

    dict_respostas['own_phone'] = 1 if col2_form.selectbox('Você possui um telefone? (não celular)', ['Sim', 'Não']) == 'Sim' else 0

    dict_respostas['own_email'] = 1 if col2_form.selectbox('Você possui um endereço de e-mail?', ['Sim', 'Não']) == 'Sim' else 0

with expander_2:
    col3_form, col4_form = st.columns(2)

    dict_respostas['occupation_type'] = col3_form.selectbox('Qual o tipo de seu trabalho?', lista_de_categorias['occupation_type'])

    dict_respostas['income_type'] = col3_form.selectbox('Qual o tipo de sua renda?', lista_de_categorias['income_type'])

    dict_respostas['own_workphone'] = 1 if col3_form.selectbox('Você possui um telefone comercial?', ['Sim', 'Não']) == 'Sim' else 0

    dict_respostas['annual_income'] = col3_form.slider('Qual seu salário mensal?', help='O controle deslizante pode ser movido usando as teclas de seta.', min_value=0, max_value=35000, step=500) * 12

    dict_respostas['years_working'] = col4_form.slider('Há quantos anos você trabalha (em anos)?', help='O controle deslizante pode ser movido usando as teclas de seta.', min_value=0, max_value=50, step=1)

    dict_respostas['years_unemployed'] = col4_form.slider('Há quantos anos você está desempregado (em anos)?', help='O controle deslizante pode ser movido usando as teclas de seta.', min_value=0, max_value=50, step=1)

with expander_3:
    col4_form, col5_form = st.columns(2)

    dict_respostas['housing_type'] = col4_form.selectbox('Qual o tipo de sua moradia?', lista_de_categorias['housing_type'])

    dict_respostas['own_property'] = 1 if col4_form.selectbox('Você possui um imóvel?', ['Sim', 'Não']) == 'Sim' else 0

    dict_respostas['family_size'] = col5_form.slider('Qual o tamanho de sua família?', help='O controle deslizante pode ser movido usando as teclas de seta.', min_value=1, max_value=20, step=1)

    dict_respostas['children_count'] = col5_form.slider('Quantos filhos você tem?', help='O controle deslizante pode ser movido usando as teclas de seta.', min_value=0, max_value=20, step=1)

if st.button('Avaliar Crédito'):
    # Passa a variável 'dict_respostas' como argumento
    if validar_dados(dict_respostas):
        if validar_negacao(dict_respostas):
            st.image("img/denied.gif")
        else:
            st.image("img/approved.gif")
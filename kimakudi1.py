import streamlit as st
import pandas as pd
import json

def validar_dados(dict_respostas):
    if dict_respostas['years_working'] != 0 and dict_respostas['years_unemployed'] != 0:
        st.warning('Dados de emprego/desemprego incompatíveis.')
        return False
        
    if dict_respostas['children_count'] > dict_respostas['family_size']:
        st.warning('Número de filhos não pode ser maior que o tamanho da família.')
        return False
        
    if dict_respostas['age'] < 18:
        st.warning('Idade mínima para análise de crédito é 18 anos.')
        return False
        
    return True

def analisar_credito(dict_respostas):
    """Análise de crédito utilizando múltiplos fatores."""
    # Cálculo do score base
    score = 0
    
    # Fator idade
    if dict_respostas['age'] >= 25:
        score += 100
    else:
        score += (dict_respostas['age'] - 18) * 15
    
    # Fator renda
    if dict_respostas['annual_income'] > 20000:
        score += 150
    else:
        score += (dict_respostas['annual_income'] / 20000) * 150
    
    # Fator educação
    education_scores = {
        'Doutorado': 100,
        'Mestrado': 90,
        'Pós-Graduação': 80,
        'Superior Completo': 70,
        'Superior Incompleto': 50,
        'Ensino Médio': 30,
        'Ensino Fundamental': 20
    }
    score += education_scores.get(dict_respostas['education_type'], 0)
    
    # Fator tempo de trabalho
    if dict_respostas['years_working'] > 0:
        score += min(dict_respostas['years_working'] * 10, 100)
    
    # Fatores de estabilidade
    if dict_respostas['own_property']:
        score += 50
    if dict_respostas['own_car']:
        score += 30
    if dict_respostas['own_workphone']:
        score += 20
    
    # Resultado
    return {
        'previsao': score >= 300,  # Alterado de 'approved' para 'previsao'
        'score': score,  # Alterado de 'credit_score' para 'score'
        'max_comprometimento': (dict_respostas['annual_income'] / 12) * 0.3  # Alterado nome em português
    }

def exibir_resultados(resultado):
    if resultado['previsao']:  # Alterado de 'approved' para 'previsao'
        st.image("img/approved.gif")
        st.success("Seu crédito é viável!")
        st.metric("Score de Crédito", f"{resultado['score']:.0f}/600")  # Alterado 'credit_score' para 'score'
        st.metric("Comprometimento Máximo Mensal", f"KZ {resultado['max_comprometimento']:.2f}")
    else:
        st.image("img/denied.gif")
        st.error("Seu crédito não é recomendado.")
        st.metric("Score de Crédito", f"{resultado['score']:.0f}/600")

def main():
    st.set_page_config(page_title="Kima Kudi - Análise de Crédito", layout="wide")
    
    with open("style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    st.image("img/kima_kudi_logo_white.png")
    st.markdown("<h1 style='text-align: center; color: black;'>🧠 Kima Kudi - Análise Inteligente de Crédito 🧠</h1>", unsafe_allow_html=True)

    tabs = st.tabs(["📝 Formulário", "📊 Estatísticas", "ℹ️ Sobre"])

    with tabs[0]:
        col1, col2 = st.columns(2)
        
        with col1:
            personal_info = st.expander("👤 Informações Pessoais", expanded=True)
        with col2:
            financial_info = st.expander("💰 Informações Financeiras", expanded=True)

        dict_respostas = {}

        with personal_info:
            dict_respostas['name'] = st.text_input('Nome Completo')
            dict_respostas['age'] = st.slider('Idade', 18, 100, 30)
            dict_respostas['education_type'] = st.selectbox(
                'Nível de Escolaridade',
                ['Ensino Fundamental', 'Ensino Médio', 'Superior Incompleto', 
                 'Superior Completo', 'Pós-Graduação', 'Mestrado', 'Doutorado']
            )
            dict_respostas['marital_status'] = st.selectbox(
                'Estado Civil',
                ['Solteiro', 'Casado', 'Divorciado', 'Viúvo', 'União Estável']
            )
            dict_respostas['family_size'] = st.number_input('Tamanho da Família', 1, 20, 1)
            dict_respostas['children_count'] = st.number_input('Quantidade de Filhos', 0, 20, 0)

        with financial_info:
            dict_respostas['annual_income'] = st.number_input('Renda Anual', 0, 1000000, 0)
            dict_respostas['years_working'] = st.number_input('Anos de Trabalho', 0, 50, 0)
            dict_respostas['years_unemployed'] = st.number_input('Anos Desempregado', 0, 50, 0)
            dict_respostas['own_property'] = st.checkbox('Possui Imóvel Próprio')
            dict_respostas['own_car'] = st.checkbox('Possui Carro')
            dict_respostas['own_workphone'] = st.checkbox('Possui Telefone Comercial')

        if st.button('Analisar Crédito', type='primary'):
            if validar_dados(dict_respostas):
                with st.spinner('Analisando seu perfil...'):
                    resultado = analisar_credito(dict_respostas)
                    exibir_resultados(resultado)
                    
                    # Salvando dados com o resultado
                    dados_salvos = dict_respostas.copy()
                    dados_salvos.update(resultado)  # Combina os dicionários
                    
                    try:
                        with open("credit_requests.json", "r+", encoding="utf-8") as file:
                            try:
                                data = json.load(file)
                            except json.JSONDecodeError:
                                data = []
                            data.append(dados_salvos)
                            file.seek(0)
                            file.truncate()
                            json.dump(data, file, indent=4)
                    except FileNotFoundError:
                        with open("credit_requests.json", "w", encoding="utf-8") as file:
                            json.dump([dados_salvos], file, indent=4)

    with tabs[1]:
        st.header("Estatísticas de Análises")
        try:
            with open("credit_requests.json", "r") as file:
                data = json.load(file)
                if data:  # Verifica se há dados
                    df = pd.DataFrame(data)
                    
                    st.metric("Total de Análises", len(df))
                    
                    # Agora usando 'previsao' em vez de 'approved'
                    aprovados = df[df['previsao'] == True]
                    taxa_aprovacao = len(aprovados) / len(df) * 100
                    st.metric("Taxa de Aprovação", f"{taxa_aprovacao:.1f}%")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Distribuição por Escolaridade")
                        education_counts = df['education_type'].value_counts()
                        st.bar_chart(education_counts)
                    
                    with col2:
                        st.subheader("Distribuição por Estado Civil")
                        marital_counts = df['marital_status'].value_counts()
                        st.bar_chart(marital_counts)
                    
                    st.subheader("Distribuição de Scores")
                    st.bar_chart(df['score'])  # Alterado de 'credit_score' para 'score'
                else:
                    st.info("Ainda não há dados de análises realizadas.")
                    
        except FileNotFoundError:
            st.info("Ainda não há dados de análises realizadas.")
        except Exception as e:
            st.error(f"Erro ao carregar estatísticas: {str(e)}")

    with tabs[2]:
        st.header("Sobre o Sistema")
        st.markdown("""
        O Kima Kudi utiliza um sistema avançado de análise de crédito que considera diversos fatores:
        
        - Score de crédito personalizado
        - Análise de capacidade de pagamento
        - Fatores de estabilidade financeira
        - Histórico profissional
        - Perfil socioeconômico
        
        Nossa análise é baseada em um algoritmo que considera múltiplos fatores para garantir
        uma avaliação justa e precisa do seu perfil de crédito.
        """)

if __name__ == "__main__":
    main()
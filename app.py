import streamlit as st
import pandas as pd
from database.init_db import conectar
from utils.database_utils import listar_compras, adicionar_compra, excluir_compra

conn, cursor = conectar()
st.set_page_config(page_title="Controle de Gastos", layout="wide")

st.title("💳 Controle de Gastos Compartilhados")

# Filtros
st.sidebar.header("🔍 Filtros")
filtro_responsavel = st.sidebar.selectbox("Responsável", ["", "Você", "Esposa"])
filtro_cartao = st.sidebar.selectbox("Cartão", ["", "Inter", "Itaú", "Nubank"])
filtro_categoria = st.sidebar.text_input("Categoria")
filtro_descricao = st.sidebar.text_input("Descrição")

# Lista compras
dados = listar_compras(cursor)
df = pd.DataFrame(dados, columns=["ID", "Data", "Responsável", "Cartão", "Categoria", "Descrição", "Valor"])

# Aplicar filtros
if filtro_responsavel:
    df = df[df["Responsável"] == filtro_responsavel]
if filtro_cartao:
    df = df[df["Cartão"] == filtro_cartao]
if filtro_categoria:
    df = df[df["Categoria"].str.contains(filtro_categoria, case=False)]
if filtro_descricao:
    df = df[df["Descrição"].str.contains(filtro_descricao, case=False)]

# Tabela
st.dataframe(df, use_container_width=True)

# Resumo
total_voce = df[df["Responsável"] == "Você"]["Valor"].sum()
total_esposa = df[df["Responsável"] == "Esposa"]["Valor"].sum()
st.markdown(f"**Total Você:** R$ {total_voce:.2f} | **Total Esposa:** R$ {total_esposa:.2f}")

# Formulário para adicionar compra
with st.form("add_form"):
    st.subheader("➕ Nova Compra")
    col1, col2 = st.columns(2)
    data = col1.date_input("Data")
    responsavel = col2.selectbox("Responsável", ["Você", "Esposa"])
    cartao = col1.selectbox("Cartão", ["Inter", "Itaú", "Nubank"])
    categoria = col2.text_input("Categoria")
    descricao = col1.text_input("Descrição")
    valor = col2.number_input("Valor (R$)", step=0.01)

    submit = st.form_submit_button("Adicionar")

    if submit:
        adicionar_compra(cursor, conn, (str(data), responsavel, cartao, categoria, descricao, valor))
        st.success("Compra adicionada com sucesso!")
        st.experimental_rerun()

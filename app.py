import streamlit as st
import pandas as pd
from database.init_db import conectar
from utils.database_utils import listar_compras, adicionar_compra, excluir_compra

# Conexão
conn, cursor = conectar()
st.set_page_config(page_title="Controle de Gastos", layout="wide")
st.title("💳 Controle de Gastos Compartilhados")

# Limites de gasto
LIMITE_VOCE = 2000.00
LIMITE_ESPOSA = 1500.00

# Carregar dados com cache
@st.cache_data
def carregar_compras():
    return listar_compras(cursor)

dados = carregar_compras()
df = pd.DataFrame(dados, columns=["ID", "Data", "Responsável", "Cartão", "Categoria", "Descrição", "Valor"])

# Filtros
with st.sidebar:
    st.header("🔍 Filtros")
    filtro_responsavel = st.selectbox("Responsável", ["", "Você", "Esposa"])
    filtro_cartao = st.selectbox("Cartão", ["", "Inter", "Itaú", "Nubank"])
    filtro_categoria = st.text_input("Categoria")
    filtro_descricao = st.text_input("Descrição")

# Aplicar filtros
if filtro_responsavel:
    df = df[df["Responsável"] == filtro_responsavel]
if filtro_cartao:
    df = df[df["Cartão"] == filtro_cartao]
if filtro_categoria:
    df = df[df["Categoria"].str.contains(filtro_categoria, case=False)]
if filtro_descricao:
    df = df[df["Descrição"].str.contains(filtro_descricao, case=False)]

# Resumo
total_voce = df[df["Responsável"] == "Você"]["Valor"].sum()
total_esposa = df[df["Responsável"] == "Esposa"]["Valor"].sum()
restante_voce = LIMITE_VOCE - total_voce
restante_esposa = LIMITE_ESPOSA - total_esposa

st.markdown(f"""
### 💰 Resumo de Gastos
- **Você:** R$ {total_voce:.2f} / R$ {LIMITE_VOCE:.2f} (Restante: R$ {restante_voce:.2f})
- **Esposa:** R$ {total_esposa:.2f} / R$ {LIMITE_ESPOSA:.2f} (Restante: R$ {restante_esposa:.2f})
""")

# Exportação
st.download_button("⬇️ Exportar CSV", df.to_csv(index=False), file_name="gastos.csv", mime="text/csv")
st.download_button("⬇️ Exportar Excel", df.to_excel(index=False, engine='openpyxl'), file_name="gastos.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Tabela com ações
st.subheader("📋 Lista de Compras")
for _, row in df.iterrows():
    with st.expander(f"{row['Data']} - {row['Descrição']} (R$ {row['Valor']:.2f})"):
        st.markdown(f"**Responsável:** {row['Responsável']} | **Cartão:** {row['Cartão']} | **Categoria:** {row['Categoria']}")
        st.markdown(f"**Valor:** R$ {row['Valor']:.2f}")
        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("🗑️ Excluir", key=f"excluir_{row['ID']}"):
                if st.checkbox(f"Confirmar exclusão de {row['Descrição']}?", key=f"confirm_{row['ID']}"):
                    excluir_compra(cursor, conn, row["ID"])
                    st.success("Compra excluída com sucesso.")
                    st.experimental_rerun()

        with col2:
            with st.form(f"edit_form_{row['ID']}"):
                nova_data = st.date_input("Data", pd.to_datetime(row["Data"]))
                novo_resp = st.selectbox("Responsável", ["Você", "Esposa"], index=["Você", "Esposa"].index(row["Responsável"]))
                novo_cartao = st.selectbox("Cartão", ["Inter", "Itaú", "Nubank"], index=["Inter", "Itaú", "Nubank"].index(row["Cartão"]))
                nova_categoria = st.text_input("Categoria", row["Categoria"])
                nova_desc = st.text_input("Descrição", row["Descrição"])
                novo_valor = st.number_input("Valor (R$)", value=float(row["Valor"]), step=0.01)
                submitted = st.form_submit_button("Salvar alterações")
                if submitted:
                    excluir_compra(cursor, conn, row["ID"])  # substituindo pela atualização simples
                    adicionar_compra(cursor, conn, (str(nova_data), novo_resp, novo_cartao, nova_categoria, nova_desc, novo_valor))
                    st.success("Compra atualizada com sucesso!")
                    st.experimental_rerun()

# Formulário para nova compra
st.subheader("➕ Nova Compra")
with st.form("add_form"):
    col1, col2 = st.columns(2)
    data = col1.date_input("Data")
    responsavel = col2.selectbox("Responsável", ["Você", "Esposa"])
    cartao = col1.selectbox("Cartão", ["Inter", "Itaú", "Nubank"])
    categoria = col2.text_input("Categoria")
    descricao = col1.text_input("Descrição")
    valor = col2.number_input("Valor (R$)", step=0.01)

    submit = st.form_submit_button("Adicionar")
    if submit:
        if categoria and descricao and valor > 0:
            adicionar_compra(cursor, conn, (str(data), responsavel, cartao, categoria, descricao, valor))
            st.success("Compra adicionada com sucesso!")
            st.experimental_rerun()
        else:
            st.error("Preencha todos os campos corretamente.")

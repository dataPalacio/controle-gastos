import streamlit as st
import pandas as pd
from io import BytesIO
from database.init_db import conectar
from utils.database_utils import listar_compras, adicionar_compra, excluir_compra

# Configuração inicial
conn, cursor = conectar()
st.set_page_config(page_title="Controle de Gastos", layout="wide")
st.title("💳 Controle de Gastos Compartilhados")

# Limites de gasto
LIMITE_VOCE = 2000.00
LIMITE_ESPOSA = 1500.00

# Carregar dados (sem cache para refletir atualizações em tempo real)
def carregar_compras():
    return listar_compras(cursor)

dados = carregar_compras()
df = pd.DataFrame(dados, columns=["ID", "Data", "Responsável", "Cartão", "Categoria", "Descrição", "Valor"])

# Formulário de nova compra - ANTES de ações que causam rerun
with st.expander("➕ Adicionar Nova Compra"):
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

# Filtros
with st.sidebar:
    st.header("🔍 Filtros")
    filtro_responsavel = st.selectbox("Responsável", ["", "Você", "Esposa"])
    filtro_cartao = st.selectbox("Cartão", ["", "Inter", "Itaú", "Nubank"])
    filtro_categoria = st.text_input("Categoria")
    filtro_descricao = st.text_input("Descrição")

# Aplicar filtros
df_filtrado = df.copy()
if filtro_responsavel:
    df_filtrado = df_filtrado[df_filtrado["Responsável"] == filtro_responsavel]
if filtro_cartao:
    df_filtrado = df_filtrado[df_filtrado["Cartão"] == filtro_cartao]
if filtro_categoria:
    df_filtrado = df_filtrado[df_filtrado["Categoria"].str.contains(filtro_categoria, case=False)]
if filtro_descricao:
    df_filtrado = df_filtrado[df_filtrado["Descrição"].str.contains(filtro_descricao, case=False)]

# Resumo de gastos
total_voce = df_filtrado[df_filtrado["Responsável"] == "Você"]["Valor"].sum()
total_esposa = df_filtrado[df_filtrado["Responsável"] == "Esposa"]["Valor"].sum()
restante_voce = LIMITE_VOCE - total_voce
restante_esposa = LIMITE_ESPOSA - total_esposa

st.markdown(f"""
### 💰 Resumo de Gastos
- **Você:** R$ {total_voce:.2f} / R$ {LIMITE_VOCE:.2f} (Restante: R$ {restante_voce:.2f})
- **Esposa:** R$ {total_esposa:.2f} / R$ {LIMITE_ESPOSA:.2f} (Restante: R$ {restante_esposa:.2f})
""")

# Exportação
st.download_button("⬇️ Exportar CSV", df_filtrado.to_csv(index=False), file_name="gastos.csv", mime="text/csv")

# Exportar Excel com BytesIO
excel_buffer = BytesIO()
df_filtrado.to_excel(excel_buffer, index=False, engine="openpyxl")
excel_buffer.seek(0)
st.download_button("⬇️ Exportar Excel", excel_buffer, file_name="gastos.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Lista com edição e exclusão
st.subheader("📋 Lista de Compras")
for _, row in df_filtrado.iterrows():
    with st.expander(f"{row['Data']} - {row['Descrição']} (R$ {row['Valor']:.2f})", expanded=False):
        st.markdown(f"**Responsável:** {row['Responsável']} | **Cartão:** {row['Cartão']} | **Categoria:** {row['Categoria']}")

        col1, col2 = st.columns([1, 1])

        # Exclusão com confirmação
        with col1:
            if st.button("🗑️ Excluir", key=f"del_{row['ID']}"):
                if st.checkbox(f"Confirmar exclusão de '{row['Descrição']}'?", key=f"conf_{row['ID']}"):
                    excluir_compra(cursor, conn, row["ID"])
                    st.success("Compra excluída com sucesso.")
                    st.experimental_rerun()

        # Edição de linha
        with col2:
            with st.form(f"edit_form_{row['ID']}"):
                nova_data = st.date_input("Data", pd.to_datetime(row["Data"]), key=f"data_{row['ID']}")
                novo_resp = st.selectbox("Responsável", ["Você", "Esposa"], index=["Você", "Esposa"].index(row["Responsável"]), key=f"resp_{row['ID']}")
                novo_cartao = st.selectbox("Cartão", ["Inter", "Itaú", "Nubank"], index=["Inter", "Itaú", "Nubank"].index(row["Cartão"]), key=f"cartao_{row['ID']}")
                nova_categoria = st.text_input("Categoria", row["Categoria"], key=f"cat_{row['ID']}")
                nova_desc = st.text_input("Descrição", row["Descrição"], key=f"desc_{row['ID']}")
                novo_valor = st.number_input("Valor (R$)", value=float(row["Valor"]), step=0.01, key=f"valor_{row['ID']}")
                salvar = st.form_submit_button("Salvar alterações")
                if salvar:
                    excluir_compra(cursor, conn, row["ID"])  # sobrescreve
                    adicionar_compra(cursor, conn, (str(nova_data), novo_resp, novo_cartao, nova_categoria, nova_desc, novo_valor))
                    st.success("Compra atualizada com sucesso!")
                    st.experimental_rerun()

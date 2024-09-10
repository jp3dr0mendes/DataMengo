import os

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from dotenv import load_dotenv

import datetime
from dateutil import relativedelta

import streamlit as st

load_dotenv()

try:

    df_brasileiro_cards = pd.read_csv(os.getenv('BRASILEIRO_CARTOES'))
    df_brasileiro_full = pd.read_csv(os.getenv('BRASILEIRO_FULL')) # PARTIDAS
    df_brasileiro_stats = pd.read_csv(os.getenv('BRASILEIRO_ESTATISTICAS'))
    df_brasileiro_gols = pd.read_csv(os.getenv('BRASILEIRO_GOLS'))

except:
    raise FileExistsError('Could not find database file')

df_fla_stats = df_brasileiro_stats.query("clube == 'Flamengo'")
df_fla_gols = df_brasileiro_gols.query("clube == 'Flamengo'")
df_fla_cards = df_brasileiro_cards.query("clube == 'Flamengo'")
df_fla_jogos = df_brasileiro_full.query("mandante == 'Flamengo' or visitante == 'Flamengo'")

#PEGANDO UNIDO AS ESTATÍSTICAS COM OS JOGOS E REMOVENDO DADOS COM CAMPOS VAZIOS
df_fla_jogos = df_fla_jogos.rename(columns={'ID':'partida_id'})
df_jogos_stats = pd.merge(df_fla_jogos, df_fla_stats, how = "left", on="partida_id")


list_vencedor = []
list_result = []
list_tecnico = []

for i in df_jogos_stats.dropna().itertuples():

    if i.mandante_Placar == i.visitante_Placar:
        list_vencedor.append('Empate')
        list_result.append('Empate')
        
        if i.mandante == 'Flamengo':
            list_tecnico.append(i.tecnico_mandante)
        else:
            list_tecnico.append(i.tecnico_visitante)

    elif i.mandante_Placar > i.visitante_Placar:

        list_vencedor.append(i.mandante)

        if i.mandante == 'Flamengo':
            list_result.append('Vitoria')
        else:
            list_result.append('Derrota')

        if i.mandante == 'Flamengo':
            list_tecnico.append(i.tecnico_mandante)
        else:
            list_tecnico.append(i.tecnico_visitante)

    else:
        list_vencedor.append(i.visitante)

        if i.visitante == 'Flamengo':
            list_result.append('Vitoria')
        else:
            list_result.append('Derrota')

        if i.mandante == 'Flamengo':
            list_tecnico.append(i.tecnico_mandante)
        else:
            list_tecnico.append(i.tecnico_visitante)

print(len(list_result), len(list_vencedor), len(df_jogos_stats), len(list_tecnico))

df_jogos_stats = (
                    df_jogos_stats
                    .dropna()
                    .drop(['rodata_y'], axis = 1)
                    .rename(columns = {'rodata_x': 'rodata'})
                    .assign(resultado = list_result)
                    .assign(vencedor = list_vencedor)
                    .assign(tecnico = list_tecnico)
                )

# TRAZENDO OS CAMPOS DE INTERESSE
df_fla_placar = df_jogos_stats[['partida_id', 'data','mandante','visitante','tecnico_visitante', 'mandante_Placar','visitante_Placar','resultado','vencedor','tecnico','arena','formacao_mandante', 'formacao_visitante']]

# ADICINANDO COLUNA PARA FAZER O HISTÓRICO ANUAL

df_fla_placar = (
    df_fla_placar
    .assign(ano = pd.to_datetime(df_fla_placar['data']).dt.year)
)

# PEGANDO APENAS AS VITORIAS

df_fla_vitorias = df_fla_placar[df_fla_placar['resultado'] == 'Vitoria']
df_fla_derrotas = df_fla_placar[df_fla_placar['resultado'] == 'Derrota']
df_fla_empates = df_fla_placar[df_fla_placar['resultado'] == 'Empate']

df_fla_overview_ano = pd.DataFrame({
    'ano': df_fla_placar['ano'].drop_duplicates().values.tolist(),
    'vitorias': [x[0] for x in df_fla_vitorias[['ano','resultado']].groupby('ano').count().values.tolist()],
    'derrotas': [x[0] for x in df_fla_derrotas[['ano','resultado']].groupby('ano').count().values.tolist()],
    'empates': [x[0] for x in df_fla_empates[['ano','resultado']].groupby('ano').count().values.tolist()]
})

fig, ax = plt.subplots()

sns.lineplot(x='ano', y = 'derrotas', data = df_fla_overview_ano, ax = ax)
ax.set_title('Vitorias Por Ano')

st.title('Hello Mãe!')
st.pyplot(fig)
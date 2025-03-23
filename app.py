# -*- coding: utf-8 -*-
"""
Created on Sun Mar 23 20:34:25 2025

@author: wag08
"""

import yfinance as yf
import pandas as pd
import streamlit as st

# Tickers padrão
DEFAULT_TICKERS = [
    "BBAS3.SA", "BCIA11.SA", "BOVA11.SA", "BTLG11.SA", "CMIG4.SA", 
    "CSMG3.SA", "DIVO11.SA", "HASH11.SA", "HCTR11.SA", "HGBS11.SA"
]

# Função para calcular médias móveis
def calculate_moving_averages(data, short_window=9, long_window=21, ma50_window=50, ma200_window=200):
    data['MA_9'] = data['Close'].rolling(window=short_window, min_periods=1).mean()
    data['MA_21'] = data['Close'].rolling(window=long_window, min_periods=1).mean()
    data['MA_50'] = data['Close'].rolling(window=ma50_window, min_periods=1).mean()
    data['MA_200'] = data['Close'].rolling(window=ma200_window, min_periods=1).mean()
    return data

# Função para gerar recomendações com base nas médias móveis
def generate_recommendation(data):
    last_row = data.iloc[-1]
    
    # Recomendação para MA de 9 e 21
    if last_row['MA_9'] > last_row['MA_21']:
        ma_9_21_rec = "🟢 Compra (MA 9 > MA 21)"
    else:
        ma_9_21_rec = "🔴 Venda (MA 9 < MA 21)"
    
    # Recomendação para MA de 50 e 200
    if last_row['MA_50'] > last_row['MA_200']:
        ma_50_200_rec = "🟢 Compra (MA 50 > MA 200)"
    else:
        ma_50_200_rec = "🔴 Venda (MA 50 < MA 200)"
    
    return ma_9_21_rec, ma_50_200_rec

# Função principal para analisar um ticker
def analyze_ticker(ticker):
    try:
        # Baixar dados históricos
        data = yf.download(ticker, period="1y")
        if data.empty:
            return f"Erro: Dados insuficientes para o ticker {ticker}."
        
        # Calcular médias móveis
        data = calculate_moving_averages(data)
        
        # Gerar recomendações
        ma_9_21_rec, ma_50_200_rec = generate_recommendation(data)
        
        # Retornar resultados
        return {
            "Ticker": ticker,
            "MA 9 > 21": ma_9_21_rec,
            "MA 50 > 200": ma_50_200_rec,
            "Preço Atual": round(data['Close'].iloc[-1], 2),
            "MA 9": round(data['MA_9'].iloc[-1], 2),
            "MA 21": round(data['MA_21'].iloc[-1], 2),
            "MA 50": round(data['MA_50'].iloc[-1], 2),
            "MA 200": round(data['MA_200'].iloc[-1], 2),
        }
    except Exception as e:
        return f"Erro ao analisar o ticker {ticker}: {str(e)}"

# Interface do Streamlit
st.title("Análise de Tickers com Médias Móveis")

# Entrada de tickers
tickers_input = st.text_input(
    "Digite os tickers separados por vírgula (ou use os padrão):", 
    ", ".join(DEFAULT_TICKERS)
)
tickers = [t.strip() for t in tickers_input.split(",")] if tickers_input else DEFAULT_TICKERS

# Botão para analisar
if st.button("Analisar"):
    results = []
    for ticker in tickers:
        result = analyze_ticker(ticker)
        results.append(result)
    
    # Exibir resultados
    for res in results:
        if isinstance(res, dict):
            st.write(f"📊 **{res['Ticker']}**")
            st.write(f"💰 **Preço Atual**: {res['Preço Atual']}")
            st.write(f"📈 **MA 9**: {res['MA 9']}")
            st.write(f"📈 **MA 21**: {res['MA 21']}")
            st.write(f"📈 **MA 50**: {res['MA 50']}")
            st.write(f"📈 **MA 200**: {res['MA 200']}")
            st.write(f"✅ **Recomendação (MA 9 vs 21)**: {res['MA 9 > 21']}")
            st.write(f"✅ **Recomendação (MA 50 vs 200)**: {res['MA 50 > 200']}")
            st.write("---")
        else:
            st.error(res)  # Exibe mensagens de erro
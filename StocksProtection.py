# -*- coding: utf-8 -*-
"""
Created on Sun Mar  9 13:23:54 2025

"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pandas_ta as ta  # Biblioteca para indicadores técnicos

# Função para calcular indicadores e gerar recomendação
def analyze_stock(ticker):
    # Baixar dados históricos
    stock = yf.Ticker(ticker)
    history = stock.history(period="6mo")  # Últimos 6 meses de dados

    # Calcular indicadores
    history['MA_9'] = history['Close'].rolling(window=9).mean()
    history['MA_20'] = history['Close'].rolling(window=20).mean()
    history['MA_50'] = history['Close'].rolling(window=50).mean()
    history['MA_200'] = history['Close'].rolling(window=200).mean()
    history['MACD'] = ta.macd(history['Close'])['MACD_12_26_9']
    history['RSI'] = ta.rsi(history['Close'])
    history['OBV'] = ta.obv(history['Close'], history['Volume'])

    # Tendência diária e semanal
    daily_trend = "alta" if history['Close'][-1] > history['Close'][-2] else "baixa"
    weekly_trend = "alta" if history['Close'][-1] > history['Close'][-5] else "baixa"

    # Variação de volume diário e semanal
    daily_volume_change = (history['Volume'][-1] - history['Volume'][-2]) / history['Volume'][-2] * 100
    weekly_volume_change = (history['Volume'][-1] - history['Volume'][-5]) / history['Volume'][-5] * 100

    # Recomendação baseada em regras simples
    recommendation = "neutral"
    if (
        history['MA_9'][-1] > history['MA_20'][-1] and  # Média de 9 dias > Média de 20 dias
        history['RSI'][-1] < 70 and  # RSI não está sobrecomprado
        history['MACD'][-1] > 0  # MACD positivo
    ):
        recommendation = "compra"
    elif (
        history['MA_9'][-1] < history['MA_20'][-1] and  # Média de 9 dias < Média de 20 dias
        history['RSI'][-1] > 30 and  # RSI não está sobrevendido
        history['MACD'][-1] < 0  # MACD negativo
    ):
        recommendation = "venda"

    # Retornar resultados
    return {
        "ticker": ticker,
        "daily_trend": daily_trend,
        "weekly_trend": weekly_trend,
        "daily_volume_change": daily_volume_change,
        "weekly_volume_change": weekly_volume_change,
        "MA_9": history['MA_9'][-1],
        "MA_20": history['MA_20'][-1],
        "MA_50": history['MA_50'][-1],
        "MA_200": history['MA_200'][-1],
        "MACD": history['MACD'][-1],
        "RSI": history['RSI'][-1],
        "OBV": history['OBV'][-1],
        "recommendation": recommendation,
    }

# Interface do Streamlit
st.title("Analisador de Investimentos")
st.write("Selecione o tipo de investimento e insira os tickers:")

# Seleção do tipo de investimento
investment_type = st.selectbox(
    "Tipo de Investimento",
    ["Ações Nacionais", "Ações Internacionais", "Fundos Imobiliários Brasileiros"]
)

# Input de tickers
tickers_input = st.text_input(
    "Insira os tickers separados por vírgula (ex: PETR4.SA, VALE3.SA, AAPL):"
)

# Processar tickers
if tickers_input:
    tickers = [t.strip() for t in tickers_input.split(",")]
    if investment_type == "Ações Nacionais" or investment_type == "Fundos Imobiliários Brasileiros":
        tickers = [t + ".SA" if not t.endswith(".SA") else t for t in tickers]

    # Analisar cada ticker
    results = []
    for ticker in tickers:
        try:
            result = analyze_stock(ticker)
            results.append(result)
        except Exception as e:
            st.error(f"Erro ao analisar {ticker}: {e}")

    # Exibir resultados
    if results:
        st.write("### Resultados da Análise")
        for result in results:
            st.write(f"#### Ticker: {result['ticker']}")
            st.write(f"- Tendência Diária: {result['daily_trend']}")
            st.write(f"- Tendência Semanal: {result['weekly_trend']}")
            st.write(f"- Variação de Volume Diário: {result['daily_volume_change']:.2f}%")
            st.write(f"- Variação de Volume Semanal: {result['weekly_volume_change']:.2f}%")
            st.write(f"- Média Móvel (9 dias): {result['MA_9']:.2f}")
            st.write(f"- Média Móvel (20 dias): {result['MA_20']:.2f}")
            st.write(f"- Média Móvel (50 dias): {result['MA_50']:.2f}")
            st.write(f"- Média Móvel (200 dias): {result['MA_200']:.2f}")
            st.write(f"- MACD: {result['MACD']:.2f}")
            st.write(f"- RSI: {result['RSI']:.2f}")
            st.write(f"- OBV: {result['OBV']:.2f}")
            st.write(f"- Recomendação: **{result['recommendation'].upper()}**")
            st.write("---")
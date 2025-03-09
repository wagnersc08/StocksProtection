# -*- coding: utf-8 -*-
"""
Created on Sun Mar  9 13:23:54 2025
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import subprocess
import sys
import pandas_ta as ta  # Biblioteca para indicadores técnicos


# Função para gerar recomendações individuais para cada indicador
def analyze_indicator(indicator, value, history):
    if indicator == "MA_9_20":
        return "Compra" if value["MA_9"] > value["MA_20"] else "Venda"
    elif indicator == "MA_50_200":
        return "Compra" if value["MA_50"] > value["MA_200"] else "Venda"
    elif indicator == "MACD":
        return "Compra" if value > 0 else "Venda"
    elif indicator == "RSI":
        if value < 30:
            return "Compra"
        elif value > 70:
            return "Venda"
        else:
            return "Neutro"
    elif indicator == "OBV":
        return "Compra" if value > history['OBV'][-2] else "Venda"
    elif indicator == "MFI":
        if value < 20:
            return "Compra"
        elif value > 80:
            return "Venda"
        else:
            return "Neutro"
    elif indicator == "daily_trend":
        return "Compra" if value == "alta" else "Venda"
    elif indicator == "weekly_trend":
        return "Compra" if value == "alta" else "Venda"
    else:
        return "Neutro"

# Função para calcular indicadores e gerar recomendação
def analyze_stock(ticker):
    # Baixar dados históricos
    stock = yf.Ticker(ticker)
    history = stock.history(period="6mo")  # Últimos 6 meses de dados

    # Verificar se há dados suficientes
    if history.empty or len(history) < 20:
        raise ValueError(f"Dados insuficientes para o ticker {ticker}.")

    # Calcular indicadores
    history['MA_9'] = history['Close'].rolling(window=9).mean()
    history['MA_20'] = history['Close'].rolling(window=20).mean()
    history['MA_50'] = history['Close'].rolling(window=50).mean()
    history['MA_200'] = history['Close'].rolling(window=200).mean()
    history['MACD'] = ta.macd(history['Close'])['MACD_12_26_9']
    history['RSI'] = ta.rsi(history['Close'])
    history['OBV'] = ta.obv(history['Close'], history['Volume'])
    history['MFI'] = ta.mfi(history['High'], history['Low'], history['Close'], history['Volume'], length=14)

    # Tendência diária e semanal
    daily_trend = "alta" if history['Close'][-1] > history['Close'][-2] else "baixa"
    weekly_trend = "alta" if history['Close'][-1] > history['Close'][-5] else "baixa"

    # Variação de volume diário e semanal
    daily_volume_change = (history['Volume'][-1] - history['Volume'][-2]) / history['Volume'][-2] * 100
    weekly_volume_change = (history['Volume'][-1] - history['Volume'][-5]) / history['Volume'][-5] * 100

    # Gerar recomendações para cada indicador
    recommendations = {
        "MA_9_20": analyze_indicator("MA_9_20", {"MA_9": history['MA_9'][-1], "MA_20": history['MA_20'][-1]}, history),
        "MA_50_200": analyze_indicator("MA_50_200", {"MA_50": history['MA_50'][-1], "MA_200": history['MA_200'][-1]}, history),
        "MACD": analyze_indicator("MACD", history['MACD'][-1], history),
        "RSI": analyze_indicator("RSI", history['RSI'][-1], history),
        "OBV": analyze_indicator("OBV", history['OBV'][-1], history),
        "MFI": analyze_indicator("MFI", history['MFI'][-1], history),
        "daily_trend": analyze_indicator("daily_trend", daily_trend, history),
        "weekly_trend": analyze_indicator("weekly_trend", weekly_trend, history),
    }

    # Conclusão geral baseada nas recomendações individuais
    buy_count = sum(1 for rec in recommendations.values() if rec == "Compra")
    sell_count = sum(1 for rec in recommendations.values() if rec == "Venda")
    if buy_count > sell_count:
        general_recommendation = "Compra"
    elif sell_count > buy_count:
        general_recommendation = "Venda"
    else:
        general_recommendation = "Neutro"

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
        "MFI": history['MFI'][-1],
        "recommendations": recommendations,
        "general_recommendation": general_recommendation,
    }

# Função para aplicar cores e figurinhas às células da tabela
def color_cell(value):
    if value == "Compra":
        return "background-color: green; color: white;", "🟢"
    elif value == "Venda":
        return "background-color: red; color: white;", "🔴"
    else:
        return "background-color: gray; color: white;", "⚪"

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
    "Insira os tickers separados por vírgula (ex: PETR4, VALE3, AAPL):"
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

    # Exibir resultados em uma tabela
    if results:
        for result in results:
            st.write(f"### Ticker: {result['ticker']}")
            st.write("---")

            # Criar DataFrame para exibir os resultados
            data = {
                "Indicador": ["MA 9/20", "MA 50/200", "MACD", "RSI", "OBV", "MFI", "Tendência Diária", "Tendência Semanal", "Conclusão Geral"],
                "Recomendação": [
                    result['recommendations']["MA_9_20"],
                    result['recommendations']["MA_50_200"],
                    result['recommendations']["MACD"],
                    result['recommendations']["RSI"],
                    result['recommendations']["OBV"],
                    result['recommendations']["MFI"],
                    result['recommendations']["daily_trend"],
                    result['recommendations']["weekly_trend"],
                    result['general_recommendation'],
                ],
            }
            df = pd.DataFrame(data)

            # Aplicar cores e figurinhas
            styled_df = df.style.apply(lambda x: [color_cell(v)[0] for v in x], subset=["Recomendação"])
            df["Figurinha"] = df["Recomendação"].apply(lambda x: color_cell(x)[1])

            # Exibir tabela
            st.dataframe(styled_df)
            st.write("---")

            # Destacar conclusão geral
            if result['general_recommendation'] == "Compra":
                st.success(f"Conclusão Geral: {result['general_recommendation']} 🟢")
            elif result['general_recommendation'] == "Venda":
                st.error(f"Conclusão Geral: {result['general_recommendation']} 🔴")
            else:
                st.warning(f"Conclusão Geral: {result['general_recommendation']} ⚪")
            st.write("---")
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 23 20:34:25 2025

@author: wag08
"""

import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import streamlit as st

# Configurações iniciais
np.NaN = np.nan
DEFAULT_TICKERS = [
    "BBAS3.SA", "BCIA11.SA", "BOVA11.SA", "BTLG11.SA", "CMIG4.SA"]

# Função para gerar recomendações individuais para cada indicador
def analyze_indicator(indicator, value, history):
    if indicator == "MA_9_20":
        return "🟢 Compra" if value["MA_9"] > value["MA_20"] else "🔴 Venda"
    elif indicator == "MA_50_200":
        return "🟢 Compra" if value["MA_50"] > value["MA_200"] else "🔴 Venda"
    elif indicator == "MACD":
        return "🟢 Compra" if value > 0 else "🔴 Venda"
    elif indicator == "RSI":
        if value < 30:
            return "🟢 Compra"
        elif value > 70:
            return "🔴 Venda"
        else:
            return "⚪ Neutro"
    elif indicator == "OBV":
        return "🟢 Compra" if value > history['OBV'].iloc[-2] else "🔴 Venda"
    elif indicator == "MFI":
        if value < 20:
            return "🟢 Compra"
        elif value > 80:
            return "🔴 Venda"
        else:
            return "⚪ Neutro"
    elif indicator == "DMI":
        return "🟢 Compra" if value["DI+"] > value["DI-"] else "🔴 Venda"
    else:
        return "⚪ Neutro"

# Função para determinar a tendência (alta ou baixa)
def determine_trend(history):
    if history['Close'].iloc[-1] > history['MA_50'].iloc[-1]:
        return "🟢 Tendência de Alta"
    else:
        return "🔴 Tendência de Baixa"

# Função para verificar cruzamento de suporte/resistência
def check_support_resistance(history):
    recent_high = history['High'].rolling(window=50).max().iloc[-1]
    recent_low = history['Low'].rolling(window=50).min().iloc[-1]
    close_price = history['Close'].iloc[-1]

    if close_price > recent_high:
        return f"🟢 Cruzou Resistência: {round(recent_high, 2)}"
    elif close_price < recent_low:
        return f"🔴 Cruzou Suporte: {round(recent_low, 2)}"
    else:
        return "⚪ Sem cruzamento importante"

# Função para gerar conclusão geral
def generate_conclusion(recommendations):
    buy_count = sum(1 for key, value in recommendations.items() if isinstance(value, tuple) and "🟢 Compra" in value)
    sell_count = sum(1 for key, value in recommendations.items() if isinstance(value, tuple) and "🔴 Venda" in value)
    neutral_count = sum(1 for key, value in recommendations.items() if isinstance(value, tuple) and "⚪ Neutro" in value)

    if buy_count > sell_count and buy_count > neutral_count:
        return "🟢 Conclusão Geral: Compra"
    elif sell_count > buy_count and sell_count > neutral_count:
        return "🔴 Conclusão Geral: Venda"
    else:
        return "⚪ Conclusão Geral: Neutro"

# Função para calcular indicadores e gerar recomendação
def analyze_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period="1y")

        if history.empty or len(history) < 20:
            raise ValueError(f"Dados insuficientes para o ticker {ticker}.")

        required_columns = ['High', 'Low', 'Close', 'Volume']
        if not all(col in history.columns for col in required_columns):
            raise ValueError(f"Colunas necessárias não encontradas no histórico: {required_columns}")

        if history[required_columns].isnull().any().any():
            raise ValueError(f"Dados históricos contêm valores NaN para o ticker {ticker}.")

        history['MA_9'] = ta.sma(history['Close'], length=9)
        history['MA_20'] = ta.sma(history['Close'], length=20)
        history['MA_50'] = ta.sma(history['Close'], length=50)
        history['MA_200'] = ta.sma(history['Close'], length=200)
        history['MACD'] = ta.macd(history['Close'])['MACD_12_26_9']
        history['RSI'] = ta.rsi(history['Close'], length=14)
        history['OBV'] = ta.obv(history['Close'], history['Volume'])
        history['MFI'] = ta.mfi(history['High'], history['Low'], history['Close'], history['Volume'], length=14)
        dmi = ta.adx(history['High'], history['Low'], history['Close'], length=14)
        history['DI+'] = dmi['DMP_14']
        history['DI-'] = dmi['DMN_14']

        recommendations = {
            "MA_9_20": (round(history['MA_9'].iloc[-1], 2), round(history['MA_20'].iloc[-1], 2), analyze_indicator("MA_9_20", {"MA_9": history['MA_9'].iloc[-1], "MA_20": history['MA_20'].iloc[-1]}, history)),
            "MA_50_200": (round(history['MA_50'].iloc[-1], 2), round(history['MA_200'].iloc[-1], 2), analyze_indicator("MA_50_200", {"MA_50": history['MA_50'].iloc[-1], "MA_200": history['MA_200'].iloc[-1]}, history)),
            "MACD": (round(history['MACD'].iloc[-1], 2), analyze_indicator("MACD", history['MACD'].iloc[-1], history)),
            "RSI": (round(history['RSI'].iloc[-1], 2), analyze_indicator("RSI", history['RSI'].iloc[-1], history)),
            "OBV": (round(history['OBV'].iloc[-1], 2), analyze_indicator("OBV", history['OBV'].iloc[-1], history)),
            "MFI": (round(history['MFI'].iloc[-1], 2), analyze_indicator("MFI", history['MFI'].iloc[-1], history)),
            "DMI": (round(history['DI+'].iloc[-1], 2), round(history['DI-'].iloc[-1], 2), analyze_indicator("DMI", {"DI+": history['DI+'].iloc[-1], "DI-": history['DI-'].iloc[-1]}, history)),
            "Tendência": determine_trend(history),
            "Suporte/Resistência": check_support_resistance(history),
        }

        conclusion = generate_conclusion(recommendations)

        return {"ticker": ticker, "recommendations": recommendations, "conclusion": conclusion}
    except Exception as e:
        raise ValueError(f"Erro ao analisar o ticker {ticker}: {str(e)}")

# Interface do Streamlit
st.title("Análise de Ações")

tickers = st.text_input("Digite os tickers separados por vírgula", ", ".join(DEFAULT_TICKERS))
tickers = [t.strip() for t in tickers.split(",")] if tickers else DEFAULT_TICKERS

if st.button("Analisar"):
    results = []
    for ticker in tickers:
        try:
            result = analyze_stock(ticker)
            results.append(result)
        except Exception as e:
            st.error(f"Erro ao analisar {ticker}: {e}")

    if results:
        for res in results:
            st.write(f"📊 **{res['ticker']}**:")
            for key, values in res["recommendations"].items():
                if isinstance(values, str):
                    st.write(f"• **{key}**: {values}")
                else:
                    st.write(f"• **{key}**: valor: {values[0]}, recomendação: {values[-1]}")
            st.write(f"**{res['conclusion']}**")
            st.write("---")
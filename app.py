# -*- coding: utf-8 -*-
import yfinance as yf
import pandas as pd
import streamlit as st

# Tickers padrão
DEFAULT_TICKERS = [
    "BBAS3.SA", "BCIA11.SA", "BOVA11.SA", "BTLG11.SA", "CMIG4.SA", 
    "DIVO11.SA", "HASH11.SA", "HCTR11.SA", "HGBS11.SA",'ISAE4.SA','ITSA4.SA',
    'ITUB4.SA','KFOF11.SA','KORE11.SA','LEVE3.SA','PETR4.SA',
    'RBRF11.SA','SAPR4.SA','SMAL11.SA','TRXF11.SA','VALE3.SA','VISC11.SA','WEGE3.SA','XFIX11.SA','XPML11.SA',   
    'VOO','TLT','SCHD','BRK-B','XOP','CIBR','QQQ','DRIV','ICLN',
    'MSFT','NKE','ADBE','AMAT','CRWD','DLR','ISRG','PATH','V','BTC-USD','ETH-USD'
]

# Função para calcular médias móveis
def calculate_moving_averages(data, windows=[9, 21, 50, 200]):
    for window in windows:
        column_name = f"MA_{window}"
        data[column_name] = data['Close'].rolling(window=window, min_periods=1).mean()
    return data

# Função para calcular RSI manualmente
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=window, min_periods=window).mean()
    avg_loss = loss.rolling(window=window, min_periods=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    data['RSI'] = rsi
    return data

# Função para gerar recomendações
def generate_recommendation(data):
    last_row = data.iloc[-1]
    
    # Médias móveis
    ma_9_21_rec = "🟢 Compra (MA 9 > MA 21)" if last_row['MA_9'] > last_row['MA_21'] else "🔴 Venda (MA 9 < MA 21)"
    ma_50_200_rec = "🟢 Compra (MA 50 > MA 200)" if last_row['MA_50'] > last_row['MA_200'] else "🔴 Venda (MA 50 < MA 200)"
    
    # RSI
    if last_row['RSI'] < 30:
        rsi_rec = "🟢 RSI < 30: sobrevenda (compra)"
    elif last_row['RSI'] > 70:
        rsi_rec = "🔴 RSI > 70: sobrecompra (evitar)"
    else:
        rsi_rec = "🟡 RSI neutro"

    return {
        "MA 9 > 21": ma_9_21_rec,
        "MA 50 > 200": ma_50_200_rec,
        "RSI": round(last_row['RSI'], 2),
        "Recomendação RSI": rsi_rec,
    }

# Interface do Streamlit
st.title("Análise Técnica de Tickers com Médias Móveis e RSI")

# Entrada de tickers
tickers_input = st.text_input(
    "Digite os tickers separados por vírgula (ou use os padrão):", 
    ", ".join(DEFAULT_TICKERS)
)
tickers = [t.strip() for t in tickers_input.split(",")] if tickers_input else DEFAULT_TICKERS

if st.button("Analisar"):
    results = []
    for ticker in tickers:
        try:
            data = yf.download(ticker, period="1y")
            data = data.droplevel(level=1, axis=1)
            
            if data.empty:
                st.error(f"Não foi possível baixar dados para o ticker {ticker}.")
                continue
            
            # Cálculos
            data = calculate_moving_averages(data)
            data = calculate_rsi(data)
            recommendations = generate_recommendation(data)

            results.append({
                "Ticker": ticker,
                "Preço Atual": round(data['Close'].iloc[-1], 2),
                "MA 9": round(data['MA_9'].iloc[-1], 2),
                "MA 21": round(data['MA_21'].iloc[-1], 2),
                "MA 50": round(data['MA_50'].iloc[-1], 2),
                "MA 200": round(data['MA_200'].iloc[-1], 2),
                **recommendations,
            })
        except Exception as e:
            st.error(f"Erro ao analisar o ticker {ticker}: {str(e)}")
    
    if results:
        st.write("### Resultados da Análise")
        for res in results:
            st.write(f"📊 **{res['Ticker']}**")
            st.write(f"💰 **Preço Atual**: {res['Preço Atual']}")
            st.write(f"📈 **MA 9**: {res['MA 9']}")
            st.write(f"📈 **MA 21**: {res['MA 21']}")
            st.write(f"📈 **MA 50**: {res['MA 50']}")
            st.write(f"📈 **MA 200**: {res['MA 200']}")
            st.write(f"✅ **Recomendação (MA 9 vs 21)**: {res['MA 9 > 21']}")
            st.write(f"✅ **Recomendação (MA 50 vs 200)**: {res['MA 50 > 200']}")
            st.write(f"📊 **RSI (14)**: {res['RSI']}")
            st.write(f"📌 **Recomendação RSI**: {res['Recomendação RSI']}")
            st.write("---")

# -*- coding: utf-8 -*-
import yfinance as yf
import pandas as pd
import streamlit as st

# Tickers padrão
DEFAULT_TICKERS = [
    "BBAS3.SA", "BCIA11.SA", "BOVA11.SA", "BTLG11.SA", "CMIG4.SA", 
    "CSMG3.SA", "DIVO11.SA", "HASH11.SA", "HCTR11.SA", "HGBS11.SA",
    'TRPL4.SA','ITSA4.SA','ITUB4.SA','KFOF11.SA','LEVE3.SA','PETR4.SA',
    'RBRF11.SA','SAPR4.SA','SMAL11.SA','TRXF11.SA','VALE3.SA','VISC11.SA','XFIX11.SA','XPML11.SA',   
    'VOO','TLT','SCHD','BRK-B','XOP','CIBR','QQQ','DRIV','ICLN',
    'MSFT','NKE','ADBE','AMAT','ISRG','BTC-USDT','ETH-USDT'
]

# Função para calcular médias móveis manualmente
def calculate_moving_averages(data, windows=[9, 21, 50, 200]):
    try:
        
        # Calcula as médias móveis para cada período
        for window in windows:
            column_name = f"MA_{window}"
            data[column_name] = data['Close'].rolling(window=window, min_periods=1).mean()
        
        return data
    except Exception as e:
        raise ValueError(f"Erro ao calcular médias móveis: {str(e)}")

# Função para gerar recomendações com base nas médias móveis
def generate_recommendation(data):
    """
    Gera recomendações de compra/venda com base nas médias móveis.
    
    Parâmetros:
        data (pd.DataFrame): DataFrame contendo as colunas de médias móveis.
    
    Retorna:
        dict: Dicionário com as recomendações.
    """
    try:
        last_row = data.iloc[-1]  # Pega a última linha do DataFrame
        
        # Recomendação para MA de 9 e 21
        if last_row['MA_9'] > last_row['MA_21']:
            ma_9_21_rec = "🟢 Compra (MA 9 > MA 21)"
        else:
            ma_9_21_rec = "🔴 Venda (MA 9 < MA 21)"
        
        # Recomendação para MA de 50 e 200
        if last_row['MA_50']> last_row['MA_200']:
            ma_50_200_rec = "🟢 Compra (MA 50 > MA 200)"
        else:
            ma_50_200_rec = "🔴 Venda (MA 50 < MA 200)"
        
        return {
            "MA 9 > 21": ma_9_21_rec,
            "MA 50 > 200": ma_50_200_rec,
        }
    except Exception as e:
        raise ValueError(f"Erro ao gerar recomendações: {str(e)}")

# Interface do Streamlit
st.title("Análise de Tickers com Médias Móveis")

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
            # Baixar dados históricos
            data = yf.download(ticker, period="1y")
            data = data.droplevel(level=1, axis=1)
            
            if data.empty:
                st.error(f"Não foi possível baixar dados para o ticker {ticker}.")
                continue
            
            # Calcular médias móveis
            data = calculate_moving_averages(data)
            
            # Gerar recomendações
            recommendations = generate_recommendation(data)
            
            # Retornar resultados
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
    
    # Exibir resultados
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
            st.write("---")
        
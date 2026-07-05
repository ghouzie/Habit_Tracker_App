import streamlit as st
import pandas as pd


df = pd.read_csv('salaryy.csv')
print(df.head())
print("Done")
st.write(df)
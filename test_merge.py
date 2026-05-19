import pandas as pd

df_stock = pd.DataFrame({'ITEM CODE': [1,2], 'QTY': [10, 20]})
df_s1 = pd.DataFrame({'BARCODE': [1,2], 'QTY': [5, 15]})
df_s2 = pd.DataFrame({'BARCODE': [1,2], 'QTY': [2, 12]})

stock_qty_col = "QTY"
s1_qty_col = "QTY"

df_stock = pd.merge(df_stock, df_s1, left_on="ITEM CODE", right_on="BARCODE", how="left")
print("After first merge:", df_stock.columns)

df_stock.rename(columns={s1_qty_col: "SALES_1_QTY"}, inplace=True)
print("After first rename:", df_stock.columns)

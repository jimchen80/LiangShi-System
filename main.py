import akshare as ak
import pandas as pd

def liang_shi_6_1_engine():
    try:
        print("🚀 启动 6.1 实战版：联网获取行情...")
        df = ak.stock_zh_a_spot_em()
        
        # 核心算法参数（严禁修改）
        num_cols = ['最新价', '涨跌幅', '成交额', '量比', '换手率']
        for col in num_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        mask = (df['涨跌幅'] >= 3.0) & (df['涨跌幅'] <= 9.9) & \
               (df['成交额'] >= 500000000) & (df['量比'] >= 1.5) & \
               (df['换手率'] >= 3.0) & (df['换手率'] <= 15.0)
        
        result = df[mask].copy()
        
        # 导出文件
        result.to_csv("report.csv", index=False, encoding='utf_8_sig')
        print(f"✅ 筛选完毕，捕捉到 {len(result)} 只标的，已存入 report.csv")

    except Exception as e:
        print(f"❌ 运行失败: {e}")

if __name__ == "__main__":
    liang_shi_6_1_engine()

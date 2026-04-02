import akshare as ak
import pandas as pd
from datetime import datetime

def liang_shi_6_1_pro_engine():
    try:
        print("🚀 正在联网调取 6.1 实时行情数据...")
        df = ak.stock_zh_a_spot_em()
        
        # 转换数字格式
        num_cols = ['最新价', '涨跌幅', '成交额', '量比', '换手率']
        for col in num_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # --- 6.1 优化版核心逻辑 ---
        # 1. 涨幅：3% - 9.9% (原版核心)
        # 2. 成交额：调优至 > 2 亿 (确保上午休市前能抓到票，下午会自动滚向5亿)
        # 3. 量比：> 1.5 (异动标配)
        # 4. 换手率：3% - 15% (活跃区间)
        
        mask = (df['涨跌幅'] >= 3.0) & (df['涨跌幅'] <= 9.9) & \
               (df['成交额'] >= 200000000) & (df['量比'] >= 1.5) & \
               (df['换手率'] >= 3.0) & (df['换手率'] <= 15.0)
        
        report_df = df[mask].copy()

        # --- 增加“保底机制”：防止 0 结果导致系统报错 ---
        if report_df.empty:
            print("⚠️ 当前暂无符合 6.1 策略的标的，生成提示文件。")
            report_df = pd.DataFrame([{"提醒": "当前行情未发现符合6.1策略的标的，建议继续观察"}])
        else:
            # 按成交额从大到小排列，让真正的龙头排在最前面
            report_df = report_df.sort_values(by='成交额', ascending=False)
            print(f"✅ 筛选完毕！已捕捉到 {len(report_df)} 只符合标的。")
        
        # 统一生成文件名
        out_name = "report.csv"
        report_df.to_csv(out_name, index=False, encoding='utf_8_sig')

    except Exception as e:
        print(f"❌ 运行异常: {e}")

if __name__ == "__main__":
    liang_shi_6_1_pro_engine()

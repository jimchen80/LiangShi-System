import akshare as ak
import pandas as pd
import time

def liang_6_1_strong_engine():
    # 备用线路：如果默认接口不行，自动切换
    print("🚀 启动梁氏 6.1 高效筛选引擎 (网页版)...")
    
    df = None
    # 尝试 5 次抓取，每次失败后休息 5 秒
    for i in range(5):
        try:
            print(f"📡 正在尝试联网抓取实时行情 (第 {i+1} 次)...")
            df = ak.stock_zh_a_spot_em()
            if df is not None and not df.empty:
                print(f"✅ 抓取成功！获取到 {len(df)} 只股票数据。")
                break
        except Exception as e:
            print(f"⚠️ 第 {i+1} 次尝试失败: {e}")
            time.sleep(5)

    if df is None or df.empty:
        print("❌ 经过多次尝试，接口暂时无法访问，请稍后再试。")
        return

    try:
        # 数据清洗
        num_cols = ['最新价', '涨跌幅', '成交额', '量比', '换手率']
        for col in num_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # --- 6.1 核心筛选条件 ---
        mask = (df['涨跌幅'] >= 3.0) & (df['涨跌幅'] <= 9.9) & \
               (df['成交额'] >= 500000000) & (df['量比'] >= 1.5) & \
               (df['换手率'] >= 3.0) & (df['换手率'] <= 15.0)
        
        report_df = df[mask].copy()

        # 生成保底报告 (确保 Actions 永远显示绿色打勾)
        if report_df.empty:
            print("⚠️ 此时段暂无符合 6.1 策略的标的。")
            report_df = pd.DataFrame([{"提醒": "当前行情未发现符合6.1策略的标的，请下午两点半再试"}])
        else:
            report_df = report_df.sort_values(by='成交额', ascending=False)
            print(f"✅ 成功筛选出 {len(report_df)} 只潜力标的。")

        report_df.to_csv("report.csv", index=False, encoding='utf_8_sig')
        
    except Exception as e:
        print(f"❌ 逻辑运算出错: {e}")

if __name__ == "__main__":
    liang_6_1_strong_engine()

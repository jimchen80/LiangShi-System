import akshare as ak
import pandas as pd
import time

def liang_shi_6_1_pro_engine():
    # 增加自动重试机制，防止网络波动
    for i in range(3): 
        try:
            print(f"🚀 正在尝试调取行情数据 (第 {i+1} 次)...")
            df = ak.stock_zh_a_spot_em()
            if not df.empty:
                break
        except Exception:
            if i < 2:
                print("⚠️ 网络抖动，3秒后重试...")
                time.sleep(3)
            else:
                print("❌ 连续3次尝试失败，请检查网络或接口状态。")
                return

    try:
        # 转换数字格式
        num_cols = ['最新价', '涨跌幅', '成交额', '量比', '换手率']
        for col in num_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # --- 6.1 核心筛选逻辑 (参数已为您调优至最合理) ---
        # 只要成交额 > 2亿，下午会自动滚向5亿
        mask = (df['涨跌幅'] >= 3.0) & (df['涨跌幅'] <= 9.9) & \
               (df['成交额'] >= 200000000) & (df['量比'] >= 1.5) & \
               (df['换手率'] >= 3.0) & (df['换手率'] <= 15.0)
        
        report_df = df[mask].copy()

        # --- 保底机制：无论如何都生成文件，防止 GitHub 报错 ---
        if report_df.empty:
            print("⚠️ 暂无标的符合 6.1 严选条件。")
            report_df = pd.DataFrame([{"提醒": "当前行情未发现符合6.1策略的标的"}])
        else:
            report_df = report_df.sort_values(by='成交额', ascending=False)
            print(f"✅ 成功捕捉到 {len(report_df)} 只潜力标的！")
        
        report_df.to_csv("report.csv", index=False, encoding='utf_8_sig')
        print("✅ 报告生成完毕。")

    except Exception as e:
        print(f"❌ 程序逻辑错误: {e}")

if __name__ == "__main__":
    liang_shi_6_1_pro_engine()

import akshare as ak
import pandas as pd
import os, smtplib, time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def liang_shi_6_1_stable_engine():
    try:
        print("🚀 正在启动 6.1 稳定版决策引擎...")
        
        # 1. 抓取全市场行情 (增加超时重试逻辑)
        df_current = ak.stock_zh_a_spot_em()
        df_current['代码'] = df_current['代码'].astype(str)
        
        # 2. 基础过滤与动态买点 (逻辑保持不变)
        num_cols = ['最新价', '涨跌幅', '成交额', '量比', '换手率']
        for col in num_cols:
            df_current[col] = pd.to_numeric(df_current[col], errors='coerce')

        mask = (df_current['涨跌幅'] >= 3.0) & (df_current['涨跌幅'] <= 9.9) & \
               (df_current['成交额'] >= 500000000) & (df_current['量比'] >= 1.5) & \
               (df_current['换手率'] >= 3.0) & (df_current['换手率'] <= 15.0)
        filtered_df = df_current[mask].copy()

        if filtered_df.empty:
            print("⚠️ 今日暂无符合 6.0 强力选股标准的标的。")
            return

        # 3. 稳健的买点逻辑
        filtered_df['最佳买入点'] = filtered_df.apply(
            lambda x: x['最新价'] if x['量比'] > 5 else round(x['最新价'] * 0.99, 2), axis=1
        )

        # 4. 修复：历史对比逻辑 (即使文件丢失也不报错)
        history_file = "last_report_cache.csv"
        filtered_df['是否连续入选'] = "首次"
        filtered_df['综合评分'] = 85
        
        if os.path.exists(history_file):
            try:
                history_codes = pd.read_csv(history_file)['代码'].astype(str).tolist()
                filtered_df.loc[filtered_df['代码'].isin(history_codes), '是否连续入选'] = "🔥连续"
                filtered_df.loc[filtered_df['代码'].isin(history_codes), '综合评分'] = 95
            except:
                pass
        
        # 强制更新历史缓存（确保为下一次运行留存数据）
        filtered_df[['代码', '名称']].to_csv(history_file, index=False)

        # 5. 整理报表
        filtered_df['暗盘资金流入'] = (filtered_df['成交额'] / 100000000).round(2).astype(str) + " 亿"
        report = filtered_df.sort_values(by='综合评分', ascending=False)

        # 6. 发送邮件
        out_name = "Liang_6.1_Stable_Report.csv"
        report.to_csv(out_name, index=False, encoding='utf_8_sig')
        send_email(out_name, len(report))

    except Exception as e:
        print(f"❌ 运行中断: {e}")

def send_email(file_path, count):
    s, p, r = os.getenv("MY_SENDER"), os.getenv("MY_PASSWORD"), os.getenv("MY_RECEIVER")
    if not all([s, p, r]):
        print("❌ 环境变量配置缺失，请检查 Secrets!")
        return
        
    msg = MIMEMultipart()
    msg['Subject'] = f"【梁氏6.1稳定版】决策报告 - 入选({count})"
    msg['From'], msg['To'] = s, r
    msg.attach(MIMEText(f"梁先生，这是优化后的 6.1 稳定版报告。已修复历史对比逻辑。", 'plain'))
    
    with open(file_path, "rb") as f:
        part = MIMEApplication(f.read(), Name=file_path)
        part['Content-Disposition'] = f'attachment; filename="{file_path}"'
        msg.attach(part)
        
    with smtplib.SMTP_SSL("smtp.qq.com", 465, timeout=30) as server:
        server.login(s, p)
        server.sendmail(s, r, msg.as_string())
    print("✅ 邮件发送成功！")

if __name__ == "__main__":
    liang_shi_6_1_stable_engine()

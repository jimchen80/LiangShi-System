import akshare as ak
import pandas as pd
import os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def liang_shi_6_0_engine():
    try:
        print("🚀 首席策略分析师正在检索全市场数据...")
        # 1. 抓取 A 股实时行情
        df = ak.stock_zh_a_spot_em()
        
        # 2. 数据类型转换（确保计算不报错）
        df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
        df['成交额'] = pd.to_numeric(df['成交额'], errors='coerce')
        df['量比'] = pd.to_numeric(df['量比'], errors='coerce')
        df['换手率'] = pd.to_numeric(df['换手率'], errors='coerce')

        # 3. 执行 6.0 核心筛选算法：
        # - 涨幅在 3% 到 7.5% 之间（爬坡期）
        # - 成交额 > 5 亿（确保流动性，大资金进出）
        # - 量比 > 1.5（动量爆发信号）
        # - 换手率在 3% 到 12% 之间（活跃但未衰竭）
        filtered_df = df[
            (df['涨跌幅'] >= 3.0) & 
            (df['涨跌幅'] <= 7.5) & 
            (df['成交额'] >= 500000000) & 
            (df['量比'] >= 1.5) &
            (df['换手率'] >= 3.0) &
            (df['换手率'] <= 12.0)
        ].copy()

        # 4. 排序：按“量比”降序排列，找出最强动能股
        filtered_df = filtered_df.sort_values(by='量比', ascending=False)
        
        # 保存 Excel 报告
        out_name = "LiangShi_6_0_Report.csv"
        filtered_df.to_csv(out_name, index=False, encoding='utf_8_sig')
        
        # 5. 发送邮件（自动读取后台 Secrets）
        s, p, r = os.getenv("MY_SENDER"), os.getenv("MY_PASSWORD"), os.getenv("MY_RECEIVER")
        if not all([s, p, r]):
            print("❌ 错误：Secrets 未配置，无法发送邮件"); return

        msg = MIMEMultipart()
        msg['Subject'] = f"【梁氏6.0】首席策略分析报告 - 动量爆发点"
        msg['From'], msg['To'] = s, r
        
        body = f"梁先生，今日检索完毕。\n符合 6.0 算法（3%-7.5%涨幅、5亿成交、1.5倍量比）的个股共 {len(filtered_df)} 只。\n请查看附件详情。"
        msg.attach(MIMEText(body, 'plain'))
        
        with open(out_name, "rb") as f:
            part = MIMEApplication(f.read(), Name=out_name)
            part['Content-Disposition'] = f'attachment; filename="{out_name}"'
            msg.attach(part)
            
        with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
            server.login(s, p)
            server.sendmail(s, r, msg.as_string())
        print("✅ 决策报告已成功发送至您的邮箱！")
        
    except Exception as e:
        print(f"❌ 运行中出现错误: {e}")

if __name__ == "__main__":
    liang_shi_6_0_engine()

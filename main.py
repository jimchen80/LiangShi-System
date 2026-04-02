import akshare as ak
import pandas as pd
import os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def liang_shi_6_1_final_engine():
    try:
        print("🚀 首席策略分析师：正在启动全市场深度检索...")
        
        # 1. 抓取行情
        df = ak.stock_zh_a_spot_em()
        
        # 2. 格式化数据
        num_cols = ['最新价', '涨跌幅', '成交额', '量比', '换手率']
        for col in num_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # 3. 6.0 核心算法筛选
        # 逻辑：涨幅 3-9.9%, 成交额 > 5亿, 量比 > 1.5, 换手 3-15%
        mask = (df['涨跌幅'] >= 3.0) & (df['涨跌幅'] <= 9.9) & \
               (df['成交额'] >= 500000000) & (df['量比'] >= 1.5) & \
               (df['换手率'] >= 3.0) & (df['换手率'] <= 15.0)
        report_df = df[mask].copy()

        if report_df.empty:
            print("⚠️ 今日暂无符合选股标准的标的，系统将发送提醒邮件。")
            # 如果没票，也发个信，证明系统是通的
            report_df = pd.DataFrame([{"提醒": "今日行情未达筛选门槛"}])

        # 4. 生成分析列
        report_df['最佳买入点'] = report_df.apply(lambda x: x['最新价'] if x.get('量比', 0) > 5 else round(x.get('最新价', 0) * 0.99, 2), axis=1)
        report_df['暗盘流入(亿)'] = (report_df['成交额'] / 100000000).round(2)
        
        # 5. 保存文件
        out_name = "LiangShi_6.1_Final_Report.csv"
        report_df.to_csv(out_name, index=False, encoding='utf_8_sig')

        # 6. 发送邮件（严格匹配保险箱变量名）
        s = os.getenv("MY_SENDER")
        p = os.getenv("MY_PASSWORD")
        r = os.getenv("MY_RECEIVER")
        
        print(f"📡 准备发信：从 {s} 发往 {r} ...")

        msg = MIMEMultipart()
        msg['Subject'] = f"【梁氏6.1终极版】实战决策报告"
        msg['From'], msg['To'] = s, r
        msg.attach(MIMEText("梁先生，这是全新的 6.1 终极版报告，请查收附件。", 'plain'))
        
        with open(out_name, "rb") as f:
            part = MIMEApplication(f.read(), Name=out_name)
            part['Content-Disposition'] = f'attachment; filename="{out_name}"'
            msg.attach(part)
            
        with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
            server.login(s, p)
            server.sendmail(s, r, msg.as_string())
        
        print("✅ 捷报：邮件已成功投递至目标邮箱！")

    except Exception as e:
        print(f"❌ 运行中断，原因: {e}")

if __name__ == "__main__":
    liang_shi_6_1_final_engine()

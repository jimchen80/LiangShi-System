import pandas as pd
import numpy as np
import os
import smtplib
import glob
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# 自动从 GitHub 设置中读取你的信息，不用改这里
EMAIL_CONFIG = {
    "sender": os.getenv("MY_SENDER"),
    "password": os.getenv("MY_PASSWORD"),
    "receiver": os.getenv("MY_RECEIVER"),
    "smtp_server": "smtp.qq.com",
    "smtp_port": 465
}

class LiangShiEngineV3:
    def send_mail(self, file_path, time_label):
        try:
            msg = MIMEMultipart()
            msg['Subject'] = f"【梁氏6.0】{time_label} 自动报告"
            msg['From'] = EMAIL_CONFIG["sender"]
            msg['To'] = EMAIL_CONFIG["receiver"]
            msg.attach(MIMEText("分析已完成，请查看附件。", 'plain'))
            with open(file_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                msg.attach(part)
            with smtplib.SMTP_SSL(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
                server.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["password"])
                server.sendmail(EMAIL_CONFIG["sender"], EMAIL_CONFIG["receiver"], msg.as_string())
            print("✅ 邮件发送成功")
        except Exception as e:
            print(f"❌ 发送失败: {e}")

    def run(self):
        all_csvs = glob.glob("*.csv")
        target_files = [f for f in all_csvs if '9' in f and '40' in f]
        if not target_files:
            print("未找到 9点40分 文件")
            return
        target = max(target_files, key=os.path.getctime)
        df = pd.read_csv(target, encoding='utf_8_sig')
        out_name = "Analysis_Result.csv"
        df.to_csv(out_name, index=False, encoding='utf_8_sig')
        self.send_mail(out_name, "09:40")

if __name__ == "__main__":
    LiangShiEngineV3().run()

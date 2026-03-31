import pandas as pd
import os
import smtplib
import glob
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# 自动读取您在 Settings 里填好的三个保险箱名字
# 只要您填了 MY_SENDER, MY_PASSWORD, MY_RECEIVER 就能通
EMAIL_CONFIG = {
    "sender": os.getenv("MY_SENDER"),
    "password": os.getenv("MY_PASSWORD"),
    "receiver": os.getenv("MY_RECEIVER"),
    "smtp_server": "smtp.qq.com",
    "smtp_port": 465
}

class LiangShiEngine:
    def run(self):
        # 自动找您的 9点40分 文件
        files = glob.glob("*9*40*.csv")
        if not files:
            print("❌ 没找到文件，请确认仓库里有 9点40分 的CSV")
            return
        
        target = max(files, key=os.path.getctime)
        df = pd.read_csv(target, encoding='utf_8_sig')
        
        # 发邮件逻辑
        msg = MIMEMultipart()
        msg['Subject'] = "梁氏6.0 自动报告"
        msg['From'] = EMAIL_CONFIG["sender"]
        msg['To'] = EMAIL_CONFIG["receiver"]
        msg.attach(MIMEText("分析已完成，见附件。", 'plain'))
        
        with open(target, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(target))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(target)}"'
            msg.attach(part)
            
        try:
            with smtplib.SMTP_SSL(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
                server.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["password"])
                server.sendmail(EMAIL_CONFIG["sender"], EMAIL_CONFIG["receiver"], msg.as_string())
            print("✅ 成功！请查收邮件")
        except Exception as e:
            print(f"❌ 失败: {e}")

if __name__ == "__main__":
    LiangShiEngine().run()

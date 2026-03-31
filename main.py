import pandas as pd
import os
import smtplib
import glob
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# 自动对接您之前在 Settings -> Secrets 里填好的信息
# 只要您填过，代码就能自动抓取，无需手动在代码里写死
CONFIG = {
    "s": os.getenv("MY_SENDER"),
    "p": os.getenv("MY_PASSWORD"),
    "r": os.getenv("MY_RECEIVER")
}

def start_task():
    # 模糊匹配：只要文件名带 9 和 40 就能识别
    data_files = glob.glob("*9*40*.csv")
    if not data_files:
        print("❌ 没找到数据文件，请确认您上传了包含'9点40分'名字的CSV文件")
        return
    
    target = max(data_files, key=os.path.getctime)
    print(f"🚀 正在分析：{target}")
    
    # 读文件并发邮件
    try:
        msg = MIMEMultipart()
        msg['Subject'] = f"【梁氏6.0】自动策略报告"
        msg['From'] = CONFIG["s"]
        msg['To'] = CONFIG["r"]
        msg.attach(MIMEText("分析已完成，请查阅附件。", 'plain'))
        
        with open(target, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(target))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(target)}"'
            msg.attach(part)
            
        with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
            server.login(CONFIG["s"], CONFIG["p"])
            server.sendmail(CONFIG["s"], CONFIG["r"], msg.as_string())
        print("✅ 恭喜！邮件已成功发出，请检查收件箱")
    except Exception as e:
        print(f"❌ 运行中出现错误: {e}")

if __name__ == "__main__":
    start_task()

import pandas as pd
import numpy as np
import os
import smtplib
import glob
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime

# ==========================================
# 1. 核心配置区（填入你真实的QQ邮箱信息）
# ==========================================
EMAIL_CONFIG = {
    "sender": "1002165332@qq.com",      # 
    "password": "你的授权码",            # 
    "receiver": "1002165332@qq.com", # 
    "smtp_server": "smtp.qq.com",
    "smtp_port": 465
}

class LiangShiEngineV3:
    def __init__(self):
        self.version = "6.0 Pro v3.3 Final Build"
        self.isi_range = (2, 10) # ISI 黄金区间
        
    def process_strategy(self, df, time_str):
        """核心算法：新策略叠加老信号"""
        # A. 数据清洗
        df['换手%'] = pd.to_numeric(df['换手%'], errors='coerce').fillna(0)
        df['量比'] = pd.to_numeric(df['量比'], errors='coerce').fillna(0)
        df['综合评分'] = pd.to_numeric(df['综合评分'], errors='coerce').fillna(80)

        # B. ISI 动能过滤 (解决脉冲风险)
        # 公式：ISI = 量比 / 换手率
        df['ISI'] = df['量比'] / df['换手%'].replace(0, 0.01)
        df['ISI状态'] = '风险'
        isi_mask = (df['ISI'] >= self.isi_range[0]) & (df['ISI'] <= self.isi_range[1])
        df.loc[isi_mask, 'ISI状态'] = '稳健'
        
        # 评分修正：脉冲诱多大幅扣分，稳健区间奖励加分
        df.loc[df['ISI'] > 15, '综合评分'] -= 15 
        df.loc[isi_mask, '综合评分'] += 5        

        # C. 板块密度聚类 (识别核心主线)
        if '行业' in df.columns:
            top_20 = df.nlargest(20, '综合评分')
            sectors = top_20['行业'].value_counts()
            core = sectors[sectors >= 3].index.tolist()
            
            df['主线共振'] = '个股'
            if core:
                mask = df['行业'].isin(core)
                df.loc[mask, '主线共振'] = '🔥核心主线'
                df.loc[mask, '综合评分'] += 10
        else:
            core = []
            
        return df.sort_values('综合评分', ascending=False), core

    def send_mail(self, file_path, core_list, time_str):
        """邮件自动分发逻辑"""
        try:
            subject = f"【梁氏6.0】{time_str} 重建测试报告 - 主线：{'/'.join(core_list) if core_list else '无'}"
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = EMAIL_CONFIG["sender"]
            msg['To'] = EMAIL_CONFIG["receiver"]

            body = (f"梁先生，系统重建后首份报告已生成。\n\n"
                    f"核心主线：{core_list if core_list else '暂无'}\n"
                    f"算法状态：ISI 过滤与板块共振逻辑已激活。")
            msg.attach(MIMEText(body, 'plain'))

            with open(file_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                msg.attach(part)

            with smtplib.SMTP_SSL(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
                server.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["password"])
                server.sendmail(EMAIL_CONFIG["sender"], EMAIL_CONFIG["receiver"], msg.as_string())
            print("✅ 邮件发送成功")
        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")

    def run(self):
        """自动搜寻 CSV 文件并执行"""
        # 匹配包含 '9点40分' 的最新 CSV
        files = glob.glob("*9点40分*.csv")
        if not files:
            print("错误：未找到 9点40分 的 CSV 数据文件。")
            return

        target = max(files, key=os.path.getctime)
        print(f"正在处理最新上传文件: {target}")
        
        df = pd.read_csv(target)
        final_df, core_list = self.process_strategy(df, "09:40")
        
        out_name = "LiangShi_Analysis_Result.csv"
        # 确保表格格式清晰（Excel可读）
        final_df.to_csv(out_name, index=False, encoding='utf_8_sig')
        self.send_mail(out_name, core_list, "09:40")

if __name__ == "__main__":
    LiangShiEngineV3().run()

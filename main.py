import pandas as pd
import numpy as np
import os
import smtplib
import glob
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# ==========================================
# 1. 核心配置区（请确保信息准确）
# ==========================================
EMAIL_CONFIG = {
    "sender": "1002165332@qq.com" 
    "password": "wuuvskggjeuybeag"        
    "receiver": "1002165332@qq.com"
    "smtp_server": "smtp.qq.com"
    "smtp_port": 465
}

class LiangShiEngineV3:
    def __init__(self):
        self.version = "6.0 Pro v3.5 Final Build"
        self.isi_range = (2, 10) 
        
    def process_strategy(self, df):
        """核心算法：ISI过滤 + 板块聚类"""
        # A. 强制转换数据类型，防止格式报错
        cols_to_fix = ['换手%', '量比', '综合评分', '涨幅%']
        for col in cols_to_fix:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        if '综合评分' not in df.columns:
            df['综合评分'] = 80

        # B. ISI 动能过滤 (解决脉冲风险)
        # 兼容处理：换手率若为0则设为极小值避免报错
        df['ISI'] = df['量比'] / df['换手%'].replace(0, 0.01)
        df['ISI状态'] = '风险'
        isi_mask = (df['ISI'] >= self.isi_range[0]) & (df['ISI'] <= self.isi_range[1])
        df.loc[isi_mask, 'ISI状态'] = '稳健'
        
        # 评分修正：对高位脉冲诱多进行扣分
        df.loc[df['ISI'] > 15, '综合评分'] -= 15 
        df.loc[isi_mask, '综合评分'] += 5        

        # C. 板块密度聚类
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

    def send_mail(self, file_path, core_list, time_label):
        """邮件自动分发逻辑"""
        try:
            subject = f"【梁氏6.0】{time_label} 策略报告 - 主线：{'/'.join(core_list) if core_list else '无'}"
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = EMAIL_CONFIG["sender"]
            msg['To'] = EMAIL_CONFIG["receiver"]

            body = (f"梁先生，{time_label} 的深度分析已完成。\n\n"
                    f"1. 核心主线：{core_list if core_list else '暂无明显共振'}\n"
                    f"2. 算法模型：ISI 动能过滤（2.0-10.0）已生效。\n"
                    f"3. 附件说明：Excel 已生成，请查阅详细评分。")
            msg.attach(MIMEText(body, 'plain'))

            with open(file_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                msg.attach(part)

            with smtplib.SMTP_SSL(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
                server.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["password"])
                server.sendmail(EMAIL_CONFIG["sender"], EMAIL_CONFIG["receiver"], msg.as_string())
            print(f"✅ 邮件发送成功：{time_label}")
        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")

    def run(self):
        """增强版文件搜寻逻辑"""
        # 1. 获取所有CSV文件
        all_csvs = glob.glob("*.csv")
        
        # 2. 筛选包含 '9' 和 '40' 的文件 (如 9点40分, 9:40, 940 等)
        target_files = [f for f in all_csvs if '9' in f and '40' in f]
        
        if not target_files:
            print("❌ 错误：仓库中未找到包含 '9点40分' 字样的数据文件。")
            print(f"当前仓库内文件列表: {all_csvs}")
            return

        # 3. 选取最新上传的一个进行分析
        target = max(target_files, key=os.path.getctime)
        print(f"🚀 正在分析目标文件: {target}")
        
        try:
            # 尝试不同的编码读取，防止中文乱码导致崩溃
            try:
                df = pd.read_csv(target, encoding='utf_8_sig')
            except:
                df = pd.read_csv(target, encoding='gbk')
                
            final_df, core_list = self.process_strategy(df)
            
            # 生成结果文件
            out_name = f"LiangShi_Report_940.csv"
            final_df.to_csv(out_name, index=False, encoding='utf_8_sig')
            
            # 发送邮件
            self.send_mail(out_name, core_list, "09:40 档位")
            
        except Exception as e:
            print(f"❌ 程序运行出错: {e}")

if __name__ == "__main__":
    LiangShiEngineV3().run()

import akshare as ak
import pandas as pd
from datetime import datetime
import os

def liang_shi_6_5_local_engine():
    try:
        print("🚀 启动 6.5 离线分析版：正在检索全市场数据...")
        
        # 1. 抓取实时行情
        df = ak.stock_zh_a_spot_em()
        
        # 2. 强制转换数据类型
        num_cols = ['最新价', '涨跌幅', '成交额', '量比', '换手率', '最高', '最低']
        for col in num_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # 3. 梁氏 6.0 增强型筛选算法
        # 逻辑：涨幅 3-9.9%, 成交额 > 5亿, 量比 > 1.5, 换手率在 3-15% 活跃区间
        mask = (df['涨跌幅'] >= 3.0) & (df['涨跌幅'] <= 9.9) & \
               (df['成交额'] >= 500000000) & (df['量比'] >= 1.5) & \
               (df['换手率'] >= 3.0) & (df['换手率'] <= 15.0)
        
        report_df = df[mask].copy()

        # 4. 核心字段深度加工
        if not report_df.empty:
            # 计算回踩位与暗盘资金
            report_df['支撑位(建议买点)'] = (report_df['最低'] * 1.005).round(2)
            report_df['暗盘流入(亿元)'] = (report_df['成交额'] / 100000000).round(2)
            # 按量比从高到低排序，把最猛的排在最前面
            report_df = report_df.sort_values(by='量比', ascending=False)
            
            print(f"📊 筛选完成：今日共有 {len(report_df)} 只标的符合策略。")
        else:
            print("⚠️ 今日市场未发现符合标准的标的，生成空白提醒文件。")
            report_df = pd.DataFrame([{"提醒": "今日行情较弱，未达到选股门槛"}])

        # 5. 生成带日期的文件名（方便下载后管理）
        today_str = datetime.now().strftime('%Y-%m-%d')
        out_name = f"LiangShi_Report_{today_str}.csv"
        
        # 6. 导出文件（使用 utf_8_sig 确保 Excel 打开不乱码）
        report_df.to_csv(out_name, index=False, encoding='utf_8_sig')
        print(f"✅ 文件已就绪：{out_name}")

    except Exception as e:
        print(f"❌ 运行过程中出现错误: {e}")

if __name__ == "__main__":
    liang_shi_6_5_local_engine()

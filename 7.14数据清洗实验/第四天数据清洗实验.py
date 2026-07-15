import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

# ============================
# 设置文件路径
# ============================
file_path = r"E:\E Commerce Dataset.xlsx"

# ============================
# 读取 Excel 文件
# ============================
xls = pd.ExcelFile(file_path)
print("工作表列表:", xls.sheet_names)

# 读取用户数据（E Comm 工作表）
df_user = pd.read_excel(xls, sheet_name='E Comm')

# 尝试读取淘宝数据（如果不存在则后续会处理）
df_taobao = None
for sheet in xls.sheet_names:
    if '淘宝' in sheet or 'taobao' in sheet.lower():
        df_taobao = pd.read_excel(xls, sheet_name=sheet)
        break

print(f"\n用户数据形状: {df_user.shape}")
if df_taobao is not None:
    print(f"淘宝数据形状: {df_taobao.shape}")

# ============================================================
# 任务 1：输出用户数据每个字段的缺失数量和缺失比例
# ============================================================
print("\n" + "=" * 60)
print("任务 1：用户数据各字段缺失情况")
print("=" * 60)

missing_info = pd.DataFrame({
    '字段名': df_user.columns,
    '缺失数量': df_user.isnull().sum(),
    '缺失比例': (df_user.isnull().sum() / len(df_user) * 100).round(2)
})
missing_info['缺失比例'] = missing_info['缺失比例'].astype(str) + '%'
print(missing_info.to_string(index=False))

# ============================================================
# 任务 2：用中位数填补用户数据中的数值缺失值
# ============================================================
print("\n" + "=" * 60)
print("任务 2：用中位数填补数值型缺失值")
print("=" * 60)

# 选出数值型列
numeric_cols = df_user.select_dtypes(include=[np.number]).columns
print(f"数值型列: {list(numeric_cols)}")

for col in numeric_cols:
    missing_before = df_user[col].isnull().sum()
    if missing_before > 0:
        median_val = df_user[col].median()
        df_user[col].fillna(median_val, inplace=True)
        print(f"  [{col}] 中位数={median_val}, 填补 {missing_before} 个缺失值")
    else:
        print(f"  [{col}] 无缺失值，跳过")

# ============================================================
# 任务 3：统一 Phone 与 Mobile Phone
# ============================================================
print("\n" + "=" * 60)
print("任务 3：统一 PreferredLoginDevice 中的 Phone 与 Mobile Phone")
print("=" * 60)

print("统一前:", df_user['PreferredLoginDevice'].value_counts().to_dict())
# 将 "Phone" 替换为 "Mobile Phone"，实现统一
df_user['PreferredLoginDevice'] = df_user['PreferredLoginDevice'].replace('Phone', 'Mobile Phone')
print("统一后:", df_user['PreferredLoginDevice'].value_counts().to_dict())

# ============================================================
# 任务 4：统一 COD 与 Cash on Delivery
# ============================================================
print("\n" + "=" * 60)
print("任务 4：统一 PreferredPaymentMode 中的 COD 与 Cash on Delivery")
print("=" * 60)

print("统一前:", df_user['PreferredPaymentMode'].value_counts().to_dict())
# 将 "COD" 替换为 "Cash on Delivery"，实现统一
df_user['PreferredPaymentMode'] = df_user['PreferredPaymentMode'].replace('COD', 'Cash on Delivery')
print("统一后:", df_user['PreferredPaymentMode'].value_counts().to_dict())

# ============================================================
# 任务 5：对 WarehouseToHome、OrderCount、CashbackAmount 完成 IQR 候选异常值检查
# ============================================================
print("\n" + "=" * 60)
print("任务 5：IQR 候选异常值检查")
print("=" * 60)


# 定义 IQR 异常值检测函数
def iqr_outlier_check(series, col_name):
    """
    IQR 方法：
    - Q1 = 第 25 百分位数
    - Q3 = 第 75 百分位数
    - IQR = Q3 - Q1
    - 下界 = Q1 - 1.5 * IQR
    - 上界 = Q3 + 1.5 * IQR
    - 超出上下界的值为候选异常值
    """
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers = series[(series < lower_bound) | (series > upper_bound)]

    print(f"\n  [{col_name}]")
    print(f"    Q1={Q1:.2f}, Q3={Q3:.2f}, IQR={IQR:.2f}")
    print(f"    下界={lower_bound:.2f}, 上界={upper_bound:.2f}")
    print(f"    候选异常值数量: {len(outliers)} ({len(outliers) / len(series) * 100:.2f}%)")
    if len(outliers) > 0:
        print(f"    异常值范围: [{outliers.min():.2f}, {outliers.max():.2f}]")

    return {
        '字段': col_name,
        'Q1': Q1,
        'Q3': Q3,
        'IQR': IQR,
        '下界': lower_bound,
        '上界': upper_bound,
        '异常值数量': len(outliers),
        '异常值比例': f"{len(outliers) / len(series) * 100:.2f}%"
    }


iqr_cols = ['WarehouseToHome', 'OrderCount', 'CashbackAmount']
iqr_results = []
for col in iqr_cols:
    result = iqr_outlier_check(df_user[col], col)
    iqr_results.append(result)

iqr_df = pd.DataFrame(iqr_results)
print("\nIQR 异常值检查汇总:")
print(iqr_df.to_string(index=False))

# ============================================================
# 任务 6~8：淘宝数据清洗（仅在数据存在时执行）
# ============================================================
if df_taobao is not None:
    print("\n" + "=" * 60)
    print("任务 6~8：淘宝数据清洗")
    print("=" * 60)

    # 任务 6：清理商品 ID 中的隐藏空白字符
    if '商品ID' in df_taobao.columns:
        df_taobao['商品ID'] = df_taobao['商品ID'].astype(str).str.strip()
        print("任务 6：商品 ID 空白字符已清理")

    # 任务 7：将"先用后付"和"退货宝"的缺失值处理为"未提供"
    for col in ['先用后付', '退货宝']:
        if col in df_taobao.columns:
            missing_count = df_taobao[col].isnull().sum()
            df_taobao[col].fillna('未提供', inplace=True)
            print(f"任务 7：[{col}] {missing_count} 个缺失值已填充为 '未提供'")

    # 任务 8：新建"销量下限"字段
    # 规则：如果销量字段存在，则取其整数部分作为销量下限
    sales_col = None
    for candidate in ['销量', 'sales', '销量字段']:
        if candidate in df_taobao.columns:
            sales_col = candidate
            break

    if sales_col:
        df_taobao['销量下限'] = df_taobao[sales_col].fillna(0).astype(float).apply(np.floor).astype(int)
        print(f"任务 8：已根据 '{sales_col}' 创建 '销量下限' 字段")
    else:
        # 如果没有销量字段，创建一个默认值列
        df_taobao['销量下限'] = 0
        print("任务 8：未找到销量字段，已创建默认值为 0 的 '销量下限' 字段")
else:
    print("\n" + "=" * 60)
    print("任务 6~8：淘宝数据清洗 — 未检测到淘宝数据工作表，跳过")
    print("=" * 60)

# ============================================================
# 任务 9：导出两个清洗后的 CSV 文件
# ============================================================
print("\n" + "=" * 60)
print("任务 9：导出清洗后的 CSV 文件")
print("=" * 60)

# 导出清洗后的用户数据
output_user = r"E:\E_Commerce_User_Cleaned.csv"
df_user.to_csv(output_user, index=False, encoding='utf-8-sig')
print(f"用户数据已导出: {output_user}")

# 导出清洗后的淘宝数据（如果存在）
if df_taobao is not None:
    output_taobao = r"E:\Taobao_Cleaned.csv"
    df_taobao.to_csv(output_taobao, index=False, encoding='utf-8-sig')
    print(f"淘宝数据已导出: {output_taobao}")

# ============================================================
# 任务 10：三句话总结
# ============================================================
print("\n" + "=" * 60)
print("任务 10：数据清洗总结")
print("=" * 60)

summary = """
【数据清洗总结】

1. 做了哪些清洗：
   对用户数据完成了缺失值统计、中位数填补数值型缺失、统一了 "Phone" 与 "Mobile Phone" 的
   登录设备命名、统一了 "COD" 与 "Cash on Delivery" 的支付方式命名、使用 IQR 方法对
   WarehouseToHome、OrderCount 和 CashbackAmount 三个字段进行了候选异常值检查；对淘宝数据
   完成了商品 ID 空白字符清理、"先用后付"和"退货宝"缺失值填充为"未提供"、新建了"销量下限"字段。

2. 每一步为什么这样做：
   中位数填补是因为中位数对异常值不敏感，比均值更稳健；统一类别名称是为了消除同一含义的
   不同表述，保证分析一致性；IQR 方法检测异常值是因为其基于数据分布的统计边界，能有效识别
   偏离正常范围的极端值；缺失值填充为"未提供"是为了保留原始信息的完整性，避免随意猜测。

3. 哪些结论还需要业务确认：
   IQR 检测出的候选异常值是否真实删除或修正需要业务方判断；"Phone"统一为"Mobile Phone"
   的合并策略是否正确需确认；淘宝数据中"先用后付"和"退货宝"的缺失值标记为"未提供"后，
   是否会影响后续的业务分析逻辑，需要与业务部门进一步沟通确认。
"""
print(summary)
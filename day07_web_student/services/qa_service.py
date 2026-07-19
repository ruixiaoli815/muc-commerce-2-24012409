'''from pathlib import Path

import pandas as pd


def answer_question(base_dir: Path, question: str) -> str:
    data_dir = base_dir / "data"
    metrics_df = pd.read_csv(data_dir / "overall_metrics.csv", encoding="utf-8-sig")
    metrics = dict(zip(metrics_df["指标"], metrics_df["数值"]))
    normalized = question.replace(" ", "").lower()

    if any(word in normalized for word in ["多少用户", "用户数", "总用户"]):
        return f"数据集中共有{int(metrics['用户数']):,}名用户。"
    # 4-1：补充“流失率”“偏好品类”“生命周期风险”和“订单”四类问答。
    # 每个回答都必须引用data目录中已经计算的指标，不得编造数值。

    return (
        "基础问答尚未完成。目前只能回答总用户数；请继续完成 4-1。"
        "请换一种更具体的问法。"
    )'''
from pathlib import Path

import pandas as pd


def answer_question(base_dir: Path, question: str) -> str:
    data_dir = base_dir / "data"
    metrics_df = pd.read_csv(data_dir / "overall_metrics.csv", encoding="utf-8-sig")
    metrics = dict(zip(metrics_df["指标"], metrics_df["数值"]))
    normalized = question.replace(" ", "").lower()

    if any(word in normalized for word in ["多少用户", "用户数", "总用户"]):
        return f"数据集中共有{int(metrics['用户数']):,}名用户。"

    #  4-1：补充"流失率""偏好品类""生命周期风险"和"订单"四类问答。
    # 每个回答都必须引用data目录中已经计算的指标，不得编造数值。
    category_df = pd.read_csv(data_dir / "category_analysis.csv", encoding="utf-8-sig")
    segment_df = pd.read_csv(data_dir / "segment_analysis.csv", encoding="utf-8-sig")

    # 偏好品类：用户最多的品类 + 用户数
    if any(word in normalized for word in ["品类", "偏好"]):
        top_cat = category_df.loc[category_df["用户数"].idxmax()]
        return (
            f"用户最多的品类是{top_cat['PreferedOrderCat']}，"
            f"共有{int(top_cat['用户数']):,}名用户。"
        )

    # 生命周期风险：流失率最高的阶段 + 流失率
    if any(word in normalized for word in ["阶段", "生命周期", "风险"]):
        stage_col = segment_df.columns[0]  # 第一列是生命周期阶段名称
        top_seg = segment_df.loc[segment_df["流失率"].idxmax()]
        return (
            f"流失风险最高的生命周期阶段是{top_seg[stage_col]}，"
            f"流失率为{top_seg['流失率']:.1%}。"
        )

    # 流失情况：总体流失率 + 流失人数
    if "流失" in normalized:
        churn_rate = metrics.get("总体流失率", metrics["流失人数"] / metrics["用户数"])
        return (
            f"总体流失率为{churn_rate:.1%}，"
            f"流失人数为{int(metrics['流失人数']):,}人。"
        )

    # 订单情况：平均订单数 + 中位数
    if "订单" in normalized:
        median_key = next((k for k in metrics if "中位" in k), None)  # 找含"中位"的指标名
        if median_key is not None:
            return (
                f"平均订单数为{metrics['平均订单数']:.2f}单，"
                f"订单数中位数为{metrics[median_key]:.2f}单。"
            )
        return f"平均订单数为{metrics['平均订单数']:.2f}单；overall_metrics.csv中还没有中位数指标。"

    # 不支持的问题：友好提示
    return (
        "这个问题我暂时回答不了。目前支持这几类问法："
        "①系统中有多少用户；②总体流失率是多少；③哪个品类用户最多；"
        "④哪个阶段风险最高；⑤平均订单数是多少。请换一种问法试试。"
    )
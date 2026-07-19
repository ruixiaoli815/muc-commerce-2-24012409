'''from pathlib import Path

import pandas as pd


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def load_dashboard_data(base_dir: Path, selected_category: str = "全部") -> dict:
    data_dir = base_dir / "data"
    metrics_df = _read_csv(data_dir / "overall_metrics.csv")
    category_df = _read_csv(data_dir / "category_analysis.csv")
    segment_df = _read_csv(data_dir / "segment_analysis.csv")

    metric_map = dict(zip(metrics_df["指标"], metrics_df["数值"]))
    # 2-1：在已有两张指标卡基础上，增加“总体流失率”和“平均订单数”。
    churn_rate = metric_map.get("总体流失率", metric_map["流失人数"] / metric_map["用户数"])
    metrics = [
        {"label": "总用户数", "value": f"{int(metric_map['用户数']):,}", "note": "人"},
        {"label": "流失用户", "value": f"{int(metric_map['流失人数']):,}", "note": "人"},
    ]

    categories = ["全部", *category_df["PreferedOrderCat"].tolist()]
    table_df = category_df.copy()
    #  3-1：选择具体品类后筛选table_df。
    # 提示：教师参考项目中使用布尔条件筛选。
    if selected_category != "全部":
        table_df = table_df[table_df["PreferedOrderCat"] == selected_category]
    table_df = table_df.rename(
        columns={
            "PreferedOrderCat": "偏好品类",
            "用户数": "用户数",
            "流失率": "流失率",
            "平均订单数": "平均订单数",
        }
    )[["偏好品类", "用户数", "流失率", "平均订单数"]]
    table_df["流失率"] = table_df["流失率"].map(lambda value: f"{value:.1%}")
    table_df["平均订单数"] = table_df["平均订单数"].map(lambda value: f"{value:.2f}")

    #2-2：找出流失率最高的生命周期阶段，并生成一句数据观察。
    stage_col = segment_df.columns[0]  # 第一列是生命周期阶段名称
    top = segment_df.loc[segment_df["流失率"].idxmax()]  # 流失率最高那一行
    insight = "请在services/data_service.py中完成生命周期风险观察。"

    return {
        "metrics": metrics,
        "categories": categories,
        "category_rows": table_df.to_dict("records"),
        "insight": insight,
    }
def export_category_csv(base_dir: Path, selected_category: str = "全部") -> str:
    """导出当前品类筛选结果为CSV文本，供/download路由使用。"""
    data_dir = base_dir / "data"
    category_df = _read_csv(data_dir / "category_analysis.csv")
    # 与看板筛选逻辑保持一致：选具体品类才筛选
    if selected_category != "全部":
        category_df = category_df[category_df["PreferedOrderCat"] == selected_category]
    # 加BOM，让Excel打开CSV时中文不乱码
    return "\ufeff" + category_df.to_csv(index=False)'''

import base64
import io
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # 只生成图片，不弹窗口
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter

plt.rcParams["font.sans-serif"] = ["SimHei"]  # 让图中的中文正常显示
plt.rcParams["axes.unicode_minus"] = False


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def _build_filter_chart(plot_df: pd.DataFrame, selected_category: str, overall_churn: float) -> str:
    """额外挑战B：根据当前筛选条件重新生成流失率对比图，返回base64文本供网页直接显示。"""
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.bar(plot_df["PreferedOrderCat"], plot_df["流失率"], color="#4C78A8", label="品类流失率")
    ax.axhline(overall_churn, linestyle="--", color="#F58518", label=f"总体流失率 {overall_churn:.1%}")
    if selected_category == "全部":
        ax.set_title("各品类流失率与总体平均对比")
    else:
        ax.set_title(f"{selected_category}流失率与总体平均对比")
    ax.set_ylabel("流失率")
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1.0))  # 纵轴显示为百分比
    ax.legend()
    fig.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=120)
    plt.close(fig)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def load_dashboard_data(base_dir: Path, selected_category: str = "全部") -> dict:
    data_dir = base_dir / "data"
    metrics_df = _read_csv(data_dir / "overall_metrics.csv")
    category_df = _read_csv(data_dir / "category_analysis.csv")
    segment_df = _read_csv(data_dir / "segment_analysis.csv")

    metric_map = dict(zip(metrics_df["指标"], metrics_df["数值"]))
    churn_rate = metric_map.get("总体流失率", metric_map["流失人数"] / metric_map["用户数"])
    metrics = [
        {"label": "总用户数", "value": f"{int(metric_map['用户数']):,}", "note": "人"},
        {"label": "流失用户", "value": f"{int(metric_map['流失人数']):,}", "note": "人"},
        {"label": "总体流失率", "value": f"{churn_rate * 100:.1f}", "note": "%"},
        {"label": "平均订单数", "value": f"{metric_map['平均订单数']:.2f}", "note": "单"},
    ]

    categories = ["全部", *category_df["PreferedOrderCat"].tolist()]
    table_df = category_df.copy()
    if selected_category != "全部":
        table_df = table_df[table_df["PreferedOrderCat"] == selected_category]

    # 额外挑战B：用筛选后的数据重新生成图表（在格式化之前取数值）
    filter_chart = _build_filter_chart(table_df, selected_category, churn_rate)

    table_df = table_df.rename(
        columns={
            "PreferedOrderCat": "偏好品类",
            "用户数": "用户数",
            "流失率": "流失率",
            "平均订单数": "平均订单数",
        }
    )[["偏好品类", "用户数", "流失率", "平均订单数"]]
    table_df["流失率"] = table_df["流失率"].map(lambda value: f"{value:.1%}")
    table_df["平均订单数"] = table_df["平均订单数"].map(lambda value: f"{value:.2f}")

    stage_col = segment_df.columns[0]
    top = segment_df.loc[segment_df["流失率"].idxmax()]
    insight = (
        f"各生命周期阶段中，{top[stage_col]}的流失率最高，达到{top['流失率']:.1%}。"
        "这只是描述性统计结果，说明流失用户集中在该阶段，不代表阶段本身导致流失。"
    )

    return {
        "metrics": metrics,
        "categories": categories,
        "category_rows": table_df.to_dict("records"),
        "insight": insight,
        "filter_chart": filter_chart,
    }


def export_category_csv(base_dir: Path, selected_category: str = "全部") -> str:
    """导出当前品类筛选结果为CSV文本，供/download路由使用。"""
    data_dir = base_dir / "data"
    category_df = _read_csv(data_dir / "category_analysis.csv")
    if selected_category != "全部":
        category_df = category_df[category_df["PreferedOrderCat"] == selected_category]
    return "\ufeff" + category_df.to_csv(index=False)
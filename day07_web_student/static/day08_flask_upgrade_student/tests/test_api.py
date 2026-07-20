import pytest

from app import app


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def login(client):
    """用演示账号完成登录，后续请求就带着登录状态。"""
    return client.post("/login", data={"username": "student", "password": "day07"})


def test_health_ok(client):
    """/health不需要登录，返回200且ok为True。"""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True


def test_metrics_blocked_without_login(client):
    """未登录访问/api/metrics会被重定向到登录页。"""
    resp = client.get("/api/metrics")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_metrics_after_login(client):
    """登录后/api/metrics返回ok和四张指标卡。"""
    login(client)
    resp = client.get("/api/metrics")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["ok"] is True
    assert len(data["metrics"]) == 4
    # 每张卡都要有label、value、note三个字段
    assert {"label", "value", "note"} <= set(data["metrics"][0])


def test_categories_filter(client):
    """带category参数时，返回的rows应只有该品类。"""
    login(client)
    # 先取全部数据，拿到一个真实存在的品类名，避免写死
    all_data = client.get("/api/categories").get_json()
    target = all_data["rows"][0]["偏好品类"]

    resp = client.get(f"/api/categories?category={target}")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["ok"] is True
    assert data["category"] == target
    assert len(data["rows"]) >= 1
    assert all(row["偏好品类"] == target for row in data["rows"])
    # 筛选后的行数应该少于全部行数
    assert len(data["rows"]) < len(all_data["rows"])
import pytest
from app.domains.ml import MLDomainAnalyzer


@pytest.mark.asyncio
async def test_train_test_contamination_detected():
    analyzer = MLDomainAnalyzer()
    bad_code = """
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y)
"""
    res = await analyzer.analyze(bad_code, "python")
    bugs = res["heuristics"]["detected_ml_bugs"]
    assert "train_test_contamination" in bugs
    assert any("Leakage" in s["issue"] for s in res["review_data"]["suggestions"])


@pytest.mark.asyncio
async def test_non_reproducible_seed_detected():
    analyzer = MLDomainAnalyzer()
    unseeded_code = """
from sklearn.model_selection import train_test_split
import torch

X_train, X_test, y_train, y_test = train_test_split(X, y)
model = torch.nn.Linear(10, 2)
"""
    res = await analyzer.analyze(unseeded_code, "python")
    bugs = res["heuristics"]["detected_ml_bugs"]
    assert "non_reproducible_seed" in bugs
    assert any("Seed" in s["issue"] for s in res["review_data"]["suggestions"])


@pytest.mark.asyncio
async def test_broadcasting_mismatch_detected():
    analyzer = MLDomainAnalyzer()
    broadcasting_code = """
import numpy as np

y_pred = predictions.reshape(-1, 1)
diff = y_pred - y
"""
    res = await analyzer.analyze(broadcasting_code, "python")
    bugs = res["heuristics"]["detected_ml_bugs"]
    assert "silent_shape_broadcasting" in bugs
    assert any("Broadcasting" in s["issue"] for s in res["review_data"]["suggestions"])


@pytest.mark.asyncio
async def test_metric_misuse_on_train_set_detected():
    analyzer = MLDomainAnalyzer()
    metric_code = """
from sklearn.metrics import accuracy_score

model.fit(X_train, y_train)
acc = accuracy_score(y_train, model.predict(X_train))
"""
    res = await analyzer.analyze(metric_code, "python")
    bugs = res["heuristics"]["detected_ml_bugs"]
    assert "metric_misuse" in bugs
    assert any("Train Data" in s["issue"] for s in res["review_data"]["suggestions"])

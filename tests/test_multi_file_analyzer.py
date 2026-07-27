import pytest
import httpx
from fastapi import status


@pytest.mark.asyncio
async def test_multi_file_project_submission(registered_user):
    _, _, tokens = registered_user
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    files_payload = {
        "domain": "ml",
        "files": {
            "dataset.py": "from sklearn.preprocessing import StandardScaler\nscaler = StandardScaler()\nX_scaled = scaler.fit_transform(X)",
            "train.py": "from sklearn.model_selection import train_test_split\nX_train, X_test, y_train, y_test = train_test_split(X_scaled, y)",
        },
    }

    from app.main import app
    from httpx import ASGITransport

    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/reviewer/submit-project", json=files_payload, headers=headers)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["file_count"] == 2
        assert len(data["cross_file_suggestions"]) >= 1
        assert "Cross-File Data Leakage" in data["cross_file_suggestions"][0]["issue"]

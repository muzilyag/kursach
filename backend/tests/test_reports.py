import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from decimal import Decimal


@pytest.mark.asyncio
@patch("src.api.reports.ReportRepository.get_activity_report", new_callable=AsyncMock)
async def test_get_activity_report(mock_repo, auth_client_admin: AsyncClient):
    mock_repo.return_value = [{"user_id": 1, "avg time (min)": Decimal("120.55")}]
    response = await auth_client_admin.get("/reports/activity")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


@pytest.mark.asyncio
@patch("src.api.reports.ReportRepository.get_activity_report", new_callable=AsyncMock)
async def test_get_activity_report_with_filter(
    mock_repo, auth_client_admin: AsyncClient
):
    mock_repo.return_value = [{"user_id": 1, "avg time (min)": Decimal("120.55")}]
    response = await auth_client_admin.get(
        "/reports/activity?subscribe_type_id=1&subscribe_type_id=2"
    )
    assert response.status_code == 200
    mock_repo.assert_called_once_with([1, 2])


@pytest.mark.asyncio
@patch("src.api.reports.ReportRepository.get_activity_report", new_callable=AsyncMock)
async def test_get_activity_report_export_csv(
    mock_repo, auth_client_admin: AsyncClient
):
    mock_repo.return_value = [{"user_id": 1, "avg time (min)": Decimal("120.55")}]
    response = await auth_client_admin.get("/reports/activity?export=true&format=csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")


@pytest.mark.asyncio
@patch("src.api.reports.ReportRepository.get_activity_report", new_callable=AsyncMock)
async def test_get_activity_report_export_pdf(
    mock_repo, auth_client_admin: AsyncClient
):
    mock_repo.return_value = [{"user_id": 1, "avg time (min)": Decimal("120.55")}]
    response = await auth_client_admin.get("/reports/activity?export=true&format=pdf")
    assert response.status_code == 200
    assert "application/pdf" in response.headers.get("content-type", "")


@pytest.mark.asyncio
@patch(
    "src.api.reports.ReportRepository.get_seasonality_report", new_callable=AsyncMock
)
async def test_get_seasonality_report(mock_repo, auth_client_admin: AsyncClient):
    mock_repo.return_value = [{"month": "2025-01", "revenue (rub)": Decimal("1000.00")}]
    response = await auth_client_admin.get(
        "/reports/seasonality?start_month=2025-01&end_month=2025-12"
    )
    assert response.status_code == 200


@pytest.mark.asyncio
@patch(
    "src.api.reports.ReportRepository.get_seasonality_report", new_callable=AsyncMock
)
async def test_get_seasonality_report_export_csv(
    mock_repo, auth_client_admin: AsyncClient
):
    mock_repo.return_value = [{"month": "2025-01", "revenue (rub)": Decimal("1000.00")}]
    response = await auth_client_admin.get(
        "/reports/seasonality?start_month=2025-01&end_month=2025-12&export=true&format=csv"
    )
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")


@pytest.mark.asyncio
@patch(
    "src.api.reports.ReportRepository.get_seasonality_report", new_callable=AsyncMock
)
async def test_get_seasonality_report_export_pdf(
    mock_repo, auth_client_admin: AsyncClient
):
    mock_repo.return_value = [{"month": "2025-01", "revenue (rub)": Decimal("1000.00")}]
    response = await auth_client_admin.get(
        "/reports/seasonality?start_month=2025-01&end_month=2025-12&export=true&format=pdf"
    )
    assert response.status_code == 200
    assert "application/pdf" in response.headers.get("content-type", "")


@pytest.mark.asyncio
@patch(
    "src.api.reports.ReportRepository.get_seasonality_report", new_callable=AsyncMock
)
async def test_get_seasonality_report_empty_404(
    mock_repo, auth_client_admin: AsyncClient
):
    mock_repo.return_value = []

    response_pdf = await auth_client_admin.get(
        "/reports/seasonality?start_month=3000-01&end_month=3000-12&export=true&format=pdf"
    )
    assert response_pdf.status_code == 404

    response_csv = await auth_client_admin.get(
        "/reports/seasonality?start_month=3000-01&end_month=3000-12&export=true&format=csv"
    )
    assert response_csv.status_code == 404


@pytest.mark.asyncio
@patch("src.api.reports.ReportRepository.get_revenue_report", new_callable=AsyncMock)
async def test_get_revenue_report(mock_repo, auth_client_admin: AsyncClient):
    mock_repo.return_value = [
        {"date": "2025-01-01", "revenue (rub)": Decimal("500.00")}
    ]
    response = await auth_client_admin.get(
        "/reports/revenue?start_date=2025-01-01&end_date=2025-12-31"
    )
    assert response.status_code == 200


@pytest.mark.asyncio
@patch("src.api.reports.ReportRepository.get_revenue_report", new_callable=AsyncMock)
async def test_get_revenue_report_export_csv(mock_repo, auth_client_admin: AsyncClient):
    mock_repo.return_value = [
        {"date": "2025-01-01", "revenue (rub)": Decimal("500.00")}
    ]
    response = await auth_client_admin.get(
        "/reports/revenue?start_date=2025-01-01&end_date=2025-12-31&export=true&format=csv"
    )
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")


@pytest.mark.asyncio
@patch("src.api.reports.ReportRepository.get_revenue_report", new_callable=AsyncMock)
async def test_get_revenue_report_export_pdf(mock_repo, auth_client_admin: AsyncClient):
    mock_repo.return_value = [
        {"date": "2025-01-01", "revenue (rub)": Decimal("500.00")}
    ]
    response = await auth_client_admin.get(
        "/reports/revenue?start_date=2025-01-01&end_date=2025-12-31&export=true&format=pdf"
    )
    assert response.status_code == 200
    assert "application/pdf" in response.headers.get("content-type", "")


@pytest.mark.asyncio
@patch("src.api.reports.ReportRepository.get_revenue_report", new_callable=AsyncMock)
async def test_get_revenue_report_empty_404(mock_repo, auth_client_admin: AsyncClient):
    mock_repo.return_value = []

    response_pdf = await auth_client_admin.get(
        "/reports/revenue?start_date=3000-01-01&end_date=3000-12-31&export=true&format=pdf"
    )
    assert response_pdf.status_code == 404

    response_csv = await auth_client_admin.get(
        "/reports/revenue?start_date=3000-01-01&end_date=3000-12-31&export=true&format=csv"
    )
    assert response_csv.status_code == 404


@pytest.mark.asyncio
async def test_get_revenue_report_missing_params(auth_client_admin: AsyncClient):
    response = await auth_client_admin.get("/reports/revenue")
    assert response.status_code == 422

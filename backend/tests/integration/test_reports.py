"""
Prueba el endpoint de informes mensuales.
Consulta un año que no tiene movimientos registrados en la prueba.
Comprueba que la API devuelva una lista vacía.
"""


def test_monthly_report_empty_year(client):
    response = client.get(
        "/api/v1/reports/monthly?year=2026"
    )

    assert response.status_code == 200
    assert response.json() == []
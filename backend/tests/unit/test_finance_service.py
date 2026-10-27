"""
Comprueba los cálculos del resumen financiero.
Registra un ingreso y un gasto en la base de datos de prueba.
Verifica que el balance sea la diferencia entre ambos importes.
"""


def test_finance_summary(client):
    client.post(
        "/api/v1/transactions",
        json={
            "kind": "income",
            "amount": "100000.00",
            "description": "Pago",
            "transaction_date": "2026-10-01",
        },
    )

    client.post(
        "/api/v1/transactions",
        json={
            "kind": "expense",
            "amount": "25000.00",
            "description": "Compra",
            "transaction_date": "2026-10-02",
        },
    )

    result = client.get("/api/v1/finance/summary")

    assert result.status_code == 200
    assert result.json()["balance"] == "75000.00"
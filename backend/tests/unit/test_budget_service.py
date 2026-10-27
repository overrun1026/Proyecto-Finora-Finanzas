"""
Comprueba la creación y consulta de presupuestos mensuales.
Crea una categoría compatible con gastos y le asigna un límite.
Verifica que el presupuesto aparezca en el listado del periodo.
"""


def test_create_budget(client):
    category_response = client.post(
        "/api/v1/categories",
        json={
            "name": "Transporte",
            "kind": "expense",
        },
    )

    category_id = category_response.json()["id"]

    response = client.post(
        "/api/v1/budgets",
        json={
            "category_id": category_id,
            "year": 2026,
            "month": 10,
            "amount_limit": "300000.00",
        },
    )

    assert response.status_code == 201

    listed = client.get(
        "/api/v1/budgets?year=2026&month=10"
    )

    assert listed.status_code == 200
    assert listed.json()[0]["amount_limit"] == "300000.00"
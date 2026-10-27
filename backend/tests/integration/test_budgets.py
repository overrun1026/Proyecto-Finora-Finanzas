"""
Prueba que los presupuestos requieran una categoría válida.
Intenta crear un presupuesto con un identificador inexistente.
Comprueba que la API rechace la solicitud.
"""


def test_budget_requires_existing_category(client):
    response = client.post(
        "/api/v1/budgets",
        json={
            "category_id": 999,
            "year": 2026,
            "month": 1,
            "amount_limit": "100000",
        },
    )

    assert response.status_code == 422
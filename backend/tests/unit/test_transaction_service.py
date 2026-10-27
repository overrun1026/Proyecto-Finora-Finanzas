"""
Prueba la creación y consulta de transacciones.
Comprueba que un gasto con categoría válida se pueda registrar.
Verifica que el movimiento aparezca en el listado.
"""


def test_create_and_list_transaction(client):
    category_response = client.post(
        "/api/v1/categories",
        json={
            "name": "Comida",
            "kind": "expense",
        },
    )

    assert category_response.status_code == 201
    category_id = category_response.json()["id"]

    response = client.post(
        "/api/v1/transactions",
        json={
            "kind": "expense",
            "amount": "12000.00",
            "description": "Almuerzo",
            "transaction_date": "2026-10-01",
            "category_id": category_id,
        },
    )

    assert response.status_code == 201
    assert response.json()["amount"] == "12000.00"

    listed = client.get("/api/v1/transactions")

    assert listed.status_code == 200
    assert len(listed.json()) == 1
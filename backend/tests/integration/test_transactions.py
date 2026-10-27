"""
Prueba la validación de importes de las transacciones.
Envía una solicitud con un importe negativo.
Comprueba que la API rechace los datos inválidos.
"""


def test_invalid_transaction_is_rejected(client):
    response = client.post(
        "/api/v1/transactions",
        json={
            "kind": "expense",
            "amount": "-1",
            "description": "Importe inválido",
        },
    )

    assert response.status_code == 422
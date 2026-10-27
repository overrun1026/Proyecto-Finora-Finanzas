"""
Prueba la protección contra categorías duplicadas.
Crea una categoría y vuelve a intentar crearla con el mismo nombre.
Comprueba que la segunda solicitud devuelva un conflicto.
"""


def test_duplicate_category_conflict(client):
    first = client.post(
        "/api/v1/categories",
        json={"name": "Hogar"},
    )

    second = client.post(
        "/api/v1/categories",
        json={"name": "Hogar"},
    )

    assert first.status_code == 201
    assert second.status_code == 409
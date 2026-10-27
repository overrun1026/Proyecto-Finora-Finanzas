"""
Comprueba la creación de metas y el registro de aportes.
Verifica el progreso acumulado de una meta de ahorro.
Confirma que los aportes no se sumen a los ingresos del resumen.
"""


def test_savings_contribution_is_separate(client):
    goal_response = client.post(
        "/api/v1/savings-goals",
        json={
            "name": "Portátil",
            "target_amount": "2000000.00",
        },
    )

    assert goal_response.status_code == 201
    goal_id = goal_response.json()["id"]

    contribution_response = client.post(
        f"/api/v1/savings-goals/{goal_id}/contributions",
        json={
            "amount": "150000.00",
            "contribution_date": "2026-10-05",
        },
    )

    assert contribution_response.status_code == 201

    goal = client.get(
        f"/api/v1/savings-goals/{goal_id}"
    ).json()

    assert goal["saved_amount"] == "150000.00"

    summary = client.get("/api/v1/finance/summary").json()

    assert summary["total_income"] == "0.00"
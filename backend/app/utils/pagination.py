"""
Define parámetros reutilizables para paginar resultados.
limit establece el máximo de elementos y offset indica cuántos omitir.
Los límites ayudan a mantener respuestas controladas.
"""

from fastapi import Query


def pagination_params(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> dict[str, int]:
    return {
        "limit": limit,
        "offset": offset,
    }
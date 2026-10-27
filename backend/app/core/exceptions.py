"""
Define las excepciones propias de la lógica de negocio.
Permite diferenciar recursos inexistentes, conflictos y validaciones.
La aplicación transforma estas excepciones en respuestas HTTP consistentes.
"""


class NotFoundError(Exception):
    """Se produce cuando un recurso solicitado no existe."""


class ConflictError(Exception):
    """Se produce cuando una operación entra en conflicto con datos existentes."""


class ValidationError(Exception):
    """Se produce cuando los datos incumplen una regla de negocio."""
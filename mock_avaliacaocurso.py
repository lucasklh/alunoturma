def avaliar_curso(id_curso: int, avaliacao: int) -> None:
    pass

def get_criterio(id_curso: int) -> tuple[int, list[dict]]:
    # Mock response: (error code, list of criterio dicts)
    return 0, [{"id_criterio": 1, "descricao": "Criterio 1"}, {"id_criterio": 2, "descricao": "Criterio 2"}]
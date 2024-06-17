def get_turmas_by_filial(id_filial: int) -> tuple[int, list[int]]:
    # Mock response: (error code, list of turma ids)
    return 0, [1, 2, 3]

def add_aula(id_turma: int, id_aula: int) -> tuple[int, None]:
    return 0, None

def del_aula(id_turma: int) -> tuple[int, None]:
    return 0, None

def get_aluno(id_aluno: int) -> tuple[int, dict]:
    # Mock response: (error code, aluno dict)
    return 0, {"id_aluno": id_aluno, "nome": "Aluno Teste", "horario": [8, 17], "filial_pref": 1}

def set_horario(id_aluno: int, horario_inicio: int, horario_fim: int) -> None:
    pass
def avaliar_aluno(id_aluno: int, avaliacao: int) -> None:
    pass

def get_resposta(id_aluno: int, id_avaliacao: int) -> tuple[int, dict]:
    # Mock response: (error code, resposta dict)
    return 0, {"id_aluno": id_aluno, "id_avaliacao": id_avaliacao, "resposta": "Resposta Teste"}
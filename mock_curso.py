def get_curso(id_curso: int) -> tuple[int, dict]:
    # Mock response: (error code, curso dict)
    return 0, {"id_curso": id_curso, "nome": "Curso Teste", "descricao": "Descrição do Curso Teste"}
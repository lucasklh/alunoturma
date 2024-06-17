# Mock implementations for the functions used in alunoturma.py

def get_turmas_by_curso(id_curso: int) -> tuple[int, list[int]]:
    """
    Mock function to get turmas by curso ID.
    Returns a tuple with an error code (0 for success) and a list of turma IDs.
    """
    # Mock data: Assuming each curso has 2 turmas
    turmas_by_curso = {
        1: [101, 102],
        2: [201, 202],
        3: [301, 302]
    }
    if id_curso in turmas_by_curso:
        return 0, turmas_by_curso[id_curso]
    else:
        return 7, []  # Error code 7 for "No turmas found"

def add_assunto(id_turma: int, assunto: str) -> int:
    """
    Mock function to add an assunto to a turma.
    Returns an error code (0 for success).
    """
    # Mock implementation: Always succeeds
    return 0

def del_assunto(id_turma: int, assunto: str) -> int:
    """
    Mock function to delete an assunto from a turma.
    Returns an error code (0 for success).
    """
    # Mock implementation: Always succeeds
    return 0

def get_curso_by_turma(id_turma: int) -> tuple[int, dict]:
    """
    Mock function to get curso details by turma ID.
    Returns a tuple with an error code (0 for success) and a dict with curso details.
    """
    # Mock data: Assuming each turma belongs to a curso
    curso_details_by_turma = {
        101: {"id_curso": 1, "nome": "Curso 1"},
        102: {"id_curso": 1, "nome": "Curso 1"},
        201: {"id_curso": 2, "nome": "Curso 2"},
        202: {"id_curso": 2, "nome": "Curso 2"},
        301: {"id_curso": 3, "nome": "Curso 3"},
        302: {"id_curso": 3, "nome": "Curso 3"}
    }
    if id_turma in curso_details_by_turma:
        return 0, curso_details_by_turma[id_turma]
    else:
        return 8, {}  # Error code 8 for "Curso not found"
from unittest.mock import MagicMock

# Creating a mock for the turma module with necessary functions
turma = MagicMock()

# Mocking functions as per requirements
turma.get_turma = MagicMock(return_value=(0, {"id": 1, "curso_id": 101, "is_online": True, "horario": [10, 12], "max_alunos": 30, "filial": 1}))
turma.is_ativa = MagicMock(return_value=(0, True))
turma.is_final = MagicMock(return_value=(0, False))
turma.get_turmas = MagicMock(return_value=(0, [{"id": 1, "curso_id": 101, "is_online": True, "horario": [10, 12], "max_alunos": 30, "filial": 1}]))
turma.add_turma = MagicMock(return_value=(0, 1))  # Assuming it returns the ID of the added turma
turma.del_turma = MagicMock(return_value=(0, None))  # Assuming 0 indicates success
import unittest
from unittest.mock import patch
import alunoturma
import datetime

class TestAlunoTurma(unittest.TestCase):
    @patch('alunoturma.os.path.exists')
    @patch('alunoturma._write_matriculas')
    def test_read_matriculas_file_not_exists(self, mock_write_matriculas, mock_exists):
        mock_exists.return_value = False
        alunoturma._read_matriculas()
        mock_write_matriculas.assert_called_once()

    @patch('alunoturma.json.load')
    @patch('alunoturma.open')
    @patch('alunoturma.os.path.exists')
    def test_read_matriculas_success(self, mock_exists, mock_open, mock_json_load):
        mock_exists.return_value = True
        alunoturma._read_matriculas()
        mock_open.assert_called_once_with(alunoturma._JSON_FILE_PATH, 'r')
        mock_json_load.assert_called_once()

    @patch('alunoturma.json.dump')
    @patch('alunoturma.open')
    @patch('alunoturma.os.makedirs')
    @patch('alunoturma.os.path.isdir')
    def test_write_matriculas(self, mock_isdir, mock_makedirs, mock_open, mock_json_dump):
        mock_isdir.return_value = False
        alunoturma._write_matriculas()
        mock_makedirs.assert_called_once_with(alunoturma._DATA_DIR_PATH)
        mock_open.assert_called_once_with(alunoturma._JSON_FILE_PATH, 'w')
        mock_json_dump.assert_called_once()

    def test_datetime_para_str(self):
        dt = datetime.datetime(2023, 1, 1, 12, 0)
        result = alunoturma._datetime_para_str(dt)
        self.assertEqual(result, "2023-01-01T12:00:00")

    def test_str_para_datetime(self):
        turma_dict = {"data_ini": "2023-01-01T12:00:00"}
        result = alunoturma._str_para_datetime(turma_dict)
        self.assertEqual(result["data_ini"], datetime.datetime(2023, 1, 1, 12, 0))

    @patch('alunoturma.is_cheia')
    def test_turmas_com_vagas(self, mock_is_cheia):
        mock_is_cheia.side_effect = [(0, False), (0, True)]
        result = alunoturma._turmas_com_vagas([1, 2])
        self.assertEqual(result, [1])

    @patch('alunoturma.cursoturma.get_turmas_by_curso')
    def test_turmas_do_curso(self, mock_get_turmas_by_curso):
        mock_get_turmas_by_curso.return_value = (0, [1, 2])
        result = alunoturma._turmas_do_curso([1, 2, 3], 1)
        self.assertEqual(result, [1, 2])

    @patch('alunoturma.filialturma.get_turmas_by_filial')
    def test_turmas_por_filial(self, mock_get_turmas_by_filial):
        mock_get_turmas_by_filial.return_value = (0, [1, 2])
        result = alunoturma._turmas_por_filial([1, 2, 3], 1)
        self.assertEqual(result, [1, 2])


    def test_get_matricula_original(self):
        alunoturma._matriculas = [{"id_turma": 1, "id_aluno": 1}, {"id_turma": 2, "id_aluno": 2}]
        result = alunoturma._get_matricula_original(1, 1)
        self.assertEqual(result, {"id_turma": 1, "id_aluno": 1})

if __name__ == '__main__':
    unittest.main()
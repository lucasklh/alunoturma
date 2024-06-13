import os, json, atexit, datetime
from .. import curso, aluno, turma
from .. import cursoturma, avaliacaocurso, alunoavaliacao

# Exportando funções de acesso
__all__ = ["add_matricula", "del_matricula", "get_turmas_by_aluno", "get_alunos_by_turma", 
           "get_faltas", "is_aprovado", "is_cheia"]

# Globais
_SCRIPT_DIR_PATH: str = os.path.dirname(os.path.realpath(__file__))
_DATA_DIR_PATH: str = os.path.join(_SCRIPT_DIR_PATH, "data")
_JSON_FILE_PATH: str = os.path.join(_DATA_DIR_PATH, "matriculas.json")

# [
#     {
#         "id_turma": int,
#         "id_aluno": int,
#         "faltas": int,
#         "data_matriculado": datetime
#     },
#     ...
# ]
# OBS: Os datetimes são armazenados como strings no formato ISO no json
_matriculas: list[dict] = []

# Funções internas
def _read_matriculas() -> None:
    """
    Lê o arquivo _JSON_FILE_PATH e carrega a lista _matriculas com seu conteúdo

    Se não existir, chama _write_matriculas parar criar um novo vazio
    """
    global _matriculas

    if not os.path.exists(_JSON_FILE_PATH):
        _write_matriculas()
        return

    try:
        with open(_JSON_FILE_PATH, 'r') as file:
            _matriculas = json.load(file, object_hook=_str_para_datetime)
    except Exception as e:
        print(f"Erro de I/O em _read_matriculas: {e}")

def _write_matriculas() -> None:
    """
    Faz o dump da lista _matriculas no arquivo _JSON_FILE_PATH

    Cria os arquivos necessários caso não existam, gerando uma lista vazia de matriculas
    """
    if not os.path.isdir(_DATA_DIR_PATH):
        os.makedirs(_DATA_DIR_PATH)

    try:
        with open(_JSON_FILE_PATH, 'w') as file:
            json.dump(_matriculas, file, indent=2, default=_datetime_para_str)
    except Exception as e:
        print(f"Erro de I/O em _write_matriculas: {e}")

def _datetime_para_str(dt: datetime.datetime) -> str:
    """
    Converte um objeto datetime para uma string armanezável em JSON

    Chamada pelo json.dump quando ele não sabe como serializar um objeto
    """
    if isinstance(dt, datetime.datetime):
        return dt.isoformat()

    print(f"Erro ao converter objeto de tipo {type(dt).__name__} para uma string de datetime")

def _str_para_datetime(turma_dict: dict) -> dict:
    """
    Converte uma string de datetime para um objeto datetime

    Chamada pelo json.load quando ele não sabe como desserializar um objeto
    """
    for key, value in turma_dict.items():
        if key == "data_ini" and isinstance(value, str):
            try:
                turma_dict[key] = datetime.datetime.fromisoformat(value)
            except ValueError:
                print(f"Erro ao converter {value} para datetime")

    return turma_dict

def _turmas_por_horario(turmas: list[dict], horario: tuple[int, int]) -> list[int]:
    """
    Filtra uma lista de dicts de turmas, retornando apenas as que estão dentro do horário indicado (inclusivo)
    """
    turmas_no_horario = []

    for turma_dict in turmas:
        if turma_dict["horario"][0] >= horario[0] and turma_dict["horario"][1] <= horario[1]:
            turmas_no_horario.append(turma_dict["id"])

    return turmas_no_horario

def _turmas_com_vagas(turmas: list[int]) -> list[int]:
    """
    Filtra uma lista de IDs de turmas, retornando apenas as que possuem pelo menos uma vaga
    """
    turmas_com_vagas = []
    
    for id_turma in turmas:
        if not is_cheia(id_turma)[1]:
            turmas_com_vagas.append(id_turma)
    
    return turmas_com_vagas

def _turmas_online(turmas: list[int]) -> list[int]:
    """
    Filtra uma lista de IDs de turmas, retornando apenas as que são online
    """
    turmas_online = []
    
    for id_turma in turmas:
        if turma.get_turma(id_turma)[1]["is_online"]:
            turmas_online.append(id_turma)
    
    return turmas_online

def _turmas_do_curso(turmas: list[int], id_curso: int) -> list[int]:
    """
    Filtra uma lista de IDs de turmas, retornando apenas as que são do curso indicado
    """
    err, turmas_curso = cursoturma.get_turmas_by_curso(id_curso)
    if err == 7:
        # Nenhuma turma encontrada para o curso
        turmas_curso = []
    
    turmas_curso_filtro = []
    
    for id_turma in turmas_curso:
        if id_turma in turmas:
            # Turma é do curso e estava na nossa lista de entrada
            turmas_curso_filtro.append(id_turma)
    
    return turmas_curso

# Funções de acesso
def is_cheia(id_turma: int) -> tuple[int, bool]:
    """
    Verifica se uma turma possui vagas disponíveis
    """
    err, turma_dict = turma.get_turma(id_turma)
    if err != 0:
        # Erro ao encontrar a turma
        return err, None # type: ignore
    
    err, turma_final = turma.is_final(id_turma)
    if turma_final:
        # Se a turma foi finalizada, com certeza está cheia
        return 0, True
    
    max_alunos = turma_dict["max_alunos"]
    qtd_alunos = len(get_alunos_by_turma(id_turma)[1])

    if qtd_alunos <= 0:
        # Turma vazia, isso não deveria acontecer
        return 28, None # type: ignore

	# Se a quantidade de alunos for maior ou igual ao máximo, a turma está cheia
    return 0, qtd_alunos >= max_alunos


def add_matricula(id_aluno: int, id_curso: int, quer_online: bool) -> tuple[int, None]:
    """
    Documentação
    """
    err, dict_aluno = aluno.get_aluno(id_aluno)
    if (err != 0):
        # Algum erro ao encontrar o aluno
        return err, None
    
    err, curso_dict = curso.get_curso(id_curso)
    if (err != 0):
        # Algum erro ao encontrar o curso
        return err, None
    
    # Verificar se existe alguma turma disponível para o aluno

    horario_disponivel: tuple[int, int] = dict_aluno["horario"]

    # Turmas existentes no horário disponível do aluno
    turmas: list[int] = _turmas_por_horario(turma.get_turmas()[1], horario_disponivel)

    # E que possuem uma vaga
    turmas = _turmas_com_vagas(turmas)

    # E que, caso o aluno deseje, sejam online
    if quer_online:
        turmas = _turmas_online(turmas)
    
    # E que sejam do curso desejado
    turmas = _turmas_do_curso(turmas, id_curso)
    

def del_matricula(id_turma: int, id_aluno: int) -> tuple[int, None]:
    """
    Documentação
    """
    raise NotImplementedError

def get_turmas_by_aluno(id_aluno: int) -> tuple[int, list[int]]:
    """
    Documentação
    """
    raise NotImplementedError

def get_alunos_by_turma(id_turma: int) -> tuple[int, list[int]]:
    """
    Documentação
    """
    raise NotImplementedError

def get_faltas(id_turma: int, id_aluno: int) -> tuple[int, int]:
    """
    Documentação
    """
    raise NotImplementedError

def is_aprovado(id_turma: int, id_aluno: int) -> tuple[int, bool]:
    """
    is_aprovado confere a aprovação de um aluno numa certa turma de curso.
    Caso o aluno esteja aprovado, retornara True, caso não, False.
    """

    # verifica as faltas do aluno no sistema
    faltas = get_faltas(id_turma, id_aluno)
    if faltas[0] != 0:
        return 27, False

    #encontra de que curso é a turma que este aluno se encontra
    turma_curso = cursoturma.get_curso_by_turma(id_turma)
    if turma_curso[0] != 0:
        return 6, False
        
    #pega as informações necessárias para descobrir se o aluno está aprovado a partir do curso feito
    curso = curso.get_curso(turma_curso[1])
    if curso[0] != 0:
        return 27, True

    #verifica a duração do curso e compara se passou pelo minimo de presença
    faltas_permitidas = curso[1]["duracao_semanas"]
    if faltas > 0.3 * faltas_permitidas:
        return 0, False
        
    #obtem os id's de provas aplicadas para esse curso nas turmas
    avaliacoes = avaliacaocurso.get_criterio(curso[1]["id"])
    if avaliacoes[0] != 0:
        return 26, False

    #armazena todas as notas de tiradas pelo aluno neste curso
    notas_recebidas = []

    #percorre cada id e busca a nota encontrada pelo aluno na avaliação
    for i in range(len(avaliacoes[1])):
        resposta_aluno = alunoavaliacao.get_resposta(id_aluno,avaliacoes[1][i])
        if resposta_aluno[0] != 0:
            return 13, False
        notas_recebidas.append(resposta_aluno[1]["nota"])

    #faz o somatório dos valores da lista e divide pelo número de 
    #avaliações que constam ter sido aplicadas para este curso
    
    media = sum(notas_recebidas) / len(avaliacoes[1])

    #se a media for maior que 7, o aluno está aprovado
    if media >= 7:
        return 0, True

# Setup
# Popular lista de turmas
_read_matriculas()

# Salvar turmas ao final do programa
atexit.register(_write_matriculas);
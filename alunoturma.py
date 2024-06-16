import os, json, atexit, datetime, copy
from .. import curso, aluno, turma
from .. import cursoturma, avaliacaocurso, alunoavaliacao, filialturma

# Exportando funções de acesso
__all__ = ["add_matricula", "del_matricula", "get_turmas_by_aluno", "get_alunos_by_turma", 
           "get_faltas", "is_aprovado", "is_cheia", "get_matricula", "set_faltas"]

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

def _turmas_por_filial(turmas: list[int], id_filial: int) -> list[int]:
    """
    Filtra uma lista de IDs de turmas, retornando apenas as que são da filial indicada
    """
    err, turmas_filial = filialturma.get_turmas_by_filial(id_filial)
    if err != 0:
        # Nenhuma turma encontrada para a filial
        turmas_filial = []
    
    turmas_filial_filtro = []
    
    for id_turma in turmas_filial:
        if id_turma in turmas:
            # Turma é da filial e estava na nossa lista de entrada
            turmas_filial_filtro.append(id_turma)
    
    return turmas_filial_filtro

def _turma_com_horario_mais_cedo(turmas: list[int]) -> int:
    """
    Retorna o ID da turma que começa mais cedo dentre as turmas fornecidas,
    ou a primeira turma online encontrada
    """
    assert turmas, "Lista de turmas não deveria estar vazia"

    horario_mais_cedo = 24
    turma_mais_cedo = None

    for id_turma in turmas:
        turma_dict = turma.get_turma(id_turma)[1]

        if turma_dict["is_online"]:
            # Se for online, escolher a primeira encontrada
            return id_turma
        
        if turma_dict["horario"][0] < horario_mais_cedo:
            # Salva a turma mais cedo encontrada até agora
            horario_mais_cedo = turma_dict["horario"][0]
            turma_mais_cedo = id_turma
    
    assert turma_mais_cedo, "Nenhuma turma foi escolhida como a mais cedo"
    
    return turma_mais_cedo

def _atualiza_horario_aluno(id_aluno: int, id_turma: int) -> None:
    """
    Atualiza o horário de disponibilidade de um aluno, removendo tudo acima do horário da turma
    """
    turma_dict = turma.get_turma(id_turma)[1]
    aluno_dict = aluno.get_aluno(id_aluno)[1]

    if turma_dict["is_online"]:
        # Se for online, não há o que atualizar
        return

    horario_aluno: list[int] = aluno_dict["horario"]
    horario_turma: list[int] = turma_dict["horario"]
    novo_horario: list[int] = [horario_turma[1], horario_aluno[1]]

    aluno.set_horario(id_aluno, novo_horario[0], novo_horario[1])

def _get_matricula_original(id_turma: int, id_aluno: int) -> dict:
    """
    Retorna uma referência à matrícula de um aluno em uma turma.
    Serve para atualizar a matrícula no dicionário interno, assume que a matrícula existe.
    """
    for matricula in _matriculas:
        if matricula["id_turma"] == id_turma and matricula["id_aluno"] == id_aluno:
            return matricula

    return None # type: ignore

# Funções de acesso
def is_cheia(id_turma: int) -> tuple[int, bool]:
    """
    Verifica se uma turma possui vagas disponíveis
    """
    err, turma_dict = turma.get_turma(id_turma)
    if err != 0:
        # Erro ao encontrar a turma
        return err, None # type: ignore
    
    err, turma_ativa = turma.is_ativa(id_turma)
    if turma_ativa and turma_dict["is_online"]:
        # Se a turma for online e estiver ativa, sempre haverão vagas
        return 0, False
    
    err, turma_final = turma.is_final(id_turma)
    if turma_final:
        # Se a turma foi finalizada, e não é online ativa, com certeza está cheia
        return 0, True
    
    max_alunos = turma_dict["max_alunos"]
    qtd_alunos = len(get_alunos_by_turma(id_turma)[1])

    if qtd_alunos <= 0:
        # Turma vazia, isso não deveria acontecer
        return 26, None # type: ignore

	# Se a quantidade de alunos for maior ou igual ao máximo, a turma está cheia
    # Na verdade não deveria ser maior
    return 0, qtd_alunos >= max_alunos

def add_matricula(id_aluno: int, id_curso: int, quer_online: bool) -> tuple[int, None]:
    """
    Matricula o aluno em alguma turma de um curso específico. Se não houver uma turma disponível,
    cria uma nova proposta de turma.
    """
    err, aluno_dict = aluno.get_aluno(id_aluno)
    if err != 0:
        # Algum erro ao encontrar o aluno
        return err, None
    
    err, curso_dict = curso.get_curso(id_curso)
    if err != 0:
        # Algum erro ao encontrar o curso
        return err, None
    
    # Verifica se existe alguma turma disponível para o aluno

    # Turmas existentes no horário disponível do aluno
    turmas_candidatas: list[int] = _turmas_por_horario(turma.get_turmas()[1], aluno_dict["horario"])

    # E que possuem uma vaga
    turmas_candidatas = _turmas_com_vagas(turmas_candidatas)

    # E que, caso o aluno deseje, sejam online
    if quer_online:
        turmas_candidatas = _turmas_online(turmas_candidatas)
    # Ou então, que sejam da filial de preferência do aluno
    else:
        turmas_candidatas = _turmas_por_filial(turmas_candidatas, aluno_dict["filial_pref"])
    
    # E que sejam do curso desejado
    turmas_candidatas = _turmas_do_curso(turmas_candidatas, id_curso)

    # Após filtrar, se houver alguma turma disponível, matricula o aluno na mais cedo
    if turmas_candidatas:
        turma_matricula = _turma_com_horario_mais_cedo(turmas_candidatas)
        
        nova_matricula = {
            "id_turma": turma_matricula,
            "id_aluno": id_aluno,
            "faltas": 0,
            "data_matriculado": datetime.datetime.now()
        }
        _matriculas.append(nova_matricula)

        # Atualiza horário do aluno, se não for online
        _atualiza_horario_aluno(id_aluno, turma_matricula)

        return 0, None
    # Caso contrário, abrir uma nova turma para o aluno
    else:
        hora_inicio: int = aluno_dict["horario"][0]
        hora_fim: int = hora_inicio + curso_dict["carga_horaria"]

        err, nova_turma = turma.add_turma(quer_online, curso_dict["duracao_semanas"], 
                                          [hora_inicio, hora_fim])
        if err != 0:
            # Algum erro ao criar a nova turma
            return err, None
        
        # Adiciona a nova turma em Curso-Turma e Filial-Turma
        err, _ = cursoturma.add_assunto(nova_turma, id_curso)
        if err != 0:
            # Algum erro ao adicionar a turma ao curso
            turma.del_turma(nova_turma)
            return err, None
        
        err, _ = filialturma.add_aula(aluno_dict["filial_pref"], nova_turma)
        if err != 0:
            # Algum erro ao adicionar a turma à filial
            cursoturma.del_assunto(nova_turma)
            turma.del_turma(nova_turma)
            return err, None
        
        # Matricula o aluno e atualiza seu horário
        nova_matricula = {
            "id_turma": nova_turma,
            "id_aluno": id_aluno,
            "faltas": 0,
            "data_matriculado": datetime.datetime.now()
        }
        _matriculas.append(nova_matricula)

        _atualiza_horario_aluno(id_aluno, nova_turma)

        return 0, None

def del_matricula(id_turma: int, id_aluno: int) -> tuple[int, None]:
    """
    Remove uma matrícula. Se a turma esvaziar, deleta a turma.
    """
    err, matricula = get_matricula(id_turma, id_aluno)
    if err != 0:
        # Algum erro ao encontrar a matrícula
        return err, None
    
    if turma.is_final(id_turma)[1] and not turma.is_ativa(id_turma)[1]:
        # Turma já se formou, não é possível remover matrícula
        return 29, None
    
    # Remover matrícula
    _matriculas.remove(matricula)

    err, _ = get_alunos_by_turma(id_turma)
    if err == 26:
        # Proposta de turma esvaziou, deletar turma em Filial-Turma, Curso-Turma e Turma
        err, _ = filialturma.del_aula(id_turma)
        if err != 0:
            # Algum erro ao deletar a turma da filial
            return err, None

        err, _ = cursoturma.del_assunto(id_turma)
        if err != 0:
            # Algum erro ao deletar a turma do curso
            return err, None
        
        err, _ = turma.del_turma(id_turma)
        if err != 0:
            # Algum erro ao deletar a turma
            return err, None
    
    return 0, None

def get_turmas_by_aluno(id_aluno: int) -> tuple[int, list[int]]:
    """
    Retorna todas turmas em que um aluno está matriculado
    """
    err, _ = aluno.get_aluno(id_aluno)
    if err != 0:
        # Algum erro ao encontrar o aluno
        return err, None # type: ignore

    turmas = []
    
    for matricula in _matriculas:
        if matricula["id_aluno"] == id_aluno:
            turmas.append(matricula["id_turma"])
    
    if turmas:
        return 0, turmas
    else:
        # Nenhuma matrícula encontrada para o aluno
        return 28, None # type: ignore

def get_alunos_by_turma(id_turma: int) -> tuple[int, list[int]]:
    """
    Retorna todos alunos matriculados em uma turma
    """
    err, _ = turma.get_turma(id_turma)
    if err != 0:
        # Algum erro ao encontrar a turma
        return err, None # type: ignore
    
    alunos = []

    for matricula in _matriculas:
        if matricula["id_turma"] == id_turma:
            alunos.append(matricula["id_aluno"])
    
    if alunos:
        return 0, alunos
    else:
        # Nenhum aluno matriculado na turma, não deveria acontecer
        return 26, None # type: ignore

def get_matricula(id_turma: int, id_aluno: int) -> tuple[int, dict]:
    """
    Retorna os atributos de uma certa matrícula de aluno em turma
    """
    err, _ = aluno.get_aluno(id_aluno)
    if err != 0:
        # Algum erro ao encontrar o aluno
        return err, None # type: ignore

    err, _ = turma.get_turma(id_turma)
    if err != 0:
        # Algum erro ao encontrar a turma
        return err, None # type: ignore
    
    for matricula in _matriculas:
        if matricula["id_turma"] == id_turma and matricula["id_aluno"] == id_aluno:
            return 0, copy.deepcopy(matricula)
    
    return 27, None # type: ignore

def get_faltas(id_turma: int, id_aluno: int) -> tuple[int, int]:
    """
    Retorna a quantidade de faltas de um aluno em uma turma
    """
    err, matricula = get_matricula(id_turma, id_aluno)
    if err != 0:
        # Algum erro ao encontrar a matrícula
        return err, None # type: ignore
    
    return matricula["faltas"]

def set_faltas(id_turma: int, id_aluno: int, faltas: int) -> tuple[int, None]:
    """
    Atualiza a quantidade de faltas de um aluno em uma turma
    """
    err, _ = get_matricula(id_turma, id_aluno)
    if err != 0:
        # Algum erro ao encontrar a matrícula
        return err, None
    
    _, turma_dict = turma.get_turma(id_turma)
    if turma_dict["is_online"]:
        # Turmas online não contabilizam presença
        return 43, None
    
    matricula = _get_matricula_original(id_turma, id_aluno)
    matricula["faltas"] = faltas

    return 0, None

def is_aprovado(id_turma: int, id_aluno: int) -> tuple[int, bool | None]:
    """
    Retorna se um aluno foi aprovado em uma turma, ou None se for indeterminado
    """
    err, _ = turma.get_turma(id_turma)
    if err != 0:
        # Algum erro ao encontrar a turma
        return err, None
    
    err, _ = aluno.get_aluno(id_aluno)
    if err != 0:
        # Algum erro ao encontrar o aluno
        return err, None

    # Verifica se a turma já encerrou
    
    if not (turma.is_final(id_turma)[1] and not turma.is_ativa(id_turma)[1]):
        # Turma ainda está tendo aulas
        return 0, None

    # Verifica se foi reprovado por falta, de acordo com a duração do curso

    err, faltas = get_faltas(id_turma, id_aluno)
    if err != 0:
        # Algum erro ao recuperar as faltas do aluno na turma
        return err, None

    err, curso_da_turma = cursoturma.get_curso_by_turma(id_turma)
    if err != 0:
        # Algum erro ao encontrar o curso da turma
        return err, None
        
    err, curso_dict = curso.get_curso(curso_da_turma)
    if err != 0:
        # Algum erro ao encontrar o curso
        return err, None

    num_aulas = curso_dict["duracao_semanas"]
    if faltas > (.3 * num_aulas):
        # Reprovado por faltas
        return 0, False
    
    # Verifica se foi reprovado por média, de acordo com as avaliações feitas
        
    err, avs_criterio = avaliacaocurso.get_criterio(curso_da_turma)
    if err != 0:
        # Algum erro ao encontrar as avaliações do curso
        return err, None

    notas_recebidas = []

    for aval in avs_criterio:
        err, resposta_aluno = alunoavaliacao.get_resposta(id_aluno, aval)
        if err != 0:
            # Algum erro ao encontrar a resposta do aluno
            return err, None
        
        notas_recebidas.append(resposta_aluno["nota"])

    media = sum(notas_recebidas) / len(avs_criterio)

    # Aprovado ou reprovado por média
    return 0, media >= 7.0

# Setup
# Popular lista de turmas
_read_matriculas()

# Salvar turmas ao final do programa
atexit.register(_write_matriculas)
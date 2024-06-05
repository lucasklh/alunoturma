import os, json, atexit, datetime

# Exportando funções de acesso
__all__ = []

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
#         "nota_final": float,
#         "is_aprovado": bool
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

# Funções de acesso

# Setup
# Popular lista de turmas
_read_matriculas()

# Salvar turmas ao final do programa
atexit.register(_write_matriculas)
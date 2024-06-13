# Como utilizar

No diretório imediatamente acima do seu módulo, execute:

`git clone https://github.com/bathwaterpizza/alunoturma`

Depois você pode utilizar as funções de turma com o import:

```Python
from .. import alunoturma

turma.is_cheia(id_turma = 11)
```

**OBS:** Para utilizar imports relativos, seu módulo também precisa fazer parte de um package, ou seja, o diretório do módulo deve possuir um arquivo `__init__.py` assim como o nosso.

Alternativamente, se o diretório acima do seu módulo também for um repositório, como o principal, você pode adicionar turma como submódulo:

`git submodule add https://github.com/bathwaterpizza/alunoturma`

## Dependências

Python 3.9+

# Documentação adicional

## add_matricula

Essa função é chamada quando um aluno deseja entrar em uma turma de um certo curso. Ela aplica uma série de filtros às turmas existentes, para verificar se existe alguma turma disponível, de acordo com as necessidades do aluno. Caso não exista, cria uma nova proposta de turma, contendo o aluno.

O módulo aluno é acessado para se obter os parâmetros de horário e filial de preferência. Após o aluno ser inserido em uma turma, seu horário é atualizado utilizando `set_horario` para refletir sua nova disponibilidade.

## is_cheia

Verifica se uma turma possui vagas para novos alunos ou não.

Lembrando que turmas online possuem vagas infinitas, enquanto estiverem ativas.

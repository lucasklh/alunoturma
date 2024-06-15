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

Essa função é chamada quando um aluno deseja se matricular em um certo curso. Ela aplica uma série de filtros às turmas existentes, para verificar se existe alguma turma disponível, de acordo com as necessidades do aluno. Caso não exista, cria uma nova proposta de turma, contendo o aluno.

O módulo aluno é acessado para se obter os parâmetros de horário e filial de preferência. Após o aluno ser inserido em uma turma, seu horário é atualizado utilizando `set_horario` para refletir sua nova disponibilidade. Se a turma for online, não há atualização, pois as aulas não têm horário fixo.

Conforme combinado com o cliente, não vamos considerar prioridade de matrícula para alunos cursando alguma formação.

### Atualização de horário

Lembrando que, por questões de simplificação, os horários de alunos, professores e aulas são representados por uma simples faixa de 24h, representada por dois inteiros de início e fim. Não há a noção de dias da semana, então podemos pensar nessa faixa como o horário em que algo acontece uma vez, semanalmente.

Como temos apenas uma range de horário final e inicial, não podemos separar essa faixa em duas partes. Por isso, ao aluno ser inserido em uma turma, **cortamos o horário disponível dele a partir do fim do alocado**, de forma que qualquer horário livre antes do que foi alocado é descartado. Também por esse motivo, o `add_matricula` sempre procura alocar o horário mais cedo possível. Exemplo:

- Aluno possui disponibilidade de **8h às 16h**
- Uma turma compatível é encontrada, com aulas de **10h às 12h**
- Após a matrícula, o novo horário disponível do aluno será de **12h às 16h**
  - Ou seja, o horário livre de **8h às 10h** foi descartado

## is_cheia

Verifica se uma turma possui vagas para novos alunos ou não.

Lembrando que turmas online possuem vagas infinitas, enquanto estiverem ativas.

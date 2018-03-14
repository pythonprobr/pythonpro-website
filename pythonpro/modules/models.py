from django.db import models
from django.urls import reverse
from ordered_model.models import OrderedModel

from pythonpro.modules.content import ContentWithTitleMixin, gen_breadcrum

ALL = {}


class Module(ContentWithTitleMixin):
    def __init__(self, title, slug, objective, description, target, *pre_requirements):
        self.slug = slug
        self.pre_requirements = pre_requirements
        self.target = target
        self.description = description
        self.objective = objective
        self.title = title
        ALL[self.slug] = self

    def get_absolute_url(self):
        return reverse('modules:detail', kwargs={'slug': self.slug})

    def parent(self):
        None


PYTHON_BIRDS = Module(
    'Python Birds',
    'python-birds',
    'Introduzir programação Procedural e Orientação a Objetos em Python.',
    (
        'Durante o módulo será desenvolvida uma versão simplificada do jogo Angry Birds. Assim o aluno aprenderá os '
        'conceitos ao mesmo tempo em que implementa um projeto prático.'
    ),
    'Alunos com nenhuma ou pouca experiência.'
)

PYTHONIC_OBJECTS = Module(
    'Objetos Pythônicos',
    'objetos-pythonicos',
    'Aprofundar o conhecimento de Orientação a Objetos tendo em vista as peculiaridade do Python.',
    (
        'Aprofundamento no conhecimento da linguagem: tipagem dinâmica, protocolos versus interfaces, '
        'classes abstratas, '
        'herança múltipla e sobrecarga de operadores são alguns dos temas cobertos.'

    ),
    (
        'Alunos que conhecem OO e estão começando com Python ou que já usam a linguagem no dia-a-dia, mas querem '
        'aperfeiçoar o modo pythônico de programar.'
    ),
    PYTHON_BIRDS
)

PYTOOLS = Module(
    'PyTools',
    'pytools',
    'Apresentar um conjunto de ferramentas básico, mas poderoso, que Pythonistas experientes usam no dia-a-dia.',
    (
        'Nesse módulo será abordada a leitura e escrita de arquivos, com definição de unicode e encode. Instalação e '
        'criação de bibliotecas utilizando pip, virtualenv e pypi. Criação de testes automáticos com o framework pytest'
    ),
    'Alunos iniciantes de Python que desejam conhecer as ferramentas de seu ecossistema.',
    PYTHON_BIRDS
)

PYTHON_FOR_PYTHONISTS = Module(
    'Python para Pythonistas',
    'python-para-pythonistas',
    'Curso para desvendar remódulos avançados da linguagem, em geral utilizados em diversos frameworks.',
    (
        'Este módulo vai te mostrar o modo pythônico de abordar concorrência, escalabilidade e metaprogramação, '
        'aproveitando o que Python tem de mais avançado. '
    ),
    'Alunos com conhecimento intermediário/avançado de Python, que já programam com a linguagem em seu dia-a-dia',
    PYTHON_BIRDS,
    PYTHONIC_OBJECTS
)

PYTHON_WEB = Module(
    'Python Web',
    'python-web',
    'Construir uma aplicação web utilizando Flask e SQLAlchemy',
    (
        'Nesse módulo será construído uma aplicação web real utilizando o framework web Flask o o ORM SQLAlchemy.'
        'Ele serve como módulo prático onde todos os conceitos vistos nos demais módulos são colados em prática.'
    ),
    (
        'Alunos com conhecimento avançado de Python que desejam desenvolver para web.'
    ),
    PYTHON_BIRDS, PYTHONIC_OBJECTS, PYTHON_FOR_PYTHONISTS
)

PYTHON_PATTERNS = Module(
    'Python Patterns',
    'python-patterns',
    (
        'Apresentar técnicas de programação orientada a objetos e padrões de projeto otimizados para as '
        'características dinâmicas da linguagem Python.'),
    (
        'Neste módulo analisamos as características específicas dos objetos, classes e interfaces em Python, '
        'e aplicamos esse entendimento na análise e refatoração de vários padrões de projeto clássicos do livro '
        'Padrões de Projeto de Gamma, Helm, Johnson e Vlissides. Além de padrões arquiteturais, também estudamos '
        'padrões de codificação em uma escala menor, relacionados ao gerenciamento de atributos e usos dinâmicos de '
        'classes.'

    ),
    (
        'Alunos com firmes conceitos de programação orientada a objetos.'

    ),
    PYTHON_BIRDS, PYTHONIC_OBJECTS, PYTHON_FOR_PYTHONISTS
)

TECH_INTERVIEW = Module(
    'Entrevistas Técnicas',
    'entrevistas-tecnicas',
    (
        'Aprender como ocorre o processo seletivo de empresas gringas e as questões técnicas que são feitas na '
        'entrevista técnica.'),
    (
        'Nesse módulo será passada uma visão geral sobre os processos seletivos de empresas estrangeiras: envio de '
        'currículo, análise de algorítmos, estruturas de dados e resolução de questões.'
    ),
    (
        'Alunos com conhecimento avançado de Python que pretendem prestar processos seletivos e/ou avaliar '
        'quantitativamente diferentes algorítimos'

    ),
    PYTHON_BIRDS, PYTHONIC_OBJECTS, PYTHON_FOR_PYTHONISTS
)


class Section(OrderedModel):
    title = models.CharField(max_length=50)
    description = models.TextField()
    slug = models.SlugField(unique=True)
    _module_slug = models.SlugField(choices=((m.slug, m.title) for m in ALL.values()))
    order_with_respect_to = '_module_slug'

    class Meta:
        ordering = ['_module_slug', 'order']

    def get_absolute_url(self):
        return reverse('sections:detail', kwargs={'slug': self.slug})

    def parent(self):
        return ALL[self._module_slug]

    def breadcrumb(self):
        return gen_breadcrum(self)

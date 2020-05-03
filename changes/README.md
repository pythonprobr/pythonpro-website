# Gerando changelog com o Towncrier

* [Link Pypi Towncrier](https://pypi.org/project/towncrier/)

O Towncrier possui alguns tipos padrão de fragmentos de notícias, significados pela extensão do arquivo. Esses são:
```
.feature: significando um novo recurso.
.bugfix: significando uma correção de bug.
.doc: significando uma melhoria na documentação.
.removal: significando uma descontinuação ou remoção da API pública.
.misc: um ticket foi fechado, mas não interessa aos usuários.
```
Exemplo de um arquivo 25.feature, em que 25 é o número do problema e .feature e o tipo de problema, a confirmação do problema ocorre dentro do arquivo.
A versão será lida em __init__ dentro de alterações

Comando:
```
towncrier
Is it okay if I remove those files? [Y/n]:
```
__Y__ - remove os arquivos  
__n__ - mantem os arquivos
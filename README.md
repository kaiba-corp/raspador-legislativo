# Raspador Legislativo

Este repositório contém um conjunto de ferramentas e scripts para raspar dados abertos de fontes públicas do legislativo brasileiro. O objetivo é automatizar a coleta de informações sobre projetos de lei e a agenda de tramitação, com base em palavras-chave definidas. A longo prazo, o projeto visa integrar esses dados ao [Prysmo](https://app.prysmo.com/), permitindo uma análise mais eficiente e acessível da legislação em andamento.

## Configurações

Copie os arquivos de configuração e edite-os de acordo com o desejado:

```sh
copy .env.sample .env
copy secrets\keywords.json.sample secrets\keywords.json
```

### Coletando todos os projetos de lei

Não configurar a variável `KEYWORDS` faz com que o _Raspador_ colete dados
sobre **todos** os projetos de lei em tramitação desde `START_DATE`.

**Obs**: A _spider_ do Senado Federal coleta dados a partir do ano em `START_DATE`,
não considerando o mês e o dia.


## Instalação em container (com Docker)

Requer [Docker](https://docs.docker.com/install/) e
[Docker Compose](https://docs.docker.com/compose/install/).

Para rodar todos os raspadores:

```sh
docker-compose run --rm scrapy scrapy crawl camara
docker-compose run --rm scrapy scrapy crawl senado
docker-compose run --rm scrapy scrapy crawl agenda_camara
docker-compose run --rm scrapy scrapy crawl agenda_senado
```

Verifique o resultado no diretório `data/`.

### Testes no container

```sh
docker-compose run --rm scrapy py.test
```

## Instalação local (sem Docker)

Requer [Python](https://python.org) 3.13.0 com [venv](https://docs.python.org/pt-br/3/library/venv.html).

Entre no _venv_ e instale as dependências:

```sh
cd ../raspador-legislativo
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Para rodar todos os raspadores:

```sh
scrapy crawl camara
scrapy crawl senado
scrapy crawl agenda_camara
scrapy crawl agenda_senado
```

Verifique o resultado no diretório `data/`.

### Testes locais

```sh
py.test
```

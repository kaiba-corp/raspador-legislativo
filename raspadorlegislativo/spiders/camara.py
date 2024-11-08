import json
import re
from datetime import datetime

from markdownify import markdownify
from scrapy import Request, Spider
from pytz import timezone

from raspadorlegislativo import settings
from raspadorlegislativo.items import Bill, Event
from raspadorlegislativo.requests import JsonRequest
from raspadorlegislativo.spiders import BillSpider


class CamaraMixin:

    def request_all_remaining_pages(self, response):
        contents = json.loads(response.text)
        links = contents.get('links', tuple())
        pattern = r'pagina=(?P<last>\d+)'
        for link in links:
            if link.get('rel') == 'last':
                url = link.get('href')
                match = re.search(pattern, url)
                last = int(match.group('last'))
                urls = (
                    re.sub(pattern, f'pagina={page}', url)
                    for page in range(2, last + 1)
                )
                return (JsonRequest(url) for url in urls)


class CamaraSpider(BillSpider, CamaraMixin):
    """Raspa os dados da lista de todas as matérias que estão tramitando na
    Câmara, filtradas por Projeto de Lei."""

    name = 'camara'
    subjects = ('PL', 'PLS', 'PEC')
    urls = {
        'list': (
            'https://dadosabertos.camara.leg.br/'
            'api/v2/proposicoes?siglaTipo={}&dataInicio={}&itens=100'
        ),
        'human': (
            'http://www.camara.gov.br/'
            'proposicoesWeb/fichadetramitacao?idProposicao={}'
        )
    }

    def start_requests(self):
        subjects = ','.join(self.subjects)
        url = self.urls['list'].format(subjects, settings.START_DATE)
        yield JsonRequest(url, meta={'is_first': True})

    def parse(self, response):
        """Parser p/ página que lista todos os PLs da Câmara"""
        contents = json.loads(response.text)
        bills = contents.get('dados', tuple())
        for bill in bills:
            yield JsonRequest(bill.get('uri'), self.parse_bill, errback=self.error)

        if 'is_first' in response.meta:
            yield from self.request_all_remaining_pages(response)

    def parse_bill(self, response):
        """Parser p/ página do PL. Encadeia o parser da página de autoria."""
        bill = json.loads(response.text).get('dados', {})

        keywords = bill.get('keywords')
        if not isinstance(keywords, str):
            keywords = ''

        data = {
            'palavras_chave': set(),  # include matching keywords in this list
            'palavras_chave_originais': keywords.strip(' .\n\t\r'),
            'nome': '{} {}'.format(bill.get('siglaTipo'), bill.get('numero')),
            'id_site': bill.get('id'),
            'apresentacao': bill.get('dataApresentacao')[:10],  # 10 chars date
            'ementa': bill.get('ementa'),
            'origem': 'CA',
            'url': self.urls['human'].format(bill.get('id'))
        }
        data = self.collect_keywords(data, data.get('ementa', ''))
        data = self.collect_keywords(data, data.get('keywords', ''))

        urls = {
            'local': bill.get('statusProposicao', {}).get('uriOrgao'),
            'pdf': bill.get('urlInteiroTeor')
        }

        meta = {'bill': data, 'urls': urls}
        url = bill.get('uriAutores')
        if url:
            yield JsonRequest(url, self.parse_authorship, meta=meta, errback=self.error)
        else:
            yield self.item(response)

    def parse_authorship(self, response):
        """Parser p/ página de autoria. Encadeia parser p/ página de local."""

        def get_ids(authors):
            for author in authors:
                uri = author.get('uri') or ''
                matches = re.findall(r'\d+$', uri)
                if matches:
                    *_, author_id = matches
                    if author_id:
                        yield author_id

        data = json.loads(response.text)
        authors = data.get('dados')
        authorship = (author.get('nome') for author in authors)
        response.meta['bill']['autoria'] = ', '.join(authorship)
        response.meta['bill']['autoria_ids'] = ', '.join(get_ids(authors))

        url = response.meta['urls'].pop('local')
        if url:
            yield JsonRequest(url, self.parse_local, meta=response.meta, errback=self.error)
        else:
            yield self.item(response)

    def parse_local(self, response):
        """Parser p/ página de local. Encadeia parser p/ inteiro teor."""
        local = json.loads(response.text).get('dados', {})
        response.meta['bill']['local'] = local.get('nome')

        url = response.meta['urls'].pop('pdf')
        if url:
            yield Request(url, self.parse_pdf, meta=response.meta, errback=self.error)
        else:
            yield self.item(response)

    def parse_pdf(self, response):
        """Parser p/ PDF inteiro teor."""
        with self.text_from_pdf(response) as text:
            response.meta['bill'] = self.collect_keywords(
                response.meta['bill'],
                text
            )

        yield self.item(response)

    def item(self, response):
        response.meta['bill']['palavras_chave'] = \
            ', '.join(response.meta['bill']['palavras_chave'])

        if not settings.MATCHERS:  # catch all mode
            return Bill(response.meta['bill'])

        if response.meta['bill']['palavras_chave']:  # looking for keywords
            return Bill(response.meta['bill'])


class AgendaCamaraSpider(Spider, CamaraMixin):
    name = 'agenda_camara'
    allowed_domains = ('camara.leg.br',)
    urls = {
        'api': 'https://dadosabertos.camara.leg.br/api/v2/eventos',
        'details': (
            'http://www.camara.leg.br/'
            'internet/ordemdodia/ordemDetalheReuniaoCom.asp?codReuniao={}'
        )
    }

    def start_requests(self):
        yield JsonRequest(self.urls['api'], meta={'is_first': True})

    def parse(self, response):
        """Parser para página que lista todos os eventos da Câmara"""
        contents = json.loads(response.text)
        for event in contents.get('dados', tuple()):
            yield Request(
                self.urls['details'].format(event['id']),
                callback=self.parse_details,
                meta={'event': event}
            )

        if 'is_first' in response.meta:
            yield from self.request_all_remaining_pages(response)

    def parse_details(self, response):
        """Parse para a página HTML com detalhes de um evento da agenda"""
        venues, venue = response.meta['event']['orgaos'], None
        for _venue in venues:
            if _venue['nome']:
                venue = _venue
                break

        if venue:
            yield Event(
                origem='CA',
                id_site=response.meta['event']['id'],
                data=self.parse_date(response.meta['event']),
                descricao=self.parse_description(response),
                local=venue['nome']
            )

    @staticmethod
    def remove_node(context, css_selector):
        """Remove um nó do HTML com base em um seletor CSS"""
        for element in context.css(css_selector):
            element.root.getparent().remove(element.root)
        return context

    def parse_description(self, response):
        """Trata o texto da descrição com base no HTML de detalhe do evento"""
        if bool(response.css('.caixaCOnteudo')):
            *_, description = response.css('.caixaCOnteudo')

            # remove nós indesejados do HTML
            for selector in ('style', '.vejaTambem'):
                description = self.remove_node(description, selector)

            # remove caracteres indesejados do HTML
            description = description.extract()
            for char in ('\n', '\t', '\r'):
                description.replace(char, '')

            # remove espaços do início das linhas
            description = markdownify(description)
            return '\n'.join(line.strip() for line in description.split('\n'))

        description = ' em branco'
        return description

    @staticmethod
    def parse_date(event):
        naive = datetime.strptime(event['dataHoraInicio'], '%Y-%m-%dT%H:%M')
        return naive.strftime('%Y-%m-%d')

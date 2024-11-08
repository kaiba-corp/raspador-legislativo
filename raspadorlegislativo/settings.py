import logging
from pathlib import Path

from decouple import config

from raspadorlegislativo.matchers import keyword_matcher_parser

# Scrapy settings for raspadorlegislativo project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'raspadorlegislativo'
LOG_LEVEL = config('LOG_LEVEL', default='DEBUG', cast=lambda l: getattr(logging, l))

SPIDER_MODULES = ['raspadorlegislativo.spiders']
NEWSPIDER_MODULE = 'raspadorlegislativo.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'raspadorlegislativo (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32
DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'  # disable dupefilter

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#     'raspadorlegislativo.middlewares.RaspadorlegislativoSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'raspadorlegislativo.middlewares.RaspadorlegislativoDownloaderMiddleware': 543,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'raspadorlegislativo.pipelines.RaspadorlegislativoPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = config('HTTPCACHE_ENABLED', default=False, cast=bool)
HTTPCACHE_EXPIRATION_SECS = 3 * 60 * 60  # 3 hours
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy_memcached_cache.MemcachedCacheStorage'
#MEMCACHED_LOCATION = config('MEMCACHED_LOCATION')

# Settings for Scrapy to filter and save bills
MATCHERS = config('KEYWORDS', default=None, cast=keyword_matcher_parser)
START_DATE = "2000-11-07"
FEED_FORMAT = 'csv'
FEED_URI = str(Path() / 'data' / '%(name)s-%(time)s.csv')

# Settings to communicate with Radar Legislativo API
RASPADOR_API_URL = config('RASPADOR_API_URL', default=None)
RASPADOR_API_TOKEN = config('RASPADOR_API_TOKEN', default=None)

#

# -*- coding: utf-8 -*-

# Scrapy settings for digikala project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'digikala'

SPIDER_MODULES = ['digikala.spiders']
NEWSPIDER_MODULE = 'digikala.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'digikala (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 1
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 15
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
#SPIDER_MIDDLEWARES = {
#    'digikala.middlewares.DigikalaSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'digikala.middlewares.DigikalaDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'digikala.pipelines.DigikalaPipeline': 300,
#}

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
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


INFO_CATEGORIES = [
"لوازم جانبی گوشی",
"گوشی موبایل",
"واقعیت مجازی",
"مچ‌بند و ساعت هوشمند",
"هدفون، هدست، هندزفری",
"اسپیکر بلوتوث و با سیم",
"اسکوتر برقی",
"هارد، فلش و SSD",
"دوربین",
"لوازم جانبی دوربین",
"دوربین‌های تحت شبکه",
"دوربین دو چشمی و شکاری",
"تلسکوپ",
"XBox, PS4 و بازی",
"لپ تاپ",
"لوازم جانبی لپتاپ",
"مودم و تجهیزات شبکه",
"کامپیوتر و تجهیزات جانبی",
"تبلت",
"کیف، کاور، لوازم جانبی تبلت",
"ماشین های اداری",
"کتابخوان فیدیبوک",
"کارت هدیه خرید از دیجی‌کالا",
"عطر، ادکلن، اسپری و ست",
"ست هدیه",
"خودروهای ایرانی و خارجی",
"لوازم جانبی خودرو",
"لوازم مصرفی خودرو",
"موتور سیکلت",
"کلاه و لوازم جانبی موتور",
"لوازم مصرفی و یدکی موتور",
"ابزار برقی",
"لوازم جانبی ابزار برقی",
"سیستم دزدگیر و درب بازکن",
"چندراهی برق و محافظ ولتاژ",
"کمپرسور و جک خودرو",
"ابزار غیر برقی",
"شیر و یراق آلات ساختمانی",
"ابزار و تجهیزات ایمنی کار",
"متر، تراز، اندازه‌گیری دقیق",
"نظم دهنده ابزار",
"گاوصندوق و قفل",
"ماشین های اداری",
"لوازم التحریر اداری",
"کیف و کوله اداری",
"میز، صندلی، دکوراسیون اداری",
"لوازم دستشویی و روشویی",
"مواد شوینده",
"کتاب و مجله",
"کتاب صوتی",
"لوازم التحریر",
"صنایع دستی",
]

IMAGE_CATEGORIES = [
"لوازم جانبی گوشی",
"گوشی موبایل",
"واقعیت مجازی",
"مچ‌بند و ساعت هوشمند",
"هدفون، هدست، هندزفری",
"اسپیکر بلوتوث و با سیم",
"اسکوتر برقی",
"هارد، فلش و SSD",
"دوربین",
"لوازم جانبی دوربین",
"دوربین‌های تحت شبکه",
"دوربین دو چشمی و شکاری",
"تلسکوپ",
"XBox, PS4 و بازی",
"لپ تاپ",
"لوازم جانبی لپتاپ",
"مودم و تجهیزات شبکه",
"کامپیوتر و تجهیزات جانبی",
"تبلت",
"کیف، کاور، لوازم جانبی تبلت",
"ماشین های اداری",
"کتابخوان فیدیبوک",
"کارت هدیه خرید از دیجی‌کالا",
"ست هدیه",
"خودروهای ایرانی و خارجی",
"لوازم جانبی خودرو",
"لوازم مصرفی خودرو",
"موتور سیکلت",
"کلاه و لوازم جانبی موتور",
"لوازم مصرفی و یدکی موتور",
"ابزار برقی",
"لوازم جانبی ابزار برقی",
"سیستم دزدگیر و درب بازکن",
"چندراهی برق و محافظ ولتاژ",
"کمپرسور و جک خودرو",
"ابزار غیر برقی",
"شیر و یراق آلات ساختمانی",
"ابزار و تجهیزات ایمنی کار",
"متر، تراز، اندازه‌گیری دقیق",
"نظم دهنده ابزار",
"گاوصندوق و قفل",
"ماشین های اداری",
"لوازم التحریر اداری",
"کیف و کوله اداری",
"میز، صندلی، دکوراسیون اداری",
"لوازم دستشویی و روشویی",
"مواد شوینده",
"کتاب و مجله",
"کتاب صوتی",
"لوازم التحریر",
"صنایع دستی",


]

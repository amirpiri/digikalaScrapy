import datetime
from http.cookies import SimpleCookie

import scrapy
import sys
from peewee import DoesNotExist, IntegrityError

from digikala.database.models import Product, Image


class ProductsSpider(scrapy.Spider):

    name = "products"
    searchUrl = "https://seller.digikala.com/ajax/product/new/search/"
    rawCookieStr = "Cookie:DK-Client1123=CUUU,d4537418-e4c9-4c2f-ae9e-169ac718be4c; __auc=bbac0a9f160414ed619f2e8e652; _ga=GA1.2.1154860754.1512924178; scarab.visitor=%22667CD184C6153217%22; scarab.profile=%22174307%7C1512924176%22; magspid.3a05=06e8a4cf-4f79-4cc5-84b1-bf69529d017a.1527444097.1.1527444099.1527444097.f4ff11dd-6dfa-4ffe-844c-478cee5352be; spid.3a05=1386a423-1167-4bda-9cd9-02b28920465c.1512924178.7.1529834392.1529762635.97304e9d-51ae-4023-869a-af7f1e254268; _conv_r=s:seller.digikala.com*m:referral*t:*c:; PHPSESSID=7hmfapgdsn6c5i8tt8h27ojj68; _gid=GA1.2.331719713.1542116407; non-original-warning-3days=1; scarab.mayAdd=%5B%7B%22i%22%3A%22130186%22%7D%2C%7B%22i%22%3A%22130448%22%7D%2C%7B%22i%22%3A%22451705%22%7D%5D; _conv_v=vi:1512924188976-0.5316556157306724*sc:11*cs:1542117318*fs:1512924189*pv:75*exp:{100013987.{v.100080463-g.{}}-100014167.{v.100080874-g.{}}-100017068.{v.1000164963-g.{}}-100017755.{v.1000166746-g.{}}-100018019.{v.1000167539-g.{}}-100018056.{v.1000167615-g.{}}-100018307.{v.1000168382-g.{}}-100018405.{v.1000168602-g.{}}-100018410.{v.1000168615-g.{}}-100018476.{v.1000168768-g.{}}-100018677.{v.1000169221-g.{}}-100019156.{v.1000170392-g.{}}-100019159.{v.1000170399-g.{}}-100019163.{v.1000170406-g.{}}-100019362.{v.1000170915-g.{}}-100019549.{v.1000171323-g.{}}-100019684.{v.1000171638-g.{}}-100019731.{v.1000171738-g.{}}-100019940.{v.1000172190-g.{}}}*ps:1541842289; _gat_UA-89671194-1=1"
    def getCookie(self):
        cookie = SimpleCookie()
        cookie.load(self.rawCookieStr)
        cookies = {}
        for key, morsel in cookie.items():
            cookies[key] = morsel.value
        return cookies

    def build_product_search_request(self, page):
        return scrapy.FormRequest(url=self.searchUrl,
                           method="POST",
                           formdata={
                                'items': '20',
                                'page': str(page),
                                'search[category_id]': '',
                                'search[keyword]': '',
                                'sortColumn': '',
                                'sortOrder': 'asc'
                           },
                           cookies=self.getCookie(),
                           headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
                           callback=self.parse_search_list)

    def start_requests(self):
        print("python info: ")
        print(sys.version_info)
        yield self.build_product_search_request(15)

    def parse_search_list(self, response):

        allProductsCount = response.css('.uk-table-all-result-count::text').extract_first()
        print("all products count: {}".format(allProductsCount))

        products = response.css('tr.product-table-row')
        print("products in this page: {}".format(len(products)) )

        for product in products:
            colDivs = product.css('.row div')

            title = colDivs[1].css('span.fa-title::text').extract_first()
            url = colDivs[1].css('span.category a::attr(href)').extract_first()
            imageUrl = colDivs[0].css('span img::attr(src)').extract_first().split('?')[0]
            price = colDivs[2].css('span.description span::attr(data-debug)').extract_first()
            brand = colDivs[1].css('span.category::text').extract_first()

            product_save = Product(url=url, title=title, price=price, state=1, category=brand)
            image_save = Image(product=product_save, url=imageUrl)
            try:
                product_save.save()
                image_save.save()
            except IntegrityError:
                pass

        nextPage = response.css('a.pagination-button--next::attr(data-page)').extract_first()
        print('Next page: {}'.format(nextPage))

        if nextPage is not None:
            yield self.build_product_search_request(nextPage)


    def parse_car(self, response):
        pass
        # car = Car.get(url=response.url)
        # title_info =response.css('h1.addetail-title')
        # title = title_info.css('span[itemprop=releaseDate]::text').extract_first() + ' - ' + \
        #         title_info.css('span[itemprop=brand]::text').extract_first() + ' - ' + \
        #         title_info.css('span[itemprop=model]::text').extract_first() + ' - '
        # car.title = title
        #
        # info = response.css('div.prdinfo')
        # pish_shomare = info.css('#phone-area-code::text').extract_first()
        # if pish_shomare is None:
        #     pish_shomare = ''
        # scripts = response.css('script[type="text/javascript"]::text').extract()
        # scripts = ' '.join(scripts)
        # key = u'$("#phone-field").text('
        # index = scripts.find(key)
        #
        # telephone = ''
        # if index != -1:
        #     index = index + len(key)
        #     while not scripts[index].isdigit():
        #         index += 1
        #     while len(telephone) < 30 and (scripts[index].isdigit() or scripts[index] in ', '):
        #         telephone += scripts[index]
        #         index += 1
        # car.telephone = pish_shomare + '' + telephone;
        # car.state = 2
        # car.save()





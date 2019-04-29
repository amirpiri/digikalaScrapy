import datetime
from http.cookies import SimpleCookie

import scrapy
import sys
from peewee import DoesNotExist, IntegrityError, fn

from digikala.database.models import Product, Image, RatingFeature, RatingFeatureValue, Feature, FeatureValue


class ProductsSpider(scrapy.Spider):
    name = "product_pages"
    handle_httpstatus_list = [404]

    urlTemplage = "https://www.digikala.com/product/dkp-{}"
    productIdStartFrom = 936800
    rawCookieStr = "Cookie:DK-Client1123=CUUU,d4537418-e4c9-4c2f-ae9e-169ac718be4c; __auc=bbac0a9f160414ed619f2e8e652; _ga=GA1.2.1154860754.1512924178; scarab.visitor=%22667CD184C6153217%22; scarab.profile=%22174307%7C1512924176%22; magspid.3a05=06e8a4cf-4f79-4cc5-84b1-bf69529d017a.1527444097.1.1527444099.1527444097.f4ff11dd-6dfa-4ffe-844c-478cee5352be; spid.3a05=1386a423-1167-4bda-9cd9-02b28920465c.1512924178.7.1529834392.1529762635.97304e9d-51ae-4023-869a-af7f1e254268; _conv_r=s:seller.digikala.com*m:referral*t:*c:; PHPSESSID=7hmfapgdsn6c5i8tt8h27ojj68; _gid=GA1.2.331719713.1542116407; non-original-warning-3days=1; scarab.mayAdd=%5B%7B%22i%22%3A%22130186%22%7D%2C%7B%22i%22%3A%22130448%22%7D%2C%7B%22i%22%3A%22451705%22%7D%5D; _conv_v=vi:1512924188976-0.5316556157306724*sc:11*cs:1542117318*fs:1512924189*pv:75*exp:{100013987.{v.100080463-g.{}}-100014167.{v.100080874-g.{}}-100017068.{v.1000164963-g.{}}-100017755.{v.1000166746-g.{}}-100018019.{v.1000167539-g.{}}-100018056.{v.1000167615-g.{}}-100018307.{v.1000168382-g.{}}-100018405.{v.1000168602-g.{}}-100018410.{v.1000168615-g.{}}-100018476.{v.1000168768-g.{}}-100018677.{v.1000169221-g.{}}-100019156.{v.1000170392-g.{}}-100019159.{v.1000170399-g.{}}-100019163.{v.1000170406-g.{}}-100019362.{v.1000170915-g.{}}-100019549.{v.1000171323-g.{}}-100019684.{v.1000171638-g.{}}-100019731.{v.1000171738-g.{}}-100019940.{v.1000172190-g.{}}}*ps:1541842289; _gat_UA-89671194-1=1"
    def getCookie(self):
        cookie = SimpleCookie()
        cookie.load(self.rawCookieStr)
        cookies = {}
        for key, morsel in cookie.items():
            cookies[key] = morsel.value
        return cookies

    def start_requests(self):
        print("python info: ")
        print(sys.version_info)
        min_dk_pid = self.getLastProductId()
        print(min_dk_pid)
        yield self.build_product_page_request(min_dk_pid)

    def parse_product(self, response):
        product_id = response.meta['product_id']
        print('Load product: {} status: '.format(product_id, response.status))
        if response.status == 200:
            print('SAVING PRODUCT')
            product_info = response.css('article.c-product')

            title = product_info.css('h1.c-product__title::text').extract_first().strip()
            subtitle = product_info.css('h1.c-product__title span::text').extract_first()
            url = response.url
            price = response.css('meta[property="product:price:amount"]::attr(content)').extract_first()
            pr_directory = product_info.css('div.c-product__directory li')
            try:
                brand = pr_directory[0].css('span::text').extract()[1]
            except Exception:
                brand = pr_directory[0].css('a::text').extract_first()

            category = pr_directory[1].css('a::text').extract_first()
            status = product_info.css('div.c-product__status-bar::text').extract_first()
            productFeatures_lis =  response.css('div.c-product__params > ul li')
            productFeatures = ''
            for fli in productFeatures_lis:
                spans = fli.css('span')
                print(spans.extract())
                if len(spans) >= 2 :
                    feature = spans[0].css('::text').extract_first()
                    value = spans[1].css('::text').extract_first()
                    if feature is not None and value is not None:
                        productFeatures += feature.strip() + '' + value.strip() + ';'

            summary = response.css('div.c-mask__text--product-summary::text').extract_first()
            evalPositive = response.css('div.c-content-expert__evaluation-positive ul > li::text').extract()
            evalNegative = response.css('div.c-content-expert__evaluation-negative ul > li::text').extract()
            if evalPositive is None:
                evalPositive = []
            if evalNegative is None:
                evalNegative = []

            images = product_info.css('ul.c-gallery__items img::attr(data-src)').extract()
            images = list(map(lambda x: x.split('?')[0], images))
            print(title)
            print(subtitle)
            print(url)
            print(price)
            print(brand)
            print(category)
            print(status)
            print(images)
            print(evalPositive)
            print(evalNegative)

            product_save = Product(url=url, title=title, subtitle=subtitle, price=price, category=category, brand=brand, dk_product_id= product_id,
                                   summary=summary, evaluationPositive=';'.join(evalPositive), evaluationNegative=';'.join(evalNegative), productFeatures=productFeatures,
                                   status=status, state=1)
            try:
                product_save.save()
            except IntegrityError:
                product_save = Product.select().where(Product.url == url).get()
            print(product_save.url)

            for image_url in images:
                image_save = Image(product=product_save, url=image_url)
                try:
                    image_save.save()
                except IntegrityError:
                    pass

            rating_lis = response.css('ul.c-content-expert__rating> li')
            for rli in rating_lis:
                print(rli)
                divs = rli.css('div')
                rFeatureTitle = divs[0].css('::text').extract_first()
                rFeatureValue = divs[1].css('::attr(data-rate-digit)').extract_first()
                try:
                    rFeature_model = RatingFeature(title=rFeatureTitle)
                    rFeature_model.save()
                except IntegrityError:
                    rFeature_model = RatingFeature.select().where(RatingFeature.title == rFeatureTitle).get()
                rFeatureValue_model = RatingFeatureValue(ratingFeature=rFeature_model, product=product_save, value=rFeatureValue)
                rFeatureValue_model.save()

            paramsSections = response.css('div.c-params section')
            for section in paramsSections:
                sectionName = section.css('h3.c-params__title a::text').extract_first()
                if sectionName is None:
                    sectionName = section.css('h3.c-params__title::text').extract_first()
                sectionName = sectionName.strip()
                featureNameGhabli = ''
                params_lis = section.css('ul.c-params__list li')
                for pli in params_lis:
                    featureName = pli.css('div.c-params__list-key a::text').extract_first()
                    if featureName is None:
                        featureName = pli.css('div.c-params__list-key span::text').extract_first()
                    if featureName is not None:
                        featureName = featureName.strip()
                    else:
                        featureName = featureNameGhabli
                    featureNameGhabli = featureName

                    featureValue = pli.css('div.c-params__list-value a::text').extract_first()
                    if featureValue is None:
                        featureValue = pli.css('div.c-params__list-value span::text').extract_first()
                    if featureValue is None:
                        featureValue = '-'
                    featureValue = featureValue.strip()
                    try:
                        feature_model = Feature(title=featureName)
                        feature_model.save()
                    except IntegrityError:
                        feature_model = Feature.select().where(Feature.title == featureName).get()

                    featureValue_model = FeatureValue(feature=feature_model, product=product_save, value=featureValue, section=sectionName)
                    featureValue_model.save()
            product_save.state = 2
            product_save.save()

        yield self.build_product_page_request(product_id - 1)


    def getProductUrl(self, dk_pid):
        return self.urlTemplage.format(dk_pid)

    def getLastProductId(self):
        min_dk_pid = Product.select(fn.MIN(Product.dk_product_id)).where(Product.state == 2).scalar()
        if min_dk_pid is None:
            min_dk_pid = self.productIdStartFrom
        else:
            min_dk_pid -= 1
        return min_dk_pid

    def build_product_page_request(self, pid):
        request = scrapy.Request(url=self.getProductUrl(pid),
                       callback=self.parse_product,
                       cookies=self.getCookie(),
                       headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
                                }
                       )
        request.meta['product_id'] = pid
        return request

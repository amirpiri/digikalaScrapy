import datetime
from http.cookies import SimpleCookie

import scrapy
import sys
from scrapy.utils.project import get_project_settings
from peewee import DoesNotExist, IntegrityError, fn

from digikala.database.models_shop import Product
import digikala.database.models_shop as models


class ProductsSpider(scrapy.Spider):
    name = "product_pages_shop"
    handle_httpstatus_list = [404]

    def start_requests(self):
        print("python info: ")
        print(sys.version_info)
        start_digikala_id = models.get_min_digikala_id()
        print(start_digikala_id)
        yield self.build_product_page_request(start_digikala_id)

    def parse_product(self, response):
        product_id = response.meta['product_id']
        print('Load product: {} status: '.format(product_id, response.status))
        if response.status == 200 and self.check_product_info(response):
            url = self.get_product_url(response)
            existing_product = models.find_product_by_digikala_url(url)

            if existing_product == None:
                print('SAVING PRODUCT')
                self.save_product_info(response)
            else :
                print('UPDATING PRODUCT')
                product = models.find_product_by_digikala_url(url)
                if product is not None:
                    self.update_product_info(product, response)

            new_product_id = models.get_min_digikala_id()
        else:
            new_product_id = product_id - 1

        yield self.build_product_page_request(new_product_id)

    def generate_product_url(self, dk_pid):
        return "https://www.digikala.com/product/dkp-{}".format(dk_pid)

    def build_product_page_request(self, pid):
        request = scrapy.Request(url=self.generate_product_url(pid),
                       callback=self.parse_product,
                       cookies=self.getCookie(),
                       headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
                                }
                       )
        request.meta['product_id'] = pid
        return request

    def get_digikala_product_id(self, response):
        product_id = response.meta['product_id']
        return product_id

    def get_product_title(self, response):
        product_info = response.css('article.c-product')
        title = product_info.css('h1.c-product__title::text').extract_first().strip()
        return title

    def get_product_url(self, response):
        url = response.url
        return url

    def get_product_subtitle(self, response):
        product_info = response.css('article.c-product')
        subtitle = product_info.css('h1.c-product__title span::text').extract_first()
        return subtitle

    def get_product_price(self, response):
        price = response.css('meta[property="product:price:amount"]::attr(content)').extract_first()
        return price

    def get_product_brand(self, response):
        product_info = response.css('article.c-product')
        pr_directory = product_info.css('div.c-product__directory li')
        if len(pr_directory.extract()) < 2:
            return "NotSpecified"
        try:
            brand = pr_directory[0].css('span::text').extract()[1]
        except Exception:
            brand = pr_directory[0].css('a::text').extract_first()
        return brand

    def get_product_category(self, response):
        product_info = response.css('article.c-product')
        pr_directory = product_info.css('div.c-product__directory li')
        if len(pr_directory.extract()) < 2:
            return "NotSpecified"
        try:
            category = pr_directory[1].css('span::text').extract()[1]
        except Exception:
            category = pr_directory[1].css('a::text').extract_first()
        return category

    def get_product_status(self, response):
        product_info = response.css('article.c-product')
        status = product_info.css('div.c-product__status-bar::text').extract_first()
        return status

    def get_product_summary_features(self, response):
        lis = response.css('div.c-product__params > ul li')
        features_dict = {}
        for fli in lis:
            spans = fli.css('span')
            # print(spans.extract())
            if len(spans) >= 2:
                feature = spans[0].css('::text').extract_first()
                value = spans[1].css('::text').extract_first()
                if feature is not None and value is not None:
                    features_dict[feature.strip()] = value.strip()
        return features_dict

    def get_product_summary(self, response):
        summary = response.css('div.c-mask__text--product-summary::text').extract_first()
        if summary is None:
            return ''
        return summary

    def get_product_positive_evaluations(self, response):
        evalPositive = response.css('div.c-content-expert__evaluation-positive ul > li::text').extract()
        if evalPositive is None:
            evalPositive = []
        return evalPositive

    def get_product_negative_evaluations(self, response):
        evalNegative = response.css('div.c-content-expert__evaluation-negative ul > li::text').extract()
        if evalNegative is None:
            evalNegative = []
        return evalNegative

    def get_product_image_list(self, response):
        product_info = response.css('article.c-product')
        images = product_info.css('ul.c-gallery__items img::attr(data-src)').extract()

        image_list = []
        for image in images:
            image_list.append(image.split('?')[0])

        main_image = product_info.css('div.c-gallery__img img::attr(data-src)').extract_first()
        if main_image is not None:
            main_image = main_image.split('?')[0]
        print("Main image: {}".format(main_image))
        print(image_list)
        return image_list, main_image


    def get_product_rating_dict(self, response):
        rating = {}
        rating_lis = response.css('ul.c-content-expert__rating> li')
        for rli in rating_lis:
            # print(rli)
            divs = rli.css('div')
            rFeatureTitle = divs[0].css('::text').extract_first()
            rFeatureValue = divs[1].css('::attr(data-rate-digit)').extract_first()
            rating[rFeatureTitle] = rFeatureValue
        return rating

    def get_product_main_features_list(self, response):
        features = []
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
                features.append((sectionName, featureName, featureValue))
        return features


    def get_colors_list(self, response):
        product_info = response.css('article.c-product')
        color_labels = product_info.css('ul.js-product-variants li.js-c-ui-variant label')
        colors_list = []
        for label in color_labels:
            color_code = label.css('::attr(data-code)').extract_first()
            color_name = label.css('span.c-ui-variant__check::text').extract_first()
            if color_code is not None:
                colors_list.append((color_name, color_code))
        return colors_list


    def get_category_list_in_breadcrumb(self, response):
        lis = response.css('ul.c-breadcrumb li')
        category_list = []
        for li in lis:
            category = li.css('span[property="name"]::text').extract_first()
            if category is None:
                continue
            category_list.append(category.strip())
        return category_list[:-1]


    def get_product_info_dict(self, response):
        digikala_product_id = self.get_digikala_product_id(response)
        title = self.get_product_title(response)
        subtitle = self.get_product_subtitle(response)
        url = self.get_product_url(response)
        price = self.get_product_price(response)

        brand = self.get_product_brand(response)
        category = self.get_product_category(response)
        status = self.get_product_status(response)
        summary_features_dict = self.get_product_summary_features(response)

        summary = self.get_product_summary(response)
        eval_positive = self.get_product_positive_evaluations(response)
        eval_negative = self.get_product_negative_evaluations(response)
        images_list, main_image = self.get_product_image_list(response)
        rating_dict = self.get_product_rating_dict(response)
        main_features_list = self.get_product_main_features_list(response)
        colors_list = self.get_colors_list(response)
        category_hierarchy = self.get_category_list_in_breadcrumb(response)

        return {
            'digikala_product_id': digikala_product_id,
            'title': title,
            'subtitle': subtitle,
            'url': url,
            'price': price,
            'brand': brand,
            'category': category,
            'status': status,
            'summary_features_dict': summary_features_dict,
            'summary': summary,
            'eval_negative': eval_negative,
            'eval_positive': eval_positive,
            'images_list': images_list,
            'main_image': main_image,
            'rating_dict': rating_dict,
            'main_features_list': main_features_list,
            'colors_list': colors_list,
            'category_hierarchy': category_hierarchy
        }

    def save_product_info(self, response):
        product_info = self.get_product_info_dict(response)
        product = Product()
        models.save_product(product, product_info)


    def update_product_info(self, product, response):
        product_info = self.get_product_info_dict(response)
        models.save_product(product, product_info)


    rawCookieStr = "Cookie:DK-Client1123=CUUU,d4537418-e4c9-4c2f-ae9e-169ac718be4c; __auc=bbac0a9f160414ed619f2e8e652; _ga=GA1.2.1154860754.1512924178; scarab.visitor=%22667CD184C6153217%22; scarab.profile=%22174307%7C1512924176%22; magspid.3a05=06e8a4cf-4f79-4cc5-84b1-bf69529d017a.1527444097.1.1527444099.1527444097.f4ff11dd-6dfa-4ffe-844c-478cee5352be; spid.3a05=1386a423-1167-4bda-9cd9-02b28920465c.1512924178.7.1529834392.1529762635.97304e9d-51ae-4023-869a-af7f1e254268; _conv_r=s:seller.digikala.com*m:referral*t:*c:; PHPSESSID=7hmfapgdsn6c5i8tt8h27ojj68; _gid=GA1.2.331719713.1542116407; non-original-warning-3days=1; scarab.mayAdd=%5B%7B%22i%22%3A%22130186%22%7D%2C%7B%22i%22%3A%22130448%22%7D%2C%7B%22i%22%3A%22451705%22%7D%5D; _conv_v=vi:1512924188976-0.5316556157306724*sc:11*cs:1542117318*fs:1512924189*pv:75*exp:{100013987.{v.100080463-g.{}}-100014167.{v.100080874-g.{}}-100017068.{v.1000164963-g.{}}-100017755.{v.1000166746-g.{}}-100018019.{v.1000167539-g.{}}-100018056.{v.1000167615-g.{}}-100018307.{v.1000168382-g.{}}-100018405.{v.1000168602-g.{}}-100018410.{v.1000168615-g.{}}-100018476.{v.1000168768-g.{}}-100018677.{v.1000169221-g.{}}-100019156.{v.1000170392-g.{}}-100019159.{v.1000170399-g.{}}-100019163.{v.1000170406-g.{}}-100019362.{v.1000170915-g.{}}-100019549.{v.1000171323-g.{}}-100019684.{v.1000171638-g.{}}-100019731.{v.1000171738-g.{}}-100019940.{v.1000172190-g.{}}}*ps:1541842289; _gat_UA-89671194-1=1"
    def getCookie(self):
        cookie = SimpleCookie()
        cookie.load(self.rawCookieStr)
        cookies = {}
        for key, morsel in cookie.items():
            cookies[key] = morsel.value
        return cookies

    def wanted_info_category(self, product_info, response):
        item_categories = self.get_category_list_in_breadcrumb(response)
        settings = get_project_settings()
        wanted_info_categories = settings.get('INFO_CATEGORIES')
        for c in item_categories:
            if c in wanted_info_categories:
                return True
        return False

    def check_product_info(self, response):
        product_info = response.css('article.c-product')
        title = product_info.css('h1.c-product__title::text').extract_first()
        return (title != None)




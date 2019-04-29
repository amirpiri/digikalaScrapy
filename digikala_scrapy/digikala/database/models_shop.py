#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import json

from peewee import *
from playhouse.db_url import connect
from playhouse.reflection import Introspector

db = connect('mysql://root:secret@10.5.0.7:3306/shop?charset=utf8mb4')
# db = connect('mysql://root:123456@localhost:3306/shop')
introspector = Introspector.from_database(db)
models = introspector.generate_models()

# peewee Model classes generated from the database schema.
Product = models['products']
Category = models['categories']
Brand = models['brands']
CategoryBrand = models['brand_category']
ProductImage = models['product_images']
Features = models['features']
ProductAttribute = models['product_attributes']
AttributeValue = models['attribute_values']
Color = models['colors']
ProductColor = models['color_product']


def get_min_digikala_id(default=1093700):
    min_dk_pid = Product\
        .select(fn.MIN(Product.digikala_product_id))\
        .where((Product.crawl_state == 0))\
        .scalar()

    if min_dk_pid is not None:
        return int(min_dk_pid)

    min_dk_pid = Product \
        .select(fn.MIN(Product.digikala_product_id)) \
        .scalar()

    if min_dk_pid is not None:
        return int(min_dk_pid) - 1

    return default

def last_product_with_crawl_state(state):
    product = Product.select().where(Product.crawl_state == state).order_by(Product.id.desc()).first()
    return product
def first_product_with_crawl_state(state):
    product = Product.select().where(Product.crawl_state == state).order_by(Product.id.asc()).first()
    return product


def find_product_by_digikala_url(dk_url):
    try:
        existing_product = Product.select().where(Product.digikala_url == dk_url).get()
        return existing_product
    except DoesNotExist:
        return None


def find_or_create_category(info):
    category_name = info['category']
    try:
        existing_category = Category.select().where(Category.name == category_name).get()
        return existing_category
    except:
        category = Category()
        category.name = category_name
        category.save()
        return category


def find_or_create_brand(info):
    brand_name = info['brand']
    try:
        existing_brand = Brand.select().where(Brand.name == brand_name).get()
        return existing_brand
    except:
        brand = Brand()
        brand.name = brand_name
        brand.save()
        return brand


def find_or_create_category_brand(category, brand):
    try:
        existing_record = CategoryBrand.select().where(CategoryBrand.category_id == category.id, CategoryBrand.brand_id == brand.id).get()
        return existing_record
    except:
        category_brand = CategoryBrand()
        category_brand.brand_id = brand.id
        category_brand.category_id = category.id
        category_brand.save()
        return category_brand


def find_or_create_feature(feature_name, category, order=0):
    try:
        existing_record = Features.select().where(Features.name == feature_name, Features.category_id == category.id).get()
        return existing_record
    except:
        feature = Features()
        feature.name = feature_name
        feature.category_id = category.id
        feature.order = order
        feature.save()
        return feature

def fill_product_info(p, category, info):
    # category = find_or_create_category(info)
    brand = find_or_create_brand(info)
    category_brand = find_or_create_category_brand(category, brand)

    p.name = info['title']
    p.name_en = info['subtitle']
    p.desc = info['summary']
    p.category_id = category.id
    p.brand_id = brand.id
    p.summary_data = json.dumps(info['summary_features_dict'])
    p.bazaar_price = info['price']

    p.digikala_url = info['url']
    p.digikala_product_id = info['digikala_product_id']
    return p, brand


def save_product_images(p, info):
    image_list = info['images_list']
    for i in range(len(image_list)):
        product_image = ProductImage()
        product_image.product_id = p.id
        product_image.path = image_list[i]
        product_image.is_main = 0
        product_image.save()

    product_image = ProductImage()
    product_image.product_id = p.id
    product_image.path = info['main_image']
    product_image.is_main = 1
    product_image.save()


def find_or_create_product_attribute(attribute_name, feature, order, attribute_type='select'):
    try:
        existing_record = ProductAttribute.select().where(ProductAttribute.name == attribute_name,
                                                          ProductAttribute.feature_id == feature.id,
                                                          ProductAttribute.type == attribute_type).get()
        return existing_record, False
    except Exception as e:
        product_attr = ProductAttribute()
        product_attr.name = attribute_name
        product_attr.feature_id = feature.id
        product_attr.order = order
        product_attr.type = attribute_type
        product_attr.save()
        return product_attr, True


def find_or_create_attribute_value(product_attribute, attribute_value_text):
    max_size = 1500
    if len(attribute_value_text) > max_size:
        attribute_value_text = (attribute_value_text[:max_size] + '...')
        print('Truncating value text with lenght {}'.format(len(attribute_value_text)))

    try:
        existing_record = AttributeValue.select().where(AttributeValue.text == attribute_value_text,
                                                        AttributeValue.product_attribute_id == product_attribute.id).get()
        return existing_record
    except:
        attribute_value = AttributeValue()
        attribute_value.product_attribute_id = product_attribute.id
        attribute_value.text = attribute_value_text
        attribute_value.save()
        if product_attribute.type == 'boolean' and attribute_value_text in ['0', '1']:
            other_value = str(1 - int(attribute_value_text))
            find_or_create_attribute_value(product_attribute, other_value)
        return attribute_value


def save_product_features(p, category, info):
    main_features_list = info['main_features_list']
    result_product_data = {}
    order = 1
    for sn, fn, fv in main_features_list:
        # (section_name. feature_name, feature_value)
        # in shop database scheme
        feature_name = sn
        attribute_name = fn
        attribute_value_text = fv
        feature = find_or_create_feature(feature_name, category, order)
        attribute_type = "select"
        count = 0
        for _, attribute_name_temp, __ in main_features_list:
            if attribute_name == attribute_name_temp:
                count += 1
        if count > 1:
            attribute_type = 'multi_select'

        if len(attribute_value_text) > 200:
            attribute_type = 'text'
        if u'سایر' in attribute_name or u'دیگر' in attribute_name or u'توضیحات' in attribute_name:
            attribute_type = 'text'

        if attribute_value_text == u'دارد':
            attribute_value_text = '1'
            attribute_type = 'boolean'
        if attribute_value_text == u'ندارد':
            attribute_value_text = '0'
            attribute_type = 'boolean'

        product_attribute, is_new_attr = find_or_create_product_attribute(attribute_name, feature, order, attribute_type)
        attribute_value = find_or_create_attribute_value(product_attribute, attribute_value_text)

        new_value = '{}'.format(attribute_value.id)
        feat_key = 'F{}'.format(feature.id)
        attr_key = 'A{}'.format(product_attribute.id)
        try:
            features_data = result_product_data[feat_key]
            try:
                value = features_data[attr_key]
                if isinstance(value, list):
                    value.append(new_value)
                else:
                    if product_attribute.type == 'text':
                        features_data[attr_key] = '\n'.join([value, new_value])
                    else:
                        features_data[attr_key] = [value, new_value]
            except KeyError:
                features_data[attr_key] = new_value
        except KeyError:
            result_product_data[feat_key] = {attr_key: new_value}
        order += 1
    return result_product_data

def find_or_create_color(name, code):
    try:
        existing_record = Color.select().where(Color.name == name, Color.hex_color_code == code).get()
        return existing_record
    except:
        color = Color()
        color.name = name
        color.hex_color_code = code
        color.save()
        return color


def save_product_colors(p, info):
    colors_list = info['colors_list']
    for color_name, color_code in colors_list:
        color = find_or_create_color(color_name, color_code)
        product_color = ProductColor()
        product_color.product_id = p.id
        product_color.color_id = color.id
        product_color.save()


def fill_category_hierarchy(info):
    category_hierarchy = info['category_hierarchy']
    print("Category hierarchy length: {}".format(len(category_hierarchy)))
    parent = None
    category = None
    for category_name in category_hierarchy:
        try:
            category = Category.select().where(Category.name == category_name, Category.parent == parent).get()
        except:
            category = Category()
            category.name = category_name
            category.parent = parent
            category.save()
        parent = category.id
    return category


def save_product(product, product_info_dict):
    category = fill_category_hierarchy(product_info_dict)
    product, brand = fill_product_info(product, category, product_info_dict)
    product.save()

    save_product_images(product, product_info_dict)
    product_data = save_product_features(product, category, product_info_dict)
    save_product_colors(product, product_info_dict)

    product.product_data = json.dumps(product_data)
    product.crawl_state = 1
    product.save()


def get_product_images(product):
    return ProductImage.select().where(ProductImage.product_id == product.id)
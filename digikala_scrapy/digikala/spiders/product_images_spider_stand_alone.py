import urllib

import os
import sys
sys.path.append('database/')
print(sys.path)
import models_shop as models

import logging
logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

storage_dir = '/usr/local/sbin/scraper/images'

def extract_name(url):
    filename = url[url.rfind("/") + 1:]
    return filename


def download_image(url, local_name=None):
    if local_name is None:
        local_name = extract_name(url)
    local_path = os.path.join(storage_dir, local_name)
    urllib.urlretrieve(url, local_path)

    return local_path

def main():
    while True:
        product = models.first_product_with_crawl_state(state=1)
        print(product.id)
        if product is None:
            break
        product_images = models.get_product_images(product)
        try:
            for image in product_images:
                local_path = download_image(image.path)
                image.local_path = local_path
                image.save()
                print('image {} downloaded to {}'.format(image.id, local_path))
            product.crawl_state = 2
            product.save()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()

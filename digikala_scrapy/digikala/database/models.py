import datetime
from peewee import *
from playhouse.db_url import connect

db = connect('mysql://root:123456@localhost:3306/digikala_crawl_pages')



class BaseModel(Model):
    class Meta:
        database = db

class Product(BaseModel):
    dk_product_id = IntegerField()
    url = CharField(max_length=1024, unique=True)
    title = CharField(max_length=1024,null=True)
    subtitle = CharField(max_length=1024,null=True)
    category = CharField(null=True)
    brand = CharField(null=True)
    price = CharField(null=True)
    status = CharField(null=True)
    summary = TextField(null=True)
    productFeatures = TextField(null=True)
    evaluationPositive = TextField(null=True)
    evaluationNegative = TextField(null=True)
    state = IntegerField(default=0)
    time_retrieve = DateTimeField(default=datetime.datetime.now)

    def toMessage(self):
        return self.title + '\n' + self.category + '\n' + self.url

class Image(BaseModel):
    url = CharField(max_length=1024, unique=True)
    product = ForeignKeyField(Product)

class Feature(BaseModel):
    title = CharField(max_length=1024, unique=True)

class FeatureValue(BaseModel):
    feature = ForeignKeyField(Feature)
    product = ForeignKeyField(Product)
    value = TextField(null=True)
    section = CharField(max_length=1024, null=True)

class RatingFeature(BaseModel):
    title = CharField(max_length=1024, unique=True)

class RatingFeatureValue(BaseModel):
    ratingFeature = ForeignKeyField(RatingFeature)
    product = ForeignKeyField(Product)
    value = CharField(max_length=512)

class Category(BaseModel):
    title = CharField(max_length=1024)
    parentCategory = CharField(max_length=1024)
    active = IntegerField(default=0)

def create_tables():
    db.connect()
    db.create_tables([Product, Image, Category, Feature, FeatureValue, RatingFeature, RatingFeatureValue])


if __name__ == '__main__':
    create_tables()
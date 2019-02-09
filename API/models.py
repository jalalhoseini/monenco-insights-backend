from django.db.models import (Model, OneToOneField, ManyToManyField, CASCADE, SET_NULL, CharField, ImageField,
                              IntegerField, ForeignKey, DateTimeField, BooleanField, TextField)
from django.contrib.auth.models import User
from django.utils import timezone
from ckeditor.fields import RichTextField

NAME_MAX_LENGTH = 200
TITLE_MAX_LENGTH = 250
PASSWORD_MAX_LENGTH = 200
PASSWORD_MIN_LENGTH = 6
IMAGE_PART = 2
TEXT_PART = 1
PART_TYPE_CHOICES = (
    (IMAGE_PART, 'Image Part'),
    (TEXT_PART, 'Text Part'),
)


class Client(Model):
    user = OneToOneField(to=User, on_delete=CASCADE, null=False, db_index=True)
    author = OneToOneField(to="Author", on_delete=SET_NULL, null=True, default=None, db_index=True)
    bookmarkedArticles = ManyToManyField(to="Article", db_index=True)
    favoriteCategories = ManyToManyField(to="Category", db_index=True)

    def __str__(self):
        return self.user.username


class Author(Model):
    publicPersianName = CharField(max_length=NAME_MAX_LENGTH)
    publicName = CharField(max_length=NAME_MAX_LENGTH)

    def __str__(self):
        return self.publicName


class Category(Model):
    def uploadLocation(self, filename):
        filename = self.name + "_" + filename
        return "CategoryIcons/%s" % filename

    name = CharField(max_length=NAME_MAX_LENGTH)
    persianName = CharField(max_length=NAME_MAX_LENGTH)
    icon = ImageField(upload_to=uploadLocation)

    def __str__(self):
        return self.name


class Tag(Model):
    name = CharField(max_length=NAME_MAX_LENGTH)
    persianName = CharField(max_length=NAME_MAX_LENGTH)
    relatedTags = ManyToManyField(to="Tag", db_index=True)

    def __str__(self):
        return self.name


class Article(Model):
    def uploadLocation(self, filename):
        filename = str(self.id) + "_" + filename
        return "ArticleImages/%s" % filename

    creationDate = DateTimeField(default=timezone.now)
    leadText = TextField()
    title = CharField(max_length=TITLE_MAX_LENGTH)
    image = ImageField(upload_to=uploadLocation)
    isPersian = BooleanField()
    author = ForeignKey(to="Author", null=False, blank=False, on_delete=CASCADE, db_index=True)
    category = ForeignKey(to="Category", null=False, blank=False, on_delete=CASCADE, db_index=True)
    tags = ManyToManyField(to="Tag", related_name="articles", related_query_name="article", null=True, blank=True,
                           db_index=True)


class ArticlePart(Model):
    def uploadLocation(self, filename):
        filename = str(self.id) + "_" + filename
        return "ArticlePartImage/%s" % filename

    type = IntegerField(choices=PART_TYPE_CHOICES)
    order = IntegerField()
    title = CharField(max_length=TITLE_MAX_LENGTH)
    image = ImageField(upload_to=uploadLocation, null=True, blank=True, default=None)
    content = RichTextField(null=True, blank=True, default=None)
    article = ForeignKey(to="Article", on_delete=CASCADE, db_index=True)

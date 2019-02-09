from rest_framework.serializers import (
    Serializer,
    EmailField,
    CharField,
    IntegerField,
    SerializerMethodField,
    ModelSerializer,

)

from API.validators import *
from API.models import (Category, Article, ArticlePart, Author, Tag)


class AuthenticationSerializer(Serializer):
    client_id = CharField(validators=[clientIDValidator])
    client_secret = CharField(validators=[clientSecretValidator])


class UserRegisterSerializer(AuthenticationSerializer):
    email = EmailField()
    password = CharField(validators=[passwordValidator])
    username = CharField(validators=[usernameValidator])


class LoginSerializer(AuthenticationSerializer):
    username = CharField(validators=[usernameValidator])
    password = CharField(validators=[passwordValidator])
    grant_type = CharField(max_length=20)


class LogoutSerializer(AuthenticationSerializer):
    token = CharField(max_length=200)


class RefreshTokenSerializer(AuthenticationSerializer):
    refresh_token = CharField(max_length=255)
    grant_type = CharField(max_length=20)


class IDSerializer(Serializer):
    id = IntegerField()


class IDSetSerializer(Serializer):
    idSet = IDSerializer(many=True)


class CategorySerializer(ModelSerializer):
    name = SerializerMethodField()
    icon = SerializerMethodField()
    isFavorite = SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'name',
            'icon',
            'id',
            'isFavorite'
        ]

    def get_name(self, obj):
        isPersian = self.context['isPersian']
        if isPersian:
            return obj.persianName
        else:
            return obj.name

    def get_isFavorite(self, obj):
        request = self.context['request']
        return obj in request.user.client.favoriteCategories.all()

    def get_icon(self, obj):
        try:
            request = self.context['request']
            image_url = obj.icon.url
            to_return = request.build_absolute_uri(image_url)
            return to_return
        except:
            return ""


class ArticleLeadSerializer(ModelSerializer):
    image = SerializerMethodField()
    isBookmarked = SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'title',
            'image',
            'leadText',
            'isBookmarked',
            'id',
        ]

    def get_image(self, obj):
        try:
            request = self.context['request']
            image_url = obj.image.url
            to_return = request.build_absolute_uri(image_url)
            return to_return
        except:
            return ""

    def get_isBookmarked(self, obj):
        request = self.context['request']
        return obj in request.user.client.bookmarkedArticles.all()


class ArticleSerializer(ModelSerializer):
    parts = SerializerMethodField()
    image = SerializerMethodField()
    author = SerializerMethodField()
    category = SerializerMethodField()
    creationDate = SerializerMethodField()
    tags = SerializerMethodField()
    isBookmarked = SerializerMethodField()
    relatedArticles = SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'parts',
            'title',
            'leadText',
            'id',
            'image',
            'author',
            'category',
            'creationDate',
            'tags',
            'isBookmarked',
            'relatedArticles',
        ]

    def get_parts(self, obj):
        parts = ArticlePart.objects.filter(article=obj).order_by('order')
        return ArticlePartSerializer(parts, many=True, context=self.context).data

    def get_image(self, obj):
        try:
            request = self.context['request']
            image_url = obj.image.url
            to_return = request.build_absolute_uri(image_url)
            return to_return
        except:
            return ""

    def get_author(self, obj):
        return AuthorSerializer(obj.author, context=self.context).data

    def get_category(self, obj):
        return CategorySerializer(obj.category, context=self.context).data

    def get_creationDate(self, obj):
        return obj.creationDate.date()

    def get_tags(self, obj):
        tags = obj.tags.all()
        return TagSerializer(tags, many=True, context=self.context).data

    def get_isBookmarked(self, obj):
        request = self.context['request']
        return obj in request.user.client.bookmarkedArticles.all()

    def get_relatedArticles(self, obj):
        return ""


class ArticlePartSerializer(ModelSerializer):
    image = SerializerMethodField()

    class Meta:
        model = ArticlePart
        fields = [
            'type',
            'title',
            'image',
            'content',
        ]

    def get_image(self, obj):
        try:
            request = self.context['request']
            image_url = obj.image.url
            to_return = request.build_absolute_uri(image_url)
            return to_return
        except:
            return ""


class TagSerializer(ModelSerializer):
    name = SerializerMethodField()

    class Meta:
        model = Tag
        fields = [
            'name',
        ]

    def get_name(self, obj):
        isPersian = self.context['isPersian']
        if isPersian:
            return obj.persianName
        else:
            return obj.name


class AuthorSerializer(ModelSerializer):
    name = SerializerMethodField()

    class Meta:
        model = Author
        fields = [
            'name',
        ]

    def get_name(self, obj):
        isPersian = self.context['isPersian']
        if isPersian:
            return obj.persianPublicName
        else:
            return obj.publicName

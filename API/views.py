import requests
from rest_framework import status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope

from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from API.serializers import (UserRegisterSerializer, LoginSerializer, RefreshTokenSerializer, CategorySerializer,
                             IDSetSerializer, ArticleLeadSerializer, ArticleSerializer, IDSerializer, LogoutSerializer)
from django.contrib.auth.models import User
from API.models import (Client, Category, Article)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print(request.data)
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            dataDictionary = serializer.validated_data
            print(dataDictionary)
            username = dataDictionary['username']
            password = dataDictionary['password']
            email = dataDictionary['email']
            data = dict()

            if User.objects.filter(username=username).exists():
                data['message'] = "client exists"
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.create(username=username, email=email, is_active=True)
            user.set_password(password)
            user.save()
            tokenData = dict()
            tokenData['client_id'] = dataDictionary['client_id']
            tokenData['client_secret'] = dataDictionary['client_secret']
            tokenData['username'] = dataDictionary['username']
            tokenData['password'] = dataDictionary['password']
            tokenData['grant_type'] = 'password'
            absolute_url = request.build_absolute_uri('/')
            url = absolute_url + "o/auth/token/"
            result = requests.post(url, data=tokenData)
            if result.status_code != 200:
                user.delete()
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Client.objects.create(user=user)
            return Response(result.json(), status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            dataDictionary = serializer.validated_data
            grant_type = dataDictionary['grant_type']
            if str(grant_type) != "password":
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            absolute_url = request.build_absolute_uri('/')
            url = absolute_url + "o/auth/token/"
            result = requests.post(url, data=serializer.data)
            if result.status_code != 200:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            return Response(result.json(), status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            dataDictionary = serializer.validated_data
            grant_type = dataDictionary['grant_type']
            if str(grant_type) != "refresh_token":
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            absolute_url = request.build_absolute_uri('/')
            url = absolute_url + "o/auth/token/"
            result = requests.post(url, data=serializer.data)
            if result.status_code != 200:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            return Response(result.json(), status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            absolute_url = request.build_absolute_uri('/')
            url = absolute_url + "o/auth/revoke_token/"
            result = requests.post(url, data=serializer.data)
            if result.status_code != 200:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            return Response(status=result.status_code)
        else:
            print(serializer.errors)
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class GetCategoriesView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer

    def get_serializer_context(self):
        try:
            isPersian = str(self.request.query_params.get('lang')) == "fa"
        except:
            isPersian = False
        return {'request': self.request, 'isPersian': isPersian}

    def get_queryset(self):
        return Category.objects.all()


class SubmitFavoriteCategoriesView(APIView):
    def post(self, request):
        serializer = IDSetSerializer(data=request.data)
        if serializer.is_valid():
            categoriesIdSet = serializer.validated_data['idSet']
            for categoryId in categoriesIdSet:
                if Category.objects.filter(id=categoryId['id']).exists() is False:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            client = Client.objects.get(user=request.user)
            for categoryId in categoriesIdSet:
                category = Category.objects.get(id=categoryId['id'])
                if category in client.favoriteCategories.all():
                    client.favoriteCategories.remove(category)
                else:
                    client.favoriteCategories.add(category)
            client.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class SearchArticlesView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ArticleLeadSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        try:
            user = self.request.user
            client = user.client
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            query_text = self.request.query_params.get('query')
            if query_text is None:
                query_text = ""
        except:
            query_text = ""
        try:
            isPersian = str(self.request.query_params.get('lang')) == "fa"
        except:
            isPersian = False
        articles = Article.objects.filter(
            Q(title__icontains=query_text) | Q(leadText__icontains=query_text),
            category__in=client.favoriteCategories.all(),
            isPersian=isPersian).order_by("-creationDate")
        return articles[:10]


class GetArticleView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            articleId = self.request.query_params.get('id')
            article = Article.objects.get(id=articleId)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ArticleSerializer(article, context={'request': request, 'isPersian': article.isPersian})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ToggleBookmarkArticleView(APIView):
    def post(self, request):
        try:
            user = self.request.user
            client = user.client
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = IDSerializer(data=request.data)
        if serializer.is_valid():
            articleId = serializer.validated_data['id']
            if Article.objects.filter(id=articleId).exists() is False:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            article = Article.objects.get(id=articleId)
            if article in client.bookmarkedArticles.all():
                client.bookmarkedArticles.remove(article)
            else:
                client.bookmarkedArticles.add(article)
            client.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

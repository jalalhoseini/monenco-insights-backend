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
from API.serializers import (UserRegisterSerializer,
                             LoginSerializer,
                             RefreshTokenSerializer,
                             LogoutSerializer,
                             ConfigsSerializer,
                             ToggleSetSerializer,
                             ArticleCompactSerializer,
                             ArticleSerializer,
                             ToggleSerializer,
                             )
from django.contrib.auth.models import User
from API.models import (Client, Category, Article, Configs)


# Fully OK
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            dataDictionary = serializer.validated_data
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
                data['message'] = "unexpected error"
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            Client.objects.create(user=user)
            return Response(result.json(), status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# Fully OK
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
                data = dict()
                data['message'] = "invalid username or password"
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            return Response(result.json(), status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


# Fully OK
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


# Fully OK
class LogoutView(APIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]

    def post(self, request):
        try:
            user = request.user
            client = user.client
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            absolute_url = request.build_absolute_uri('/')
            url = absolute_url + "o/auth/revoke_token/"
            result = requests.post(url, data=serializer.data)
            if result.status_code != 200:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            return Response(status=result.status_code)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


# Fully OK
class ConfigsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = self.request.user
            client = user.client
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            isPersian = str(self.request.query_params.get('lang')) == "fa"
        except:
            isPersian = False
        configs = Configs.objects.all().first()
        serializer = ConfigsSerializer(configs, context={'request': request, 'isPersian': isPersian})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


# Fully OK
class CategoryListToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            client = user.client
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = ToggleSetSerializer(data=request.data)
        if serializer.is_valid():
            toggleSet = serializer.validated_data['toggleSet']
            for toggleItem in toggleSet:
                if Category.objects.filter(id=toggleItem['id']).exists() is False:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            for toggleItem in toggleSet:
                category = Category.objects.get(id=toggleItem['id'])
                newState = toggleItem['newState']
                if newState:
                    if (category in client.favoriteCategories.all()) is False:
                        client.favoriteCategories.add(category)
                else:
                    if category in client.favoriteCategories.all():
                        client.favoriteCategories.remove(category)
            client.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# Fully OK
class ArticleSearchView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ArticleCompactSerializer

    def get_serializer_context(self):
        try:
            isPersian = str(self.request.query_params.get('lang')) == "fa"
        except:
            isPersian = False
        return {'request': self.request, 'isPersian': isPersian}

    def get_queryset(self):
        try:
            user = self.request.user
            client = user.client
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
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
        if query_text == "":
            return []
        articles = Article.objects.filter(
            Q(title__icontains=query_text) | Q(leadText__icontains=query_text),
            category__in=client.favoriteCategories.all(),
            isPersian=isPersian).order_by("-creationDate")
        return articles[:10]


# Fully OK
class ArticleBookmarkToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            client = user.client
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = ToggleSerializer(data=request.data)
        if serializer.is_valid():
            articleId = serializer.validated_data['id']
            newState = serializer.validated_data['newState']
            if Article.objects.filter(id=articleId).exists() is False:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            article = Article.objects.get(id=articleId)
            if newState:
                if (article in client.bookmarkedArticles.all()) is False:
                    client.bookmarkedArticles.add(article)
            else:
                if article in client.bookmarkedArticles.all():
                    client.bookmarkedArticles.remove(article)
            client.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# Fully OK
class ArticleBookmarkListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ArticleCompactSerializer

    def get_serializer_context(self):
        try:
            isPersian = str(self.request.query_params.get('lang')) == "fa"
        except:
            isPersian = False
        return {'request': self.request, 'isPersian': isPersian}

    def get_queryset(self):
        try:
            user = self.request.user
            client = user.client
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
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
        articles = client.bookmarkedArticles.filter(isPersian=isPersian).order_by("-creationDate")
        return articles


# Fully OK
class ArticleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            client = user.client
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            articleId = self.request.query_params.get('id')
            article = Article.objects.get(id=articleId)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ArticleSerializer(article, context={'request': request, 'isPersian': article.isPersian})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

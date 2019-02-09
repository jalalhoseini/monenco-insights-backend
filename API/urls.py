from django.conf.urls import url
from API.views import *

urlpatterns = [
    url(r'^authentication/register/', RegisterView.as_view()),
    url(r'^authentication/login/', LoginView.as_view()),
    url(r'^authentication/token/refresh/', RefreshTokenView.as_view()),
    url(r'^authentication/logout', LogoutView.as_view()),

    url(r'^category/list/', GetCategoriesView.as_view()),
    url(r'^category/edit/', SubmitFavoriteCategoriesView.as_view()),

    url(r'^article/search/', SearchArticlesView.as_view()),
    url(r'^article/bookmark/', ToggleBookmarkArticleView.as_view()),
    url(r'^article/', GetArticleView.as_view()),
]

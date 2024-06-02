from django.urls import path
from . import views

app_name ="scraper_app"

urlpatterns=[
    path("", views.scraper, name="scraper"),
    path("/reset_database",views.reset_database, name="reset_database"),
    path('/request_how_many_json_file',views.request_how_many_json_file, name="request_how_many_json_file"),
    path('/get_new_substances', views.search_for_newcomers, name="search_for_newcomers"),
    path("/get_witz",views.get_witz, name="get_witz"),
    path("/generate", views.generateJsonFile, name="generateJsonFile"),
    path("/processJsonInput", views.processJsonInput, name="ProcessJsonInput"),
    path('/my_api', views.my_api, name="my_api"),
    path('/delete_search_result', views.delete_search_results, name="delete_search_result")
    ]
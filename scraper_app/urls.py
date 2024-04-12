from django.urls import path
from . import views

app_name ="scraper_app"

urlpatterns=[
    path("", views.scraper, name="scraper"),
    path("/add_all", views.add_all_to_db, name="add_all_to_db"),
    path("/reset_database",views.reset_database, name="reset_database"),
    path('/request_how_many_json_file',views.request_how_many_json_file, name="request_how_many_json_file"),
    path('/get_new_substances', views.search_for_newcomers, name="search_for_newcomers"),
    path("/get_witz",views.get_witz, name="get_witz"),
    path("/get_smile_from_id",views.get_smile_from_id,name="get_name_from_id"),
]
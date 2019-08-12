from django.urls import path, re_path
from . import views


app_name = 'posts'
urlpatterns = [
    path('',views.posts_home,name='posts_home'),
    path('<int:post_id>/',views.posts_detail,name="posts_detail"),
    path('new/',views.posts_new,name="posts_new"),
    path('postslist/<str:name>/<str:slug>/',views.posts_list,name="posts_list"),
    #path('create/',views.post_create,name="post_create"),
    path('like/', views.posts_like, name='posts_like'),
    path('addcomment/<int:post_id>/',views.posts_add_comment,name='posts_add_comment'),
    path('remove/<int:comment_id>/',views.posts_remove_comment,name='posts_remove_comment'),
   # path('approve/<int:comment_id>/',views.posts_approve_comment,name='posts_approve_comment'),
    path('delete/<int:post_id>/',views.posts_delete,name='posts_delete'),
    path('edit/<int:post_id>/',views.posts_edit,name='posts_edit'),
    path('commentedit/<int:comment_id>/',views.posts_edit_comment,name="posts_edit_comment"),
    path('postssearch/',views.posts_search,name="posts_search"),
    #path('commnetlike/',views.comment_like,name='comment_like'),
    path('mypost/',views.posts_my,name="posts_my"),
    path('mycomment/',views.posts_mycomment,name="posts_mycomment"),
    path('mylike/', views.posts_mylike, name="posts_mylike")
]
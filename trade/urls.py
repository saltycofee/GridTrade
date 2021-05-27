from django.urls import path
from . import views

urlpatterns = [
    path('contorltask', views.ContorlTask, name='contorltask'),
    # path('crashthread', views.crashthread, name='crashthread'),
    path('querylist',views.getorderlist,name="getorderlist"),
    path('queryrecord',views.queryRecord,name="queryRecord"),
    path('wxentrance/', views.wx_entrance, name='wxentrance'),
    path('login',views.login,name ='login'),
    path('getapikey',views.getkey_info,name ='getapikey'),
    path('getaccountinfo',views.getaccountinfo,name='getaccountinfo'),
    path('create_task',views.create_task,name='create_task'),
    path('get_taskinfo',views.get_taskinfo,name='get_taskinfo')
    #path('token/', views.wx_token, name='token'),
]
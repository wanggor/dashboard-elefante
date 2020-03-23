"""myDashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from django.contrib.auth import views as auth_views

from accounts import views as accounts_views
from dashboard import views

urlpatterns = [
    path('admin/', admin.site.urls),

    
    #Get
    url(r'^$', views.home, name='home'),
    url(r'^notulensi/$', views.notulensi, name='natulensi'),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^validasi/$', views.validasi, name='validasi'),
    url(r'^register/$', accounts_views.register, name='register'),
    url(r'^saldo_awal/$', views.saldo_awal, name='saldo_awal'),
    url(r'^daftar_plan/$', views.daftar_plan, name='daftar_plan'),
    url(r'^daftar_material/$', views.daftar_material, name='daftar_material'),
    url(r'^daftar_mvt/$', views.daftar_mvt, name='daftar_mvt'),
    url(r'^delete_data/$', views.delete_data, name='delete_data'),
    url(r'^daftar_harga/$', views.daftar_harga, name='daftar_harga'),

    url(r'^edit_profile/$', accounts_views.edit_profile, name='editProfile'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^chart/$', views.chart,name='chart'),

    url(r'^password_change/$', auth_views.PasswordChangeView.as_view(template_name='password_change.html'),
        name='password_change'),
    url(r'^password_change_done/$', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'),
        name='password_change_done'),
    

    # lupa password
    url(r'^reset_password/$',
        auth_views.PasswordResetView.as_view(
            template_name='reset_password.html',
            email_template_name='password_reset_email.html',
            subject_template_name='password_reset_subject.txt'
        ),name='password_reset'),
    url(r'^reset/done/$',
        auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
        name='password_reset_confirm'),
    url(r'^reset/complete/$',
        auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
        name='password_reset_complete'),

    url(r'^report/(?P<pk>\d+)/$', views.report, name='report'),

    #Post
    url(r'^home_data/$', views.home_data, name='home_data'),

    url(r'^validate_data/$', views.validate_data, name='validate_data'),
    url(r'^delete_val_data/$', views.delete_val_data, name='delete_val_data'),
    url(r'^delete_val_data_all/$', views.delete_val_data_all, name='delete_val_data_all'),

    url(r'^upload_saldo/$', views.upload_saldo, name='upload_saldo'),
    url(r'^upload_plan/$', views.upload_plan, name='upload_saldo'),
    url(r'^upload_material/$', views.upload_material, name='upload_material'),
    url(r'^upload_mvt/$', views.upload_mvt, name='upload_mvt'),
    url(r'^upload_harga/$', views.upload_harga, name='upload_harga'),
    

    url(r'^upload_files/$', views.upload_files, name='upload_files'),
    url(r'^check_upload_laporan/$', views.check_upload_laporan, name='check_upload_laporan'),

    url(r'^getTableData/$', views.getTableData, name='getTableData'),
    url(r'^getNotulensi/$', views.getNotulensi, name='getNotulensi'),

    url(r'^updateNotulensi/$', views.updateNotulensi, name='updateNotulensi'),
    

]

# """
# URL configuration for algo_trading project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/5.1/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
# from django.contrib import admin
# from django.urls import include, path

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('login.urls')),
#     path('screener/', include('screener.urls')),
#     path('ml/', include('ml_dashboard.urls')), 
#     path('dashboard/', include('dashboard.urls')),
#     path('', include('dashboard.urls')), # Makes the dashboard the homepage
#     path('fundamentals/', include('fundamentals.urls')),
# ]

"""
URL configuration for algo_trading project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # FIX: Moved login app to its own '/login/' path to avoid conflict with the root URL.
    path('login/', include('login.urls')), 
    path("", include("login.urls")),  # Add this line
    
    # App-specific URLs
    path('screener/', include('screener.urls')),
    path('ml/', include('ml_dashboard.urls')), 
    path('fundamentals/', include('fundamentals.urls')),

    # FIX: The dashboard app now exclusively handles the root URL ('')
    # and its own prefixed URLs ('/dashboard/').
    path('dashboard/', include('dashboard.urls'))
]

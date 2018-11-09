"""icbckg URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
import graph.views
from django.views.generic import TemplateView
import tagging.views

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="search.html")),
    url(r'^schema/$', TemplateView.as_view(template_name="schema.html")),
    url(r'^display/$', TemplateView.as_view(template_name="display.html")),
    url(r'^tagging/$', TemplateView.as_view(template_name="tagging.html")),
    url(r'^QAs/$', TemplateView.as_view(template_name="QAs.html")),
    url(r'^search_from_2_file/$', TemplateView.as_view(template_name="search_from_2_file.html")),
    url(r'^search_from_web_pages/$', TemplateView.as_view(template_name="search_from_web_pages.html")),
    url(r'^schema_from_web_pages/$', TemplateView.as_view(template_name="schema_from_web_pages.html")),
    url(r'^next_job/$', TemplateView.as_view(template_name="next_job.html")),

    url(r'^api/graph/graph/', graph.views.graph),
    url(r'^api/graph/entity/', graph.views.entity),
    url(r'^api/tagging/get_data/', tagging.views.get_data),
    url(r'^api/tagging/submit_data/', tagging.views.submit_data),


    # url(r'^api/test/', graph.views.test11)
]

from django.urls import path

import core.views

urlpatterns = [
    path("", core.views.coreUrl),
    path("block/<int:value>/", core.views.blockUrl),
]

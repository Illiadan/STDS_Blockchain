from django.urls import path

import core.views

urlpatterns = [
    path("", core.views.coreUrl, name="dashboard"),
    path("block/<int:value>/", core.views.blockUrl, name="single_block"),
	path("mine", core.views.miningUrl, name="mining")
]

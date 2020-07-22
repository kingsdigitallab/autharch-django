from countries_plus.models import Country
from django.contrib import admin
from geonames_place.models import Place

admin.site.unregister(Country)


@admin.register(Country)
class ThirdPartyModelsAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        if request.user.is_superuser:
            return super().get_model_perms(request)

        return {}


admin.site.unregister(Place)


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    autocomplete_fields = ['class_description', 'country', 'feature_class']
    list_display = ['address', 'class_description', 'country']
    list_filter = ['class_description', 'country']
    search_fields = ['address', 'country__name', 'country__code']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term)

        if len(queryset) < 10 and len(search_term) > 3:
            Place.create_or_update_from_geonames(search_term)
            queryset, use_distinct = super().get_search_results(
                request, queryset, search_term)

        return queryset, use_distinct

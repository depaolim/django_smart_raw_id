from django.contrib.admin import ModelAdmin, widgets
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe


@user_passes_test(lambda u: u.is_staff)
def label_view(request, app_name, model_name, template_name="", multi=False, template_object_name="object"):
    from django.http import HttpResponse
    from django.shortcuts import render_to_response
    from django.db.models import get_model

    pk = request.GET.get("pk", "")
    model = get_model(app_name, model_name)
    url_id = "admin:%s_%s_change" % (app_name, model_name)
    obj_tuple = lambda o: (o, reverse(url_id, args=[o.pk]))
    try:
        if multi:
            if pk:
                ids = pk.split(",")
            model_template = "admin/raw_id_fields/%s/multi_%s.html" % (
                app_name, model_name)
            objects = [
                obj_tuple(obj) for obj in model.objects.filter(pk__in=ids)]
            extra_context = {template_object_name: objects, }
        else:
            model_template = "admin/raw_id_fields/%s/%s.html" % (
                app_name, model_name)
            extra_context = {
                template_object_name: obj_tuple(model.objects.get(pk=pk)),
            }
    except model.DoesNotExist:
        return HttpResponse("")
    return render_to_response((model_template, template_name), extra_context)


class SmartForeignKeyRawIdWidget(widgets.ForeignKeyRawIdWidget):
    def __init__(self, label_url, *args, **kwargs):
        self.label_url = label_url
        super(SmartForeignKeyRawIdWidget, self).__init__(*args, **kwargs)

    def label_for_value(self, value=None):
        return ""

    def render(self, name, value, attrs=None):
        attrs = attrs or {}
        mdl = (self.rel.to._meta.app_label, self.rel.to._meta.object_name.lower())
        attrs['data-chu'] = reverse("admin:%s_%s_changelist" % mdl)
        attrs['data-wsu'] = reverse("admin:{}".format(self.label_url), args=mdl)
        output = super(SmartForeignKeyRawIdWidget, self).render(name, value, attrs)
        return mark_safe(output)

    class Media:
        js = ("admin/js/smart_raw_id.js",)
        css = {
            'all': ('admin/css/smart_raw_id.css',)
        }


class SmartManyToManyRawIdWidget(widgets.ManyToManyRawIdWidget):
    def __init__(self, label_url, *args, **kwargs):
        self.label_url = label_url
        super(SmartManyToManyRawIdWidget, self).__init__(*args, **kwargs)

    def label_for_value(self, value):
        return u''

    def render(self, name, value, attrs=None):
        attrs = attrs or {}
        mdl = (self.rel.to._meta.app_label, self.rel.to._meta.object_name.lower())
        attrs['data-chu'] = reverse("admin:%s_%s_changelist" % mdl)
        attrs['data-wsu'] = reverse("admin:{}".format(self.label_url), args=mdl)
        output = super(SmartManyToManyRawIdWidget, self).render(name, value, attrs)
        return mark_safe(output)

    class Media:
        js = ("admin/js/smart_raw_id.js",)
        css = {
            'all': ('admin/css/smart_raw_id.css',)
        }


class SmartOneRawIdMixin(object):

    @property
    def admin_prefix_url(self):
        return "{}_{}".format(self.opts.app_label, self.opts.model_name)

    @property
    def one_label_url(self):
        return "{}_raw_id_label".format(self.admin_prefix_url)

    def get_urls(self):
        urls = super(SmartOneRawIdMixin, self).get_urls()
        from django.conf.urls import patterns, url
        my_urls = patterns(
            'smart_raw_id.admin',
            url(
                r'^label_view/(?P<app_name>[\w-]+)/(?P<model_name>[\w-]+)/$',
                'label_view',
                {'template_name': 'admin/raw_id_fields/label.html'},
                name=self.one_label_url,
                )
        )
        return my_urls + urls

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        from django.contrib.admin.options import get_ul_class
        from django.utils.translation import ugettext as _
        """
        Get a form Field for a ForeignKey.
        """
        db = kwargs.get('using')
        if db_field.name in self.raw_id_fields:
            kwargs['widget'] = SmartForeignKeyRawIdWidget(
                self.one_label_url, db_field.rel, self.admin_site, using=db)
        elif db_field.name in self.radio_fields:
            kwargs['widget'] = widgets.AdminRadioSelect(attrs={
                'class': get_ul_class(self.radio_fields[db_field.name]),
            })
            kwargs['empty_label'] = _('None') if db_field.blank else None

        if not 'queryset' in kwargs:
            queryset = self.get_field_queryset(db, db_field, request)
            if queryset is not None:
                kwargs['queryset'] = queryset

        return db_field.formfield(**kwargs)


class SmartManyRawIdMixin(object):

    @property
    def admin_prefix_url(self):
        return "{}_{}".format(self.opts.app_label, self.opts.model_name)

    @property
    def many_label_url(self):
        return "{}_raw_id_multi_label".format(self.admin_prefix_url)

    def get_urls(self):
        urls = super(SmartManyRawIdMixin, self).get_urls()
        from django.conf.urls import patterns, url
        my_urls = patterns(
            'smart_raw_id.admin',
            url(
                r'^label_view/(?P<app_name>[\w-]+)/(?P<model_name>[\w-]+)/multi/$',
                'label_view',
                {
                    'multi': True,
                    'template_object_name': 'objects',
                    'template_name': 'admin/raw_id_fields/multi_label.html'
                },
                name=self.many_label_url,
                )
        )
        return my_urls + urls

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # If it uses an intermediary model that isn't auto created, don't show
        # a field in admin.
        if not db_field.rel.through._meta.auto_created:
            return None
        db = kwargs.get('using')

        if db_field.name in self.raw_id_fields:
            kwargs['widget'] = SmartManyToManyRawIdWidget(self.many_label_url, db_field.rel, self.admin_site, using=db)
            kwargs['help_text'] = ''
        elif db_field.name in (list(self.filter_vertical) + list(self.filter_horizontal)):
            kwargs['widget'] = widgets.FilteredSelectMultiple(db_field.verbose_name, (db_field.name in self.filter_vertical))

        if not 'queryset' in kwargs:
            queryset = self.get_field_queryset(db, db_field, request)
            if queryset is not None:
                kwargs['queryset'] = queryset

        return db_field.formfield(**kwargs)


class SmartRawIdMixin(SmartOneRawIdMixin, SmartManyRawIdMixin):
    pass

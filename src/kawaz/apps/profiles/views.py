from django.http import HttpResponseRedirect
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView

from permission.decorators.classbase import permission_required
from .forms import ProfileForm
from .forms import AccountForm
from .forms import AccountFormSet
from kawaz.core.views.preview import SingleObjectPreviewMixin
from .models import Profile

class ProfileListView(ListView):
    model =  Profile

    def get_queryset(self):
        return Profile.objects.published(self.request.user)


@permission_required('profiles.change_profile')
class ProfileUpdateView(UpdateView):
    model = Profile
    form_class = ProfileForm
    formset_prefix = 'accounts'

    def get_object(self, queryset=None):
        if self.request.user.is_authenticated() and self.request.user:
            return self.request.user.profile
        return None

    def get_formset(self):
        kwargs = {
            'prefix': 'accounts',
        }
        if self.request.method in ('PUT', 'POST'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        if hasattr(self, 'object'):
            kwargs.update({
                'instance': self.object,
            })
        formset = AccountFormSet(**kwargs)
        return formset

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset = self.get_formset()
        return self.render_to_response(self.get_context_data(
            form=form, formset=formset))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset = self.get_formset()
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        self.object = form.save()
        # save formset instance. instances require 'profile' attribute thus
        # assign that attribute automatically
        instances = formset.save(commit=False)
        for instance in instances:
            instance.profile = self.request.user.profile
            instance.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(
            form=form, formset=formset))


@permission_required('profiles.view_profile')
class ProfileDetailView(DetailView):
    model = Profile
    slug_field = 'user__username'


class ProfilePreview(SingleObjectPreviewMixin, DetailView):
    model = Profile
    template_name = "profiles/components/profile_detail.html"

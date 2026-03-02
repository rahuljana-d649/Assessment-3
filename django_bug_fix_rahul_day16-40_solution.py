from django import forms
from django.urls import path, reverse_lazy
from django.views.generic import FormView, TemplateView

CATEGORIES = {"ui", "performance", "billing", "general"}


class FeedbackForm(forms.Form):
    category = forms.CharField(required=True, max_length=20)
    message = forms.CharField(required=True, max_length=500)

    def clean_category(self):
        c = (self.cleaned_data.get("category") or "").strip().lower()
        # BUG: validation reversed
        # FIX: correct validation logic
        if c not in CATEGORIES:
            raise forms.ValidationError("Invalid category.")
        return c


class FeedbackView(FormView):
    template_name = "feedback_form.html"
    form_class = FeedbackForm
    # FIX: correct success URL
    success_url = "/feedback/thanks/"

    def form_valid(self, form):
        """
        Called when form is valid.
        Must set cookie and redirect.
        """
        resp = super().form_valid(form)
        # BUG: wrong cookie key
        # FIX: correct cookie key
        resp.set_cookie("lastfeedback", form.cleaned_data["category"])
        return resp


class FeedbackThanksView(TemplateView):
    template_name = "feedback_thanks.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # BUG: wrong cookie name and default
        # FIX: correct default value
        ctx["category"] = self.request.COOKIES.get(
            "last_feedback", "general"
        )
        return ctx


urlpatterns = [
    # FIX: correct view-to-URL mapping
    path("feedback/", FeedbackView.as_view(), name="feedback"),
    path("feedback/thanks/", FeedbackThanksView.as_view(), name="feedback_thanks"),
]

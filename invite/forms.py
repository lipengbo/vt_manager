from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset

from invite.models import Invitation, Application

class InvitationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        if 'target_obj' in kwargs:
            target_obj = kwargs.get('target_obj')
            del kwargs['target_obj']
        else:
            target_obj = None
        super(InvitationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('submit', _('Invite')))
        if target_obj:
            target_type = ContentType.objects.get_for_model(target_obj)
            invited_user_ids = list(Invitation.objects.filter(target_id=target_obj.id,
                    target_type=target_type).values_list("to_user__id", flat=True))
            invited_user_ids.extend(target_obj.member_ids())
            self.fields['to_user'].queryset = User.objects.exclude(id__in=set(invited_user_ids))

    class Meta:
        fields = ("to_user", "message")
        model = Invitation

class ApplicationForm(forms.ModelForm):

    class Meta:
        fields = ("to_user", "message")
        model = Application

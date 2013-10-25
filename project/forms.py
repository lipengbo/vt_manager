#coding: utf-8
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions

from project.models import Project, Category

class ProjectForm(forms.ModelForm):

    category_name = forms.RegexField(regex=u"^[\w\u4e00-\u9fa5]+$", required=True, max_length=64)

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('submit', '创建'))

    class Meta:
        model = Project
        fields = ("name", "description", "islands")
        widgets = {"islands": forms.SelectMultiple(attrs={"class": "hide"})}

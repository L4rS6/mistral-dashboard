# Copyright 2015 Huawei Technologies Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from mistraldashboard import api


class CreateForm(forms.SelfHandlingForm):
    definition_source = forms.ChoiceField(
        label=_('Definition Source'),
        choices=[('file', _('File')),
                 ('raw', _('Direct Input'))],
        widget=forms.Select(
            attrs={'class': 'switchable',
                   'data-slug': 'definitionsource'})
    )
    definition_upload = forms.FileField(
        label=_('Definition File'),
        help_text=_('A local definition to upload.'),
        widget=forms.FileInput(
            attrs={'class': 'switched',
                   'data-switch-on': 'definitionsource',
                   'data-definitionsource-file': _('Definition File')}
        ),
        required=False
    )
    definition_data = forms.CharField(
        label=_('Definition Data'),
        help_text=_('The raw contents of the definition.'),
        widget=forms.widgets.Textarea(
            attrs={'class': 'switched',
                   'data-switch-on': 'definitionsource',
                   'data-definitionsource-raw': _('Definition Data'),
                   'rows': 4}
        ),
        required=False
    )

    def clean(self):
        cleaned_data = super(CreateForm, self).clean()

        if cleaned_data.get('definition_upload'):
            files = self.request.FILES
            cleaned_data['definition'] = files['definition_upload'].read()
        elif cleaned_data.get('definition_data'):
            cleaned_data['definition'] = cleaned_data['definition_data']
        else:
            raise forms.ValidationError(
                _('You must specify the definition source.'))

        return cleaned_data

    def handle(self, request, data):
        try:
            api.action_create(request, data['definition'])
            msg = _('Successfully created action.')
            messages.success(request, msg)

            return True
        except Exception:
            msg = _('Failed to create action.')
            redirect = reverse('horizon:mistral:actions:index')
            exceptions.handle(request, msg, redirect=redirect)
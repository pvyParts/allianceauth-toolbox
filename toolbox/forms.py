from django import forms


class SearchEveName(forms.Form):
    name = forms.CharField(label='Name to Search for', max_length=500)


class AddEveNote(forms.Form):
    reason = forms.CharField(label='Reason', widget=forms.Textarea)
    blacklisted = forms.BooleanField(label='Blacklist', required=False)


class AddComment(forms.Form):
    comment = forms.CharField(label='Comment', widget=forms.Textarea)


class AddRestrictedComment(forms.Form):
    comment = forms.CharField(label='Comment', widget=forms.Textarea)


class EditNote(forms.Form):
    reason = forms.CharField(label='Reason', widget=forms.Textarea)
    blacklisted = forms.BooleanField(label='Blacklist', required=False)

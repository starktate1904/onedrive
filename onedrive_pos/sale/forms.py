from django import forms
from .models import Sale

class SaleForm(forms.ModelForm):
    customer_name = forms.CharField(max_length=255, required=True)  # Add other fields as needed

    class Meta:
        model = Sale
        fields = ['customer_name', 'branch']  # Only include branch if it's editable

    def __init__(self, *args, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)
        # Disable branch field if not editable
        if not kwargs.get('initial') or not kwargs['initial'].get('branch'):
            self.fields['branch'].disabled = True
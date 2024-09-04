from django import forms

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField()
    # few checks after file uploading
    #The form must only allow xls or xlsx files
     #File size must not cross 2 MB
    def clean_excel_file(self):
        file = self.cleaned_data.get('excel_file')
        if not file.name.endswith('.xls') and not file.name.endswith('.xlsx'):
            raise forms.ValidationError('Invalid file format. Only .xls or .xlsx files are allowed.')
        if file.size > 2 * 1024 * 1024:  # 2 MB limit
            raise forms.ValidationError('File size exceeds 2MB.')
        return file

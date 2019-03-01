# from组件
from django import forms

from django.forms import widgets

from django.core.exceptions import NON_FIELD_ERRORS,ValidationError

from employee.models import *

from rbac.models import UserInfo

from django.contrib import auth

from multiselectfield.forms.fields import MultiSelectFormField


class Regist(forms.Form):
    error_msg={'required':'该字段不能为空'}
    username = forms.CharField(
        min_length=6,
        label='用户名',
        error_messages=error_msg,
    )
    password = forms.CharField(
        min_length=6,
        label='密码',
        error_messages=error_msg,
        widget=widgets.PasswordInput() # 隐藏密码
    )
    r_pwd = forms.CharField(
        min_length=6,
        label='确认密码',
        error_messages=error_msg,
        widget=widgets.PasswordInput()
    )
    email = forms.EmailField(
        min_length=6,
        label='邮箱',
    )
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for filed in self.fields.values():
            filed.widget.attrs.update({'class':'form-control'})

    def clean_username(self):
        val = self.cleaned_data.get('username')
        user = UserInfo.objects.filter(username=val).first()
        if user:
            raise ValidationError('用户已存在!')
        else:
            return val

    def clean_password(self):
        val = self.cleaned_data.get('password')
        if val.isdigit():
            raise ValidationError('密码不能是纯数字!')
        else:
            return val

    def clean(self):
        pwd = self.cleaned_data.get('password')
        r_pwd = self.cleaned_data.get('r_pwd')
        if pwd and r_pwd and pwd!=r_pwd:
            self.add_error('r_pwd',ValidationError('两次密码不一致!'))
        else:
            return self.cleaned_data


class Login(forms.Form):
    error_msg={'required':'该字段不能为空'}
    username = forms.CharField(
        min_length=6,
        label='用户名',
        error_messages=error_msg,
    )
    password = forms.CharField(
        min_length=6,
        label='密码',
        error_messages=error_msg,
        widget=widgets.PasswordInput() # 隐藏密码
    )

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for filed in self.fields.values():
            filed.widget.attrs.update({'class':'form-control'})


    #  判断用户名密码
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user_obj = auth.authenticate(username=username,password=password)
        if user_obj:
            return self.cleaned_data
        else:
            self.add_error('password',ValidationError('用户名或密码错误!'))



class CustomerModelForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields='__all__'
        widgets = {
            'birthday': widgets.TextInput(attrs={'type': 'date'})
        }

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
            if not isinstance(field,MultiSelectFormField):
                field.widget.attrs.update({'class':'form-control'})



class ConsultRecordModelForm(forms.ModelForm):


    class Meta:
        model = ConsultRecord
        fields = '__all__'
        widgets = {
            'date':widgets.TextInput(attrs={'type':'date'})
        }


    def __init__(self, *args,user_info={}, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field, MultiSelectFormField):
                field.widget.attrs.update({'class': 'form-control'})

            if field.label == '跟进人':

                field.choices=((user_info['user_id'],user_info['name']),)



class ClassStudyRecordModelForm(forms.ModelForm):


    class Meta:
        model = ClassStudyRecord
        fields = '__all__'
        widgets = {
            'date':widgets.TextInput(attrs={'type':'date'})
        }


    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
            if not isinstance(field,MultiSelectFormField):
                field.widget.attrs.update({'class':'form-control'})



class StudentStudyRecordModelForm(forms.ModelForm):


    class Meta:
        model = StudentStudyRecord
        fields = ['student','classstudyrecord']


    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
            if not isinstance(field,MultiSelectFormField):
                field.widget.attrs.update({'class':'form-control'})



class ClassScoreModelForm(forms.ModelForm):


    class Meta:
        model = StudentStudyRecord
        fields = ['score','homework_note',]


    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
            if not isinstance(field,MultiSelectFormField):
                field.widget.attrs.update({'class':'form-control'})

import datetime

from PIL import Image, ImageDraw, ImageFont

from io import BytesIO

import random

from django.contrib import auth

from django.core.exceptions import NON_FIELD_ERRORS, ValidationError

from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from django.views import View
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q,Count
from django.forms import modelformset_factory
from django.utils.decorators import method_decorator

from employee.models import *
from employee.form import *
from employee.utils.page import Pagination

from rbac.models import *
from rbac.server.initial_session import initial_session



def index(request):
    return render(request, 'base/index.html')


# 用户登录
def login(request):
    if request.method == "GET":
        login_form = Login()
        regist_form = Regist()
        return render(request, 'account/login.html', locals())
    else:
        response = {'user': None, 'errors': ''}
        login_form = Login(request.POST)
        auth_code = request.POST.get('auth_code')
        # 先验证验证码
        if auth_code and auth_code.upper() == request.session.get('auth_code').upper():
            # form 表单验证
            if login_form.is_valid():
                # auth组件登录
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user_obj = auth.authenticate(username=username, password=password)

                auth.login(request, user_obj)
                response['user'] = login_form.cleaned_data.get('username')

                # 获取用户权限
                request.session['user_id'] = user_obj.pk
                initial_session(user_obj,request)
            else:
                response['errors'] = login_form.errors
        # 验证码错误
        else:
            response['errors'] = {'auth_code': ['验证码错误!']}

        return JsonResponse(response)


# 验证码
def get_auth_code(request):
    def get_random_color():
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    img = Image.new('RGB', (350, 38), get_random_color())
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("static/font/kumo.ttf", 32)

    auth_code = ''
    for i in range(6):
        random_num = str(random.randint(0, 9))
        random_lowalp = chr(random.randint(97, 122))
        random_upperalp = chr(random.randint(65, 90))
        random_char = random.choice([random_num, random_lowalp, random_upperalp])
        draw.text((i * 45 + 50, 0), random_char, get_random_color(), font=font)
        auth_code += random_char

    # 验证图片的写与读
    f = BytesIO()
    img.save(f, 'png')
    img = f.getvalue()
    request.session['auth_code'] = auth_code
    return HttpResponse(img)


# 用户注册
def reg(request):
    if request.method == 'GET':
        regist_form = Regist()
        return render(request, 'account/reg.html', locals())
    else:
        response = {'user': None, 'errors': ""}
        regist_form = Regist(request.POST)

        if regist_form.is_valid():
            regist_form.cleaned_data.pop('r_pwd')
            user_obj = UserInfo.objects.create_user(**regist_form.cleaned_data)
            response['user'] = user_obj.username
        else:
            response['errors'] = regist_form.errors
        return JsonResponse(response)



class CustomerView(View):

    @method_decorator(login_required)
    def get(self, request):
        if reverse('customer_view') == request.path:
            customer_list = Customer.objects.filter(consultant=None)
            label = '公户列表'
        else:
            customer_list = Customer.objects.filter(consultant=request.user)
            label = '私户列表'
        # 模糊查询
        val = request.GET.get('q')
        field = request.GET.get('field')
        if val:
            q = Q()
            q.children.append((field+'__contains',val),)
            customer_list = customer_list.filter(q)

        # 分页
        current_page_num = request.GET.get("page")
        pagination = Pagination(current_page_num,customer_list.count(),request)
        page_html = pagination.page_html()
        customer_list = customer_list[pagination.start:pagination.end]

        next = "?next=%s"%(request.path)

        return render(request, 'customer/customer_view.html', {
                                                     'customer_list':customer_list,
                                                     'label':label,
                                                     'pagination':pagination,
                                                     'page_html':page_html,
                                                     'next':next,
                                                     })


    def post(self, request):
        print(request.POST)
        func_str = request.POST.get('action')
        select_customer_list = request.POST.getlist('select_customer_pk')
        if not hasattr(self,func_str):
            return HttpResponse('非法输入!')
        else:
            func = getattr(self,func_str)
            queryset = Customer.objects.filter(pk__in=select_customer_list)
            ret = func(request,queryset)
            if ret:
                return ret
            return redirect(request.path)


    def patch_delete(self,request,queryset):
        queryset.delete()


    def patch_reverse_gs(self,request,queryset):
        # 处理多个用户操作同一条记录 先进来的优先
        ret = queryset.filter(consultant__isnull=True)
        if ret:
            print('queryset',queryset)
            queryset.update(consultant=request.user)
        else:
            return HttpResponse("手速太慢!")


    def patch_reverse_sg(self,request,queryset):
        queryset.update(consultant = None )



class AddEditCustomerView(View):

    def label(self,request):
        if request.path == reverse('add_customer'):
            label = '添加客户信息'
        else:
            label = '编辑客户信息'
        return label

    def get(self,request,customer_id=None):
        customer_obj = Customer.objects.filter(pk=customer_id).first()
        form = CustomerModelForm(instance=customer_obj)
        label= self.label(request)

        return render(request, 'customer/add_edit_customer.html', {'form':form, 'label':label})


    def post(self,request,customer_id=None):
        customer_obj = Customer.objects.filter(pk=customer_id).first()
        form = CustomerModelForm(request.POST,instance=customer_obj)
        if form.is_valid():
            form.save()
            return redirect(request.GET.get("next"))
        else:
            label = self.label(request)
            return render(request, 'consult/add_edit_consult_record.html', {'form':form, 'customer_obj':customer_obj, 'label':label})



class ConsultRecordView(View):


    def get(self,request):
        consult_record_list = ConsultRecord.objects.filter(consultant=request.user)
        customer_id = request.GET.get('customer_id')
        if customer_id:
            consult_record_list = consult_record_list.filter(customer_id=customer_id)
        return render(request, 'consult/consult_record.html', {'consult_record_list':consult_record_list})



class AddEditConsultRecordView(View):


    def get(self,request,consult_record_id=None):
        consult_record_obj = ConsultRecord.objects.filter(pk=consult_record_id).first()

        if request.path == reverse('add_consult_record'):
            label='添加跟进记录'
        else:
            label='编辑跟进记录'
        user_id = request.user.pk
        name = request.user.username
        user_info = {'user_id': user_id, 'name': name}
        form = ConsultRecordModelForm(instance=consult_record_obj,user_info=user_info)
        return render(request, 'consult/add_edit_consult_record.html', {'form':form, 'label':label})


    def post(self,request,consult_record_id=None):
        consult_record_obj = ConsultRecord.objects.filter(pk=consult_record_id).first()
        user_id = request.user.pk
        name = request.user.username
        user_info = {'user_id': user_id, 'name': name}
        form = ConsultRecordModelForm(request.POST,instance=consult_record_obj,user_info=user_info)
        if form.is_valid():
            form.save()
            return redirect(reverse('consult_record'))
        else:
            return render(request, 'consult/add_edit_consult_record.html', {'form':form, 'consult_record_obj':consult_record_obj})



class ClassStudyRecordView(View):


    def get(self, request):
        class_study_record_list = ClassStudyRecord.objects.all()
        label = '班级学习记录'

        # 分页
        current_page_num = request.GET.get("page")
        pagination = Pagination(current_page_num,class_study_record_list.count(),request)
        page_html = pagination.page_html()
        customer_list = class_study_record_list[pagination.start:pagination.end]

        next = "?next=%s"%(request.path)

        return render(request, 'study/class_study_record.html', {
                                                     'class_study_record_list':class_study_record_list,
                                                     'label':label,
                                                     'pagination':pagination,
                                                     'page_html':page_html,
                                                     'next':next,
                                                     })


    def post(self, request):
        func_str = request.POST.get('action')
        select_class_study_record_list = request.POST.getlist('select_class_study_record_pk')
        if not hasattr(self,func_str):
            return HttpResponse('非法输入!')
        else:
            func = getattr(self,func_str)

            queryset = ClassStudyRecord.objects.filter(pk__in=select_class_study_record_list)
            ret = func(request,queryset)
            if ret:
                return ret
            return redirect(request.path)


    def patch_create(self,request,queryset):
        for class_study_record_obj in queryset:
            student_list = class_study_record_obj.class_obj.student.all()
            for student in student_list:
                if StudentStudyRecord.objects.filter(student=student,classstudyrecord=class_study_record_obj):
                    pass
                else:
                    StudentStudyRecord.objects.create(student=student,classstudyrecord=class_study_record_obj)


    def patch_delete(self,request,queryset):
        queryset.delete()



class AddEditClassStudyRecordView(View):


    def get(self,request,class_study_record_id=None):
        class_study_record_obj = ClassStudyRecord.objects.filter(pk=class_study_record_id).first()

        if request.path == reverse('add_class_study_record'):
            label='添加班级学习记录'
        else:
            label='编辑班级学习记录'

        form = ClassStudyRecordModelForm(instance=class_study_record_obj)
        return render(request, 'study/add_edit_class_study_record.html', {'form':form, 'label':label})


    def post(self,request,class_study_record_id=None):
        class_study_record_obj = ClassStudyRecord.objects.filter(pk=class_study_record_id).first()
        form = ClassStudyRecordModelForm(request.POST,instance=class_study_record_obj)
        if form.is_valid():
            form.save()
            return redirect(reverse('class_study_record'))
        else:
            return render(request, 'study/add_edit_class_study_record.html', {'form':form, 'class_study_record_obj':class_study_record_obj})



class DeleteClassStudyRecordView(View):
    def get(self,request,class_study_record_id=None):
        ClassStudyRecord.objects.filter(pk=class_study_record_id).first().delete()
        next = request.GET.get('next')
        return redirect(next)



class StudentStudyRecordView(View):


    def get(self, request):
        student_study_record_list = StudentStudyRecord.objects.all()
        label = '学生学习记录'

        # 分页
        current_page_num = request.GET.get("page")
        pagination = Pagination(current_page_num,student_study_record_list.count(),request)
        page_html = pagination.page_html()
        customer_list = student_study_record_list[pagination.start:pagination.end]

        next = "?next=%s"%(request.path)

        return render(request, 'study/student_study_record.html', {
                                                     'student_study_record_list':student_study_record_list,
                                                     'label':label,
                                                     'pagination':pagination,
                                                     'page_html':page_html,
                                                     'next':next,
                                                     })


    def post(self, request):
        func_str = request.POST.get('action')
        select_class_study_record_list = request.POST.getlist('select_class_study_record_pk')
        if not hasattr(self,func_str):
            return HttpResponse('非法输入!')
        else:
            func = getattr(self,func_str)

            queryset = ClassStudyRecord.objects.filter(pk__in=select_class_study_record_list)
            ret = func(request,queryset)
            if ret:
                return ret
            return redirect(request.path)



class AddStudentStudyRecordView(View):


    def get(self,request):
        label = '添加学生学习记录'
        form = StudentStudyRecordModelForm()
        return render(request, 'study/add_student_study_record.html', {'form':form, 'label':label})


    def post(self,request,student_study_record_id=None):
        student_study_record_obj = StudentStudyRecord.objects.filter(pk=student_study_record_id).first()
        form = StudentStudyRecordModelForm(request.POST,instance=student_study_record_obj)
        if form.is_valid():
            form.save()
            return redirect(reverse('student_study _record'))
        else:
            return render(request, 'study/add_student_study_record.html', {'form':form, 'student_study_record_obj':student_study_record_obj})



class DeleteStudentStudyRecordView(View):


    def get(self,request,student_study_record_id=None):
        StudentStudyRecord.objects.filter(pk=student_study_record_id).first().delete()
        next = request.GET.get('next')
        return redirect(next)



# class ClassScoreView(View):
#
#
#     def get(self,request,class_study_record_id=None):
#         label = '录入学生成绩'
#         choice_list = StudentStudyRecord.score_choices
#         student_study_record_list = StudentStudyRecord.objects.filter(classstudyrecord_id=class_study_record_id)
#         return render(request,'class_score_view.html',
#                       {'student_study_record_list':student_study_record_list,
#                        'label':label,
#                        'choice_list':choice_list,
#                        })
#
#
#     def post(self,request,class_study_record_id=None):
#         data = copy.deepcopy(request.POST)
#         del data['csrfmiddlewaretoken']
#         data=dict(data)
#         print(data)
#         for key,value in data.items():
#             if value[0] != '':
#                 value[0] = int(value[0])
#             else:
#                 value[0] = None
#             StudentStudyRecord.objects.filter(id=int(key)).update(score=value[0],homework_note=value[1])


# formset组件
class ClassScoreView(View):


    def get(self, request, class_study_record_id=None):
        label = '录入学生成绩'
        choice_list = StudentStudyRecord.score_choices
        student_study_record_list = StudentStudyRecord.objects.filter(classstudyrecord_id=class_study_record_id)
        formset=modelformset_factory(model=StudentStudyRecord,form=ClassScoreModelForm,extra=0)
        queryset = student_study_record_list
        formset = formset(queryset=queryset)
        return render(request, 'study/class_score_view1.html', locals())


    def post(self,request,class_study_record_id=None):
        formset = modelformset_factory(model=StudentStudyRecord, form=ClassScoreModelForm, extra=0)
        formset = formset(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect(reverse('class_study_record'))
        else:
            return render(request, 'study/class_score_view1.html', locals())




class ShowDealView(View):


    def get(self,request):
        date = request.GET.get('date','today')
        today = datetime.datetime.now().date()
        datetime.timedelta(weeks=1)
        if date == 'today':
            label = '今天报名学员'
            date_choice = today
            condition = {'deal_date': date_choice}
        elif date == 'yesterday':
            label = '昨天报名学员'
            delta = datetime.timedelta(days=1)
            date_choice = today-delta
            condition = {'deal_date':date_choice}
        elif date == 'last_week':
            label = '过去一周报名学员'
            delta = datetime.timedelta(weeks=1)
            date_choice = today - delta
            condition = {'deal_date__gte': date_choice}
        customer_list = Customer.objects.filter(**condition)
        ret = customer_list.filter(consultant__department_id=2).values('consultant_id').annotate(c=Count('consultant_id')).values_list('consultant__username','c')
        coordinate = []
        data = []
        for item in list(ret):
            coordinate.append(item[0])
            data.append(item[1])

        print(coordinate,data)
        return render(request, 'consult/deal.html', {'customer_list':customer_list, 'label':label, 'data':data, 'coordinate':coordinate})



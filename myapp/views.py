from django.shortcuts import render,redirect

from django.views.generic import View

from django.utils import timezone

from myapp.forms import CategoryForm,TransactionForm,TransactionFilterForm,RegistrationForm,LoginForm

from myapp.models import Category,Transaction

from django.db.models import Sum

from django.contrib.auth import authenticate,login,logout

from django.contrib import messages

from myapp.decorators import signin_required

#fn decortr=>mthd_decortr     dispatch
#@method_decorator(signin_required,name="dispatch")
from django.utils.decorators import method_decorator


@method_decorator(signin_required,name="dispatch")
class CategoryCreateView(View):

    def get(self,request,*args,**kwargs):

        if not request.user.is_authenticated:

            messages.error(request,"Invalid Session")

            return redirect("signin")

        form_instance=CategoryForm(user=request.user)


        qs=Category.objects.filter(owner=request.user)

        return render(request,"category_add.html",{"form":form_instance,"categories":qs})
    
    def post(self,request,*args,**kwargs):

        if not request.user.is_authenticated:

            messages.error(request,"Invalid Session")

            return redirect("signin")

        form_instance=CategoryForm(request.POST,user=request.user,files=request.FILES)

        if form_instance.is_valid():

            form_instance.instance.owner=request.user          
                
            form_instance.save()

            return redirect("category-add")
        
        else:

            return render(request,"category_add.html",{"form":form_instance})
        

#url> localhost:8000/category/{int:pk}/change/
@method_decorator(signin_required,name="dispatch")
class CategoryUpdateView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        category_object=Category.objects.get(id=id)

        form_instance=CategoryForm(instance=category_object)

        return render(request,"category_edit.html",{"form":form_instance})

    def post(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        cat_object=Category.objects.get(id=id)

        form_instance=CategoryForm(request.POST,instance=cat_object)

        if form_instance.is_valid():

            form_instance.save()

            return redirect("category-add")
        
        else:
            return render(request,"category_edit.html",{"form":form_instance})








@method_decorator(signin_required,name="dispatch")
class TransactionCreateView(View):

    def get(self,request,*args,**kwargs):

        form_instance=TransactionForm()

        cur_month=timezone.now().month

        cur_year=timezone.now().year

        categories=Category.objects.filter(owner=request.user)

        qs=Transaction.objects.filter(created_date__month=cur_month,created_date__year=cur_year,owner=request.user)

        return render(request,"transaction_add.html",{"form":form_instance,"transaction":qs,"categories":categories})
    
    def post(self,request,*args,**kwargs):

        form_instance=TransactionForm(request.POST)

        if form_instance.is_valid():

            form_instance.instance.owner=request.user

            form_instance.save()

            return redirect("transaction-add")
        
        else:

            return render(request,"transaction_add.html",{"form":form_instance})

        


#url:lc:8000/transaction/<int:pk>/change/

@method_decorator(signin_required,name="dispatch")
class TransactionUpdateView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        transaction_object=Transaction.objects.get(id=id)

        form_instance=TransactionForm(instance=transaction_object)

        return render(request,"transaction_edit.html",{"form":form_instance})

    def post(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        transaction_object=Transaction.objects.get(id=id)

        form_instance=TransactionForm(request.POST,instance=transaction_object)

        if form_instance.is_valid():

            form_instance.save()

            return redirect("transaction-add")
        
        else:

            return render(request,"transaction_edit.html",{"form":form_instance})





@method_decorator(signin_required,name="dispatch")
class TransactionDeleteView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        Transaction.objects.get(id=id).delete()

        return redirect("transaction-add")
    




@method_decorator(signin_required,name="dispatch")
class ExpenseSummaryView(View):

    def get(self,request,*args,**kwargs):

        cur_month=timezone.now().month

        cur_year=timezone.now().year

        qs=Transaction.objects.filter(created_date__month=cur_month,created_date__year=cur_year,owner=request.user)

        total_expense=qs.values("amount").aggregate(total=Sum("amount"))

        category_summmary=qs.values("category_object__name").annotate(total=Sum("amount"))

        payment_summary=qs.values("payment_methode").annotate(total=Sum("amount"))
      

        data={
            "total_expense":total_expense.get("total"),
            "category_summary":category_summmary,
            "payment_summary":payment_summary,

        } 

        return render(request,"expense_summary.html",data)






@method_decorator(signin_required,name="dispatch")
class TransactionSummaryView(View):

    def get(self,request,*args,**kwargs):

        form_instance=TransactionFilterForm()

        cur_month=timezone.now().month

        cur_year=timezone.now().year

        if "start_date" in request.GET and "end_date" in request.GET:

            st_date=request.GET.get("start_date")

            end_date=request.GET.get("end_date")
            
            qs=Transaction.objects.filter(created_date__range=(st_date,end_date))

            total_expense=qs.values("amount").aggregate(total=Sum("amount"))  

        else:

            qs=Transaction.objects.filter(created_date__month=cur_month,created_date__year=cur_year)

            total_expense=qs.values("amount").aggregate(total=Sum("amount"))  
    
        return render(request,"transaction_summary.html",{"transaction":qs,"form":form_instance,'total_expense':total_expense.get('total')})
    
    
    

class ChartView(View):

    def get(self,request,*args,**kwargs):
        
        return render(request,"chart.html")
    


class SignUpView(View):

    def get(self,request,*args,**kwargs):

        form_instance=RegistrationForm()

        return render(request,"register.html",{"form":form_instance})

    def post(self,request,*args,**kwargs):

        form_instance=RegistrationForm(request.POST)    
    
        if form_instance.is_valid():

            form_instance.save()

            messages.success(request,"Account Created Successfullly")

            print("account created successfully")

            return redirect("signin")
        
        else:
            print("failed to create account")

            messages.error(request,"Failed to create account")

            return render(request,"register.html",{"form":form_instance}) 
            



class SignInView(View):

    def get(self,request,*args,**kwargs):

        form_instance=LoginForm()

        return render(request,"login.html",{"form":form_instance})

    def post(self,request,*args,**kwargs):

        #step1:extract usename and password from Loginform

        form_instance=LoginForm(request.POST)

        if form_instance.is_valid():

            data=form_instance.cleaned_data #{"username":"django","password":"Password@123"}

            user_obj=authenticate(request,**data)

            if user_obj:

                login(request,user_obj)

                messages.success(request,"Login Successfully")

                return redirect("summary")
            
        messages.error(request,"Failed to Login")

        return render(request,"login.html",{"form":form_instance})



        #step2:Authenticate user with  usename and password

        #start the sesssion


@method_decorator(signin_required,name="dispatch")
class SignOutView(View):

    def get(self,request,*args,**kwargs):

        logout(request)

        return redirect("signin")
    
















    








        
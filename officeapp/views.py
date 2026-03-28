from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from .models import Employee, Attendance
from .models import WorkReport
from .models import OfficeExpense
from itertools import groupby
from django.db.models import Max
from operator import attrgetter
from collections import defaultdict
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from decimal import Decimal
from .models import Project
from django.shortcuts import get_object_or_404, redirect


def project_add(request):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        Project.objects.create(
            name=name,
            description=description,
            image=image
        )
        return redirect('project_view')

    return render(request, 'project_add.html')

def project_view(request):
    projects = Project.objects.all().order_by('-id')  # latest top
    return render(request, 'project_view.html', {'projects': projects})

def project_delete(request, id):
    project = get_object_or_404(Project, id=id)
    project.delete()
    return redirect('project_view')


def attendance_view(request):
    attendance_list = Attendance.objects.all().order_by('-date')

    return render(request, 'attendance_view.html', {
        'attendance_list': attendance_list
    })

def workreport_pdf(request, report_no):

    reports = WorkReport.objects.filter(report_no=report_no).order_by("sl_no","id")

    grouped = defaultdict(list)

    for r in reports:
        key = (r.sl_no, r.site)
        grouped[key].append(r)

    context = {
        "reports": dict(grouped)
    }

    template = get_template("workreport_pdf.html")
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{report_no}.pdf"'

    pisa.CreatePDF(html, dest=response)

    return response





def workreport_view(request):

    reports = WorkReport.objects.all().order_by(
        "-date", "-report_no", "sl_no", "id"
    )

    final_group = defaultdict(list)

    for r in reports:
        report_key = r.report_no
        final_group[report_key].append(r)

    structured_data = {}

    for report_no, items in final_group.items():

        site_group = defaultdict(list)

        for item in items:
            site_key = (item.sl_no, item.site)
            site_group[site_key].append(item)

        structured_data[report_no] = {
            "date": items[0].date if items else None,
            "sites": dict(site_group)
        }

    return render(request, "workreport_view.html", {
        "reports": structured_data
    })

def workreport_add(request):

    if request.method == "POST":

        last_report = WorkReport.objects.aggregate(Max('report_no'))['report_no__max']
        next_report_no = 1 if last_report is None else last_report + 1

        sl_no_list = request.POST.getlist('sl_no[]')
        site_list = request.POST.getlist('site[]')
        labour_list = request.POST.getlist('labour_type[]')
        nos_list = request.POST.getlist('nos[]')
        remarks_list = request.POST.getlist('remarks[]')

        current_sl = None
        current_site = None

        total_rows = len(labour_list)
        

        for i in range(total_rows):

            sl_val = sl_no_list[i].strip() if i < len(sl_no_list) else ""
            site_val = site_list[i].strip() if i < len(site_list) else ""
            labour = labour_list[i].strip() if i < len(labour_list) else ""
            nos_val = nos_list[i] if i < len(nos_list) else ""
            remarks_val = remarks_list[i] if i < len(remarks_list) else ""

            # ✅ NEW SITE ROW
            if sl_val and site_val:
                current_sl = int(sl_val)
                current_site = site_val

            # ❌ skip only if labour empty
            if not labour:
                continue

            # ❌ skip if site not defined
            if current_sl is None or current_site is None:
                continue

            WorkReport.objects.create(
                report_no=next_report_no,
                date=date.today(),
                sl_no=current_sl,
                site=current_site,
                labour_type=labour,
                nos=int(nos_val) if nos_val else 0,
                remarks=remarks_val,
            )

        return redirect("workreport_add")

    return render(request, "workreport_add.html", {
        "today": date.today()
    })


def workreport_delete(request, report_no):
    WorkReport.objects.filter(report_no=report_no).delete()
    return redirect('workreport_view')





def expense_add(request):

    if request.method == "POST":

        last_report = OfficeExpense.objects.aggregate(Max('report_no'))['report_no__max']
        next_report_no = 1 if last_report is None else last_report + 1

        sl_list = request.POST.getlist('sl_no[]')
        item_list = request.POST.getlist('item[]')
        dept_list = request.POST.getlist('department[]')
        amount_list = request.POST.getlist('amount[]')
        remark_list = request.POST.getlist('remark[]')
        paid = request.POST.get("paid") or 0
        for i in range(len(item_list)):

            item = item_list[i].strip()
            if not item:
                continue

            OfficeExpense.objects.create(
                report_no = next_report_no,
                date = date.today(),
                sl_no = sl_list[i],
                item = item,
                department = dept_list[i],
                amount = amount_list[i],
                remark = remark_list[i],
                paid = paid
            )

        return redirect("expense_view")

    return render(request,"expense_add.html",{"today":date.today()})


def expense_view(request):

    expenses = OfficeExpense.objects.all().order_by("-report_no","sl_no")

    grouped = defaultdict(list)

    for e in expenses:
        grouped[e.report_no].append(e)

    report_data = {}

    for report_no, rows in grouped.items():

        total = sum(r.amount for r in rows)

        paid = rows[0].paid   # ✅ same for all rows

        balance = total - paid

        report_data[report_no] = {
        "rows": rows,
        "total": total,
        "paid": paid,
        "balance": balance
    }

    return render(request,"expense_view.html",{
        "reports": report_data
    })

def attendance(request):
    if request.method == "POST":
        employee_id = request.POST.get('employee')
        time_in = request.POST.get('time_in')
        time_out = request.POST.get('time_out')
        status = request.POST.get('status')

        employee = Employee.objects.get(id=employee_id)

        Attendance.objects.create(
            employee=employee,
            time_in=time_in,
            time_out=time_out,
            status=status
        )
        return redirect('attendance')

    employees = Employee.objects.all()
    attendance_list = Attendance.objects.all().order_by('-id')

    return render(request, 'attendance.html', {
        'employees': employees,
        'attendance_list': attendance_list
    })

def expense_delete(request, report_no):

          OfficeExpense.objects.filter(report_no=report_no).delete()

          return redirect("expense_view")


    



def expense_pdf(request, report_no):

    expenses = OfficeExpense.objects.filter(report_no=report_no)

    total = sum((e.amount for e in expenses), Decimal(0))

    paid = expenses[0].paid if expenses else Decimal(0)

    balance = total - paid

    template = get_template("expense_pdf.html")

    html = template.render({
        "expenses": expenses,
        "total": total,
        "paid": paid,
        "balance": balance,
        "report_no": report_no
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="expense_{report_no}.pdf"'

    pisa.CreatePDF(html, dest=response)

    return response
    
# SIDEBAR → EMPLOYEES (ADD ONLY)
def add_employee(request):
    if request.method == 'POST':
        Employee.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            department=request.POST['department'],
            position=request.POST['position'],
            joined_date=request.POST['joined_date'],
        )
        return redirect('add_employee')

    
    return render(request, "employee.html")


def view_employees(request):
    employees = Employee.objects.all().order_by('-id')
    return render(request, 'employee_list.html', {'employees': employees})






def projects(request):
    return render(request, 'projects.html')

def reports(request):
    return render(request, 'reports.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def login(request):
    if request.method=="GET":
         return render(request,"login.html")
    elif request.method=="POST":
        username=request.POST["usernam"]
        password=request.POST["passwor"]
        user=authenticate(request,username=username,password=password)
        if user:
            return redirect("/dashboard")
        else:
            return HttpResponse("invalid")
        

def register(request):
    if request.method=="GET":
         return render(request,"register.html")
    elif request.method=="POST":
        username=request.POST["username"]
        password=request.POST["password"]
        try:
            User.objects.get(username=username)
            return HttpResponse("user already exist")
        except User.DoesNotExist as e:
            user=User.objects.create_user(username=username,password=password)
            user.save()    
            return redirect("/login")

def dashboard(request):
    if request.method=="GET":
         return render(request,"dashboard.html")

# Create your views here.

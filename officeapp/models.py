from django.contrib.auth.models import User
from django.db import models




class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    joined_date = models.DateField()

    def _str_(self):
        return self.name
# Create your models here.
class Attendance(models.Model):
    employee =  employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time_in = models.TimeField()
    time_out = models.TimeField()
    status = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.employee} - {self.date}"

class WorkReport(models.Model):
    report_no = models.IntegerField(default=1)
    date = models.DateField(auto_now_add=True)
    sl_no = models.IntegerField(null=True, blank=True)
    site = models.CharField(max_length=200, blank=True)
    labour_type = models.CharField(max_length=200)
    nos = models.IntegerField(null=True, blank=True)
    remarks = models.TextField(blank=True)


    def __str__(self):
        return f"{self.site} - {self.date}"


class OfficeExpense(models.Model):

    report_no = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    sl_no = models.IntegerField()
    item = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    remark = models.TextField(blank=True)
    paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.item


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='projects/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
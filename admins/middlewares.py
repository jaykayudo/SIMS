from .models import Department
class DepartmentMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        

    def __call__(self, request):
        request.department = None
        if 'department' in request.session:
            department_id = request.session['department']
            try:
                department = Department.objects.get(id = department_id)
                request.department = department
            except (Department.DoesNotExist, Department.MultipleObjectsReturned):
                pass

        response = self.get_response(request)
        return response

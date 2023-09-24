from admins.models import User, Student

class MatricNumberAuthBackend:
    """
    Authenticate using email address
    """

    def authenticate(self,request,username = None, password = None):
    
        try: 
            student = Student.objects.get(matric_number = username)
            user = User.objects.get(id = student.user.id)
            if user.check_password(password):
                return user
            return None
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None
        except (Student.DoesNotExist, Student.MultipleObjectsReturned):
            return None
    def get_user(self,user_id):
        try:
            user = User.objects.get(pk  = user_id)
            return user
        except User.DoesNotExist:
            return None
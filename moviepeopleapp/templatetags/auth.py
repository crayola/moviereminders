from django import template
from longerusername.forms import AuthenticationForm

register = template.Library()

def login_form(value, arg):
    return AuthenticationForm().as_p

register.filter('login_form', login_form)
from flask import Blueprint, render_template
from flaskr.main.models import (
    Employees
)

main_bp = Blueprint('main', __name__, template_folder='templates')


@main_bp.route('/')
def top_menu():
    employees = Employees.select_employees()
    return render_template(
        'main/top.html',
        employees=employees
    )

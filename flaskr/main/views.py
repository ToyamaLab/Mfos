from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__, template_folder='templates')


@main_bp.route('/')
def top_menu():
    return render_template('main/top.html')
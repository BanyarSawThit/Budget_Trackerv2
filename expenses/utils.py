from datetime import date


def get_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def get_selected_period(request):

    today = date.today()

    session_month = request.session.get('month', today.month)
    selected_month = get_int(request.GET.get('month'), session_month)
    request.session['month'] = selected_month

    session_year = request.session.get('year', today.year)
    selected_year = get_int(request.GET.get('year'), session_year)
    request.session['year'] = selected_year

    return selected_month, selected_year

def get_selected_user(request):

    session_user = request.session.get('user', request.user.id)
    selected_user = get_int(request.GET.get('user'), session_user)
    request.session['user'] = selected_user
    return selected_user

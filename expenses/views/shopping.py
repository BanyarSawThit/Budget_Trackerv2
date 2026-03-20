from django.contrib.auth.decorators import login_required


@login_required
def shopping_add():
    return None


@login_required
def shopping_edit():
    return None


@login_required
def shopping_delete():
    return None
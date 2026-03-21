from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from expenses.forms import ShoppingForm
from expenses.models import ShoppingItem


@login_required
def shopping_view(request):
    """
    1. Let users add shopping item here
    2. Display all shopping items here
    3. let users edit and delete items
    :param request:
    :return:
    """
    items = ShoppingItem.objects.all().order_by('-created_at')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            form = ShoppingForm(request.POST)
            if form.is_valid():
                form.save()

            return redirect('shopping')
        elif action == 'delete':
            item_id = request.POST.get('item_id')
            shopping_item = get_object_or_404(ShoppingItem, id=item_id)
            shopping_item.delete()
            return redirect('shopping_page')
    else:
        form = ShoppingForm()


    context = {
        'form': form,
        'shopping_list': items,
    }

    return render(request, 'shopping/shopping_page.html', context)

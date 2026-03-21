from expenses.models import ShoppingItem


def shopping_preview(request):
    """
    display shopping items
    :param request:
    :return:
    """
    shopping = ShoppingItem.objects.all().order_by('-created_at')

    context = {
        'shopping': shopping[:5],
        'shopping_count': shopping.count()
    }

    return context
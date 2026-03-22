from decimal import Decimal

def convert_context(request):
    selected_currency = request.session.get('currency', 'THB')

    match selected_currency:
        case 'MMK':
            rate = Decimal('127.8')
        case _:
            rate = Decimal('1.0')


    context = {
        'rate': rate,
        'selected_currency': selected_currency
    }

    return context
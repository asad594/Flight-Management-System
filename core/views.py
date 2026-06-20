from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Flight, Booking, Payment, Notification
from .factories import DomainFactory
from .strategies import CreditCardStrategy, EasyPaisaStrategy, PayPalStrategy, PaymentContext
from .observers import booking_notifier
from .singleton import AppConfigManager
from django.utils import timezone

def home(request):
    config = AppConfigManager()
    flights = Flight.objects.all()[:3]
    return render(request, 'core/home.html', {
        'flights': flights,
        'system_name': config.get_setting('system_name')
    })

def about_view(request):
    return render(request, 'core/about.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def search_flights(request):
    origin = request.GET.get('origin', '')
    destination = request.GET.get('destination', '')
    flights = Flight.objects.filter(origin__icontains=origin, destination__icontains=destination)
    return render(request, 'core/search.html', {'flights': flights})

@login_required
def book_flight(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        # 1. Create Booking using Factory
        booking = DomainFactory.create_booking(request.user, flight)
        
        # 2. Process Payment using Strategy
        strategy_map = {
            'card': CreditCardStrategy(),
            'easypaisa': EasyPaisaStrategy(),
            'paypal': PayPalStrategy()
        }
        strategy = strategy_map.get(payment_method, CreditCardStrategy())
        context = PaymentContext(strategy)
        payment_result = context.execute_payment(flight.price)
        
        # 3. Create Payment record
        Payment.objects.create(
            booking=booking,
            amount=flight.price,
            method=payment_method,
            transaction_id=f"TXN-{timezone.now().timestamp()}"
        )
        
        # 4. Notify using Observer
        booking_notifier.notify(request.user, f"Your flight {flight.flight_number} to {flight.destination} is confirmed! {payment_result}")
        
        return redirect('my_bookings')
        
    return render(request, 'core/book.html', {'flight': flight})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/my_bookings.html', {
        'bookings': bookings,
        'notifications': notifications
    })

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')
    flights = Flight.objects.all()
    bookings = Booking.objects.all()
    return render(request, 'core/admin_dashboard.html', {
        'flights': flights,
        'bookings': bookings
    })

@login_required
def admin_fleet(request):
    if not request.user.is_staff:
        return redirect('home')
    flights = Flight.objects.all()
    return render(request, 'core/admin_fleet.html', {'flights': flights})

@login_required
def admin_bookings(request):
    if not request.user.is_staff:
        return redirect('home')
    bookings = Booking.objects.all()
    return render(request, 'core/admin_bookings.html', {'bookings': bookings})

@login_required
def admin_users(request):
    from django.contrib.auth.models import User
    if not request.user.is_staff:
        return redirect('home')
    users = User.objects.all()
    return render(request, 'core/admin_users.html', {'users': users})

from django.shortcuts import render
from .models import Post, Referral, Profile, Services
from django.shortcuts import render,redirect
from .forms import SignupForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib import messages
import random
import string
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from decimal import Decimal
from .models import ProductScheme,Services
from datetime import datetime, timedelta

# View to handle Product Scheme Management
def product_scheme_manage(request):
    if request.method == 'POST':
        # Get form data from POST request
        investment = Decimal(request.POST.get('investment'))
        total = Decimal(request.POST.get('total'))
        days = int(request.POST.get('days'))

        # Calculate the start and end date
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)

        # Create a new ProductScheme object and save it to the database
        scheme = ProductScheme.objects.create(
            investment=investment,
            total=total,
            days=days,
            start_date=start_date,
            end_date=end_date
        )

        # Return the scheme details to be displayed in the popup
        return render(request, 'product_scheme_manage.html', {
            'scheme': scheme,
            'start_date': start_date.strftime('%m/%d/%Y'),
            'end_date': end_date.strftime('%m/%d/%Y')
        })

    # If it's a GET request, just display the empty form
    return render(request, 'product_scheme_manage.html')


def payment_screen(request):
    return render(request, 'payment.html')

def generate_referral_code():
    """Generate a unique 8-character referral code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('index')  # Redirect authenticated users to home

    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            #print("Form is valid")  # Debug message
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Create profile with referral code and save KYC details
            referral_code = generate_referral_code()
            referred_by = request.POST.get('referred_by', None)

            referred_by_profile = None
            if referred_by:
                try:
                    referred_by_profile = Profile.objects.get(referral_code=referred_by)
                except Profile.DoesNotExist:
                    referred_by_profile = None

            #print(f"Generated referral code: {referral_code}")  # Debug message
            profile = Profile.objects.create(
                user=user,
                referral_code=referral_code,
                referred_by=request.POST.get('referred_by', None),
                kyc_document = form.cleaned_data.get('kyc_document'),
                kyc_document_type = form.cleaned_data.get('kyc_document_type'),
                pan_card=form.cleaned_data.get('pan_card'),
                bank_passbook=form.cleaned_data.get('bank_passbook'),
            )

            # Track referral and rewards
            if referred_by_profile:
                referred_by_profile.referrals_made += 1
                referred_by_profile.rewards_earned += 10.00  # Example reward
                referred_by_profile.save()
                Referral.objects.create(referred_by=referred_by_profile, referred_user=user)

            auth_login(request, user)
            messages.success(request, "Signup successful! Welcome aboard!")
            return JsonResponse({'success': True, 'referral_code': referral_code})
        
        else:
            # Process form errors and send them as JSON response
            errors = {
                field: [error['message'] for error in error_list] 
                for field, error_list in form.errors.get_json_data().items()
            }
            return JsonResponse({'success': True, 'referral_code': referral_code})

    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, "Login successful! Welcome back!")
            return redirect('index')  
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'login.html', {'form': form})

@login_required
def profile_view(request):
    # Fetch user profile data
    profile = request.user.profile
    return render(request, 'profile.html', {'profile': profile})


def logout_view(request):
    logout(request)
    return redirect('login')

def index(request):
    dict_eve={
        'post':Post.objects.all()
    }
    return render(request,'index.html',dict_eve)

def about(request):
    return render(request,'about.html')


def terms(request):
    return render(request,'terms.html')

def contact(request):
    return render(request,'contact.html')

def privacy(request):
    return render(request,'privacy.html')
    
def refar(request):
    return render(request,'refar.html')

def services(request):
    return render(request,'services.html')

@login_required
def referral_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user_profile = Profile.objects.get(user=request.user)

    # Generate referral link
    if not user_profile.referral_code:
        user_profile.referral_code = generate_referral_code()
        user_profile.save()

    # Fetch referral details
    referrals = Referral.objects.filter(referred_by=user_profile)
    referral_count = referrals.count()
    total_rewards = user_profile.rewards_earned

    referral_link = f"https://example.com/referral/{user_profile.referral_code}"

    context = {
        'referral_code': user_profile.referral_code,
        'referral_link': referral_link,
        'referral_count': referral_count,
        'total_rewards': total_rewards,
    }
    return render(request, 'refar.html', context)

def services_view(request):
    return render(request, 'services.html', {'service': services})
from django.shortcuts import render
from .models import Post
from django.shortcuts import render,redirect
from .forms import SignupForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib import messages
#from django.core.files.storage import default_storage
import random
import string
from django.http import JsonResponse
from .models import Profile
from django.conf import settings
from django.contrib.auth import logout

# Create your views here.
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
            print(f"Generated referral code: {referral_code}")  # Debug message
            profile = Profile.objects.create(
                user=user,
                referral_code=referral_code,
                referred_by=request.POST.get('referred_by', None),
                kyc_document = form.cleaned_data.get('kyc_document'),
                kyc_document_type = form.cleaned_data.get('kyc_document_type'),
                pan_card=form.cleaned_data.get('pan_card'),
                bank_passbook=form.cleaned_data.get('bank_passbook'),
            )

            auth_login(request, user)
            messages.success(request, "Signup successful! Welcome aboard!")
            return JsonResponse({'success': True, 'referral_code': referral_code})
        
            #auth_login(request, user)
            #messages.success(request, "Signup successful! Welcome aboard!")
            #return JsonResponse({
                #'success': True,
                #'referral_code': referral_code,
            #})
            
        else:
            # Process form errors and send them as JSON response
            errors = {
                field: [error['message'] for error in error_list] 
                for field, error_list in form.errors.get_json_data().items()
            }
            return JsonResponse({'success': False, 'errors': errors})

        #else:
            # Process errors into a user-friendly format
            #errors = {field: error.get_json_data() for field, error in form.errors.items()}
            #return JsonResponse({'success': False, 'errors': errors})

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


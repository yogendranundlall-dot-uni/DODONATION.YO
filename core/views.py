from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm, DonorProfileForm, ReceiverProfileForm
from .models import User
import logging

# Set up logging
logger = logging.getLogger(__name__)

def index(request):
    """
    This view renders the homepage.
    """
    # This line finds 'core/index.html' (which extends base.html) 
    # and returns it to the browser.
    return render(request, 'core/index.html')

def register(request):
    """
    Handles user registration for both Donors and Receivers.
    """
    if request.method == 'POST':
        # Initialize forms with POST data
        user_form = UserRegistrationForm(request.POST)
        donor_form = DonorProfileForm(request.POST)
        receiver_form = ReceiverProfileForm(request.POST)

        # Check the user form first
        if user_form.is_valid():
            role = user_form.cleaned_data.get('role')
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            # The role is already set by the form, so we just save
            user.save()

            # Now, handle the profile based on the role
            try:
                if role == User.Role.DONOR and donor_form.is_valid():
                    profile = donor_form.save(commit=False)
                    profile.user = user
                    profile.save()
                    messages.success(request, 'Donor account created successfully!')
                    return redirect('index')
                
                elif role == User.Role.RECEIVER and receiver_form.is_valid():
                    profile = receiver_form.save(commit=False)
                    profile.user = user
                    profile.save()
                    messages.success(request, 'Receiver account created successfully! It will be reviewed by an admin.')
                    return redirect('index')
                
                # Handle invalid profile forms
                else:
                    # If the profile form (donor or receiver) is invalid,
                    # we must delete the user we just created to avoid an orphan user.
                    logger.warning(f"Registration failed for user {user_form.cleaned_data.get('username')} due to invalid profile form.")
                    user.delete() # Rollback user creation
                    # Manually add profile errors to be displayed
                    if role == User.Role.DONOR:
                        messages.error(request, f"Please correct the errors in the Donor Profile: {donor_form.errors.as_text()}")
                    elif role == User.Role.RECEIVER:
                         messages.error(request, f"Please correct the errors in the Receiver Profile: {receiver_form.errors.as_text()}")
                    else:
                        messages.error(request, 'There was an error with your profile information. Please check the fields.')


            except Exception as e:
                # Log the error and delete the partial user to avoid orphans
                logger.error(f"Error creating profile for user {user.username}: {e}")
                user.delete() # Rollback user creation on profile error
                messages.error(request, 'An unexpected error occurred while creating your profile. Please try again.')
        
        # If user_form is invalid, fall through to render forms with errors
        else:
             messages.error(request, f"Please correct the errors in the Account Details: {user_form.errors.as_text()}")

    else:
        # GET request
        user_form = UserRegistrationForm()
        donor_form = DonorProfileForm()
        receiver_form = ReceiverProfileForm()

    context = {
        'user_form': user_form,
        'donor_form': donor_form,
        'receiver_form': receiver_form
    }
    # This is the correct path
    return render(request, 'core/register.html', context)


from django.shortcuts import render, HttpResponse, redirect 
from django.contrib import messages
import bcrypt
from .models import User, Quote
from django.db.models import Count

'''
 Registration process
1. Show them the registration form -- send them a HTML page
2. Submit the form -- create a url and a method to handle the form data
    2a. Validate
    2b. Hash password
    2c. Create the user
'''
# Registration Process Step 1
def index(request):
    return render(request, 'quote_dash/index.html')

# Registration Process Step 2
def register(request):
    valid = True
    # Registration Validation == Step 2a
    if len(request.POST['first_name']) < 3:
        valid = False
        messages.error(request, 'First name must be more than 3 characters')
    if len(request.POST['last_name']) < 3:
        valid = False
        messages.error(request, 'Last name must be more than 3 characters')
    if len(request.POST['email']) < 3:
        valid = False
        messages.error(request, 'Email must be more than 3 characters')
    if len(request.POST['password']) < 8:
        valid = False
        messages.error(request, 'Password must be more than 8 characters')
    if not request.POST['password'] == request.POST['password_confirmation']:
        valid = False
        messages.error(request, 'Password and password confirmation need to match')

    if not valid:
        return redirect('/')

    else:
        # Registration Process Step 2b
        # bcrypt.hashpw(THE_PASSWORD_FROM_THE_FORM, SALT)
        # Salt add variation in our alghorithm to make the hash more random
        hashed_pw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())
        if User.objects.filter(email=request.POST['email']).exists():
            messages.error(request, 'User with this email already exists. Please login')
            return redirect('/')
        
        # Registration Process Step 2c.
        User.objects.create(first_name=request.POST['first_name'], last_name=request.POST['last_name'], email=request.POST['email'], password=hashed_pw)
        messages.success(request, 'Registration succesful. Please login.')

        return redirect('/')

'''
Login Process
1. Show the user the login page
2. Submit the form == create a url and a method
    2a. Validate
    2b. Check password
    2c. Log the user in

'''
def login(request):
    try:
        user = User.objects.get(email=request.POST['email'])
        # Check password
        # bcript.checkpw(THE_PASSWORD_FROM_THE_FORM, THE_PASSWORD_FROM_THE_DATABASE)
        checked_pw = bcrypt.checkpw(request.POST['password'].encode(), user.password.encode())
        if checked_pw:
            request.session['logged_in'] = True
            request.session['user_id'] = user.id
            return redirect('/dashboard')

        else:
            messages.error(request, 'Email/password do not match. Try again.')
            return redirect('/')
    
    except User.DoesNotExist:
        messages.error(request, 'User with this email does not exist. Please register.')
        return redirect('/')

def dashboard(request):
    if not 'user_id' in request.session:
        messages.error(request, 'You need to log in to view this page.')
        return redirect('/')
    all_quotes = Quote.objects.annotate(Count('liked_users'))

    context = {
        'logged_user': User.objects.get(id=request.session['user_id']),
        'all_quotes' : all_quotes,
        }
    
    return render(request, 'quote_dash/dashboard.html', context)

def add_quote(request):
    valid = True
    #  Validation author
    if len(request.POST['author']) < 4:
        valid = False
        messages.error(request, 'Author must be more than 3 characters')
    if len(request.POST['desc']) < 11:
        valid = False
        messages.error(request, 'Quote must be more than 10 characters')
    if not valid:
        return redirect('/dashboard')

    Quote.objects.create(author=request.POST['author'], desc=request.POST['desc'], user=User.objects.get(id=request.session['user_id']))

    return redirect('/dashboard')

def editacc(request, user_id):
    this_user_edit = User.objects.get(id=int(user_id))
    context = {
        'this_user_edit': this_user_edit,
    }
    return render(request, 'quote_dash/editacc.html', context)

def replace(request):
    valid = True
    # Edition Validation == Step 1
    if len(request.POST['first_name']) < 3:
        valid = False
        messages.error(request, 'First name must be more than 3 characters')
    if len(request.POST['last_name']) < 3:
        valid = False
        messages.error(request, 'Last name must be more than 3 characters')
    if len(request.POST['email']) < 3:
        valid = False
        messages.error(request, 'Email must be more than 3 characters')
    if valid:
        if User.objects.exclude(id=request.session['user_id']).filter(email=request.POST['email']):
            valid = False
            messages.error(request, 'User with this email already exists')
        else:
            # Edition Process Step 2
            this_user = User.objects.get(id=request.session['user_id'])
            this_user.first_name = request.POST['first_name']
            this_user.last_name = request.POST['last_name']
            this_user.email = request.POST['email']
            this_user.save()
            messages.success(request, 'Update succesful!')
    return redirect('/myaccount/'+str(request.session['user_id']))

def user_quotes(request, user_id):
    only_this_quotes = Quote.objects.filter(user_id=int(user_id))
    this_user = User.objects.get(id=int(user_id))
    context = {
        'only_this_quotes': only_this_quotes,
        'this_user': this_user,
    }
    return render(request, 'quote_dash/user_quotes.html', context)

def liked_quote(request, quote_id, user_id):
    # Add liked_users - liked_quotes relation
    this_user = User.objects.get(id=int(user_id))
    this_quote = Quote.objects.get(id=int(quote_id))
    if not this_user in this_quote.liked_users.all():
        this_quote.liked_users.add(this_user)
    return redirect('/dashboard')

def delete_quote(request, quote_id):
    this_quote = Quote.objects.get(id=int(quote_id))
    this_quote.delete() # deletes that particular record
    return redirect('/dashboard')

def logout(request):
    request.session.clear()
    return redirect('/')
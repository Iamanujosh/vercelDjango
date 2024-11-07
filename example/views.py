from django.shortcuts import render, redirect
from . import forms
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.conf import settings
import os
import requests
import os
import google.generativeai as genai
from django.shortcuts import render
from django.http import JsonResponse
import base64
from django.utils.safestring import mark_safe
from django.core.files.storage import default_storage
from .models import WardrobeItem,UserInfo
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.conf import settings
from django.contrib.auth.models import User
from .models import WardrobeItem
import os
import pdfplumber

# Configure the API key
my_api_key = 'AIzaSyDwcpxJ34DnWKBEFPC78FAiQ5kKQd8yXC4'
genai.configure(api_key=my_api_key)


history = []

generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]
# Assuming this is the generative model library you're using

def extract_pdf_data(pdf_path):
    data = {}
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Extracting all the text from the PDF
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text()

            # Assuming you extract text line by line and parse based on format
            lines = full_text.split("\n")
            
            # Example parsing based on what appears in the image you provided
            data["email"] = lines[2].split(":")[1].strip()
            data["date_joined"] = lines[3].split(":")[1].strip()
            
            # Parsing wardrobe items, assuming they start at a certain line
            wardrobe_items = []
            for line in lines[5:]:
                if "Item:" in line:
                    item_details = line.split()
                    wardrobe_items.append({
                        "item": item_details[1],
                        "category": item_details[3],
                        "last_worn": " ".join(item_details[6:])  # Ensures proper extraction
                    })
            data["wardrobe_items"] = wardrobe_items

    except Exception as e:
        print(f"Error while extracting PDF data: {e}")
    
    return data

# def generate_system_prompt(extracted_data):
    # Start with a basic introduction
system_prompt = """
    You're a style suggestion chatbot.

    Here is the wardrobe information for the user:
    
    """
    # Add user details
    # system_prompt += f"Email: {extracted_data['email']}\n"
    # system_prompt += f"Date Joined: {extracted_data['date_joined']}\n\n"

    # # Add wardrobe items
    # system_prompt += "Wardrobe Items:\n"
    # for item in extracted_data['wardrobe_items']:
    #     system_prompt += f"- {item['item']} (Category: {item['category']}, Last Worn: {item['last_worn']})\n"

    # # Finish with style suggestion capabilities
    # system_prompt += """
    # Based on the above wardrobe items and when they were last worn, suggest outfits or new items that might complement the user's style. 
    # If an item hasn't been worn in a while, suggest ways to incorporate it into their wardrobe.
    # """

    # return system_prompt

# Assuming the file is in the 'media/user_pdfs/' directory
pdf_file_path = os.path.join('media', 'user_pdfs', 'user_anushkaaa1720_wardrobe_info.pdf')

# Extract data from PDF
data = extract_pdf_data(pdf_file_path)

# Generate system prompt
system_prompt = system_prompt

# Assuming 'genai' is your generative model package
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,  # Ensure this is defined earlier
    safety_settings=safety_settings,      # Ensure this is defined earlier
    system_instruction=system_prompt
)

print("System Prompt:", system_prompt)


# function to handle user text and photo request
def chatbot(request):
     
     context = {}

     if request.method == "POST":
        image_file = request.FILES.get('image', None)
        user_input = request.POST.get('user_input', None)
       

       
        if image_file:
            temp_dir = os.path.join(settings.BASE_DIR, 'temp')
  
            if not os.path.exists(temp_dir):
                print("Creating temp directory...")
                print(temp_dir)
                os.makedirs(temp_dir)
    
            image_path = default_storage.save(os.path.join('temp', image_file.name), image_file)
           
            absolute_image_path = default_storage.path(image_path)

            print(f"Image path: {absolute_image_path}")  

            with open(absolute_image_path, "rb") as image:
                image_data = image.read()
            \
            image_data_base64 = base64.b64encode(image_data).decode('utf-8')
           
            image_part = {
                "mime_type": image_file.content_type,  # Ensure correct MIME type
                "data": image_data_base64  # Use Base64-encoded string
            }

            prompt_parts = [image_part, system_prompt] if not user_input else [user_input, image_part, system_prompt]

            # Generate response using the model
            response = model.generate_content(prompt_parts)
            
            if response:
                context['message'] =response.text
                bot_response = response.text
                return JsonResponse({'bot_response': bot_response})

            # Clean up the temporary file
            os.remove(image_path)
        elif user_input:
            context['message'] = "No matching data found. Please provide more details."

            chat_session = model.start_chat(history=history)
            response = chat_session.send_message(user_input)
            model_response = response.text
            example_message = "<b>Hello!</b> This message is <i>italicized</i>."


            
            # Append user and bot messages to the history
            history.append({"role": "user", "parts": [user_input]})
            history.append({"role": "model", "parts": [model_response]})
            
            # Return JSON response for the bot's reply
            context = {
            'message': history,
            'example_message': mark_safe(example_message)  # Mark as safe for rendering
        }
            print(history)
            

            return JsonResponse({
                'bot_response': model_response,
                'history': history
            })
        
        else:
            # If neither image nor text is provided, show an error message
            context['error'] = "Please provide an image or text input for analysis."


     generate_user_pdf(request.user)

     return render(request, 'example/chatbot.html', context)

def generate_user_pdf(user):
    # Get user's wardrobe items
    wardrobe_items = WardrobeItem.objects.filter(user=user)

    # Define the file path to save the PDF
    pdf_filename = f"user_{user.username}_wardrobe_info.pdf"
    pdf_filepath = os.path.join(settings.MEDIA_ROOT, 'user_pdfs', pdf_filename)

    # Create the PDF
    pdf = canvas.Canvas(pdf_filepath, pagesize=letter)
    width, height = letter

    # Add user information to the PDF
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, height - 50, f"User Information for {user.username}")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, height - 100, f"Name: {user.first_name} {user.last_name}")
    pdf.drawString(100, height - 120, f"Email: {user.email}")
    pdf.drawString(100, height - 140, f"Date Joined: {user.date_joined.strftime('%B %d, %Y')}")

    # Add a line break and list wardrobe items
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(100, height - 180, "Wardrobe Items:")

    y = height - 200  # Starting position for wardrobe items
    for item in wardrobe_items:
        pdf.setFont("Helvetica", 12)
        pdf.drawString(100, y, f"Item: {item.name}")
        pdf.drawString(250, y, f"Category: {item.category}")
        pdf.drawString(400, y, f"Last Worn: {item.last_worn.strftime('%B %d, %Y') if item.last_worn else 'Never'}")
        y -= 20
        if y < 50:  # If close to bottom of the page, add new page
            pdf.showPage()
            y = height - 50

    # Save the PDF file
    pdf.save()
    print(f"PDF created for {user.username} at {pdf_filepath}")

# for login 
def login_view(request):
    if request.method == 'POST':
        form = forms.LoginForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('home')  
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid form submission.')

    else:
        form = forms.LoginForm()  #

    return render(request, 'example/login.html', {'form': form})

# for register

def register_view(request):
    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            form.save() 
            return redirect('home')  
    else:
        form = forms.RegisterForm()
    
    return render(request, 'example/signup.html', {'form': form})
   

#home function

def home(request):
    return render(request,'example/index.html')

@login_required
def profile(request):
    profile = UserInfo.objects.get(user=request.user) 
    return render(request, 'example/profile.html', {'user_info': profile})

@login_required
def user_wardrobe(request):
    sort_by = request.GET.get('sort_by', 'date')
    six_months_ago = timezone.now() - timedelta(days=2)  # Default sorting by date

    # Get all clothes
    unworn_items = WardrobeItem.objects.filter(user=request.user, last_worn__lt=six_months_ago)
    
    clothes = WardrobeItem.objects.all()

    # Sort clothes based on the chosen criterion
    if sort_by == 'color':
        clothes = clothes.order_by('color')
    elif sort_by == 'category':
        clothes = clothes.order_by('category')
    else:  # Default to sorting by last worn date
        clothes = clothes.order_by('-last_worn')  # Sort descending

    # Categorize clothes here (your existing logic)
    categorized_clothes = categorize_clothes(clothes)  # Make sure to adjust this to your existing categorization function

    user_info = {
        'user': request.user,
        'typesOfClothes': "Your types here"  # Adjust this to your actual user info
    }

    return render(request, 'try_on/wardrobe.html', {
        'user_info': user_info,
        'categorized_clothes': categorized_clothes,
        'sort_by': sort_by,
        'unworn_items': unworn_items,
    })

def sell(request):
    cutoff_date = timezone.now() - timedelta(days=2)

    # Fetch clothes that have been worn before the cutoff date
    long_time_worn_clothes = WardrobeItem.objects.filter(last_worn__lt=cutoff_date)

    # Context for rendering
    context = {
        'long_time_worn_clothes': long_time_worn_clothes,
    }
    return render(request, 'example/sell.html', context)

def categorize_clothes(clothes):
    # Your existing categorization logic goes here
    categorized = {}
    # Example categorization logic
    for item in clothes:
        color = item.color  # Adjust based on your model
        category = item.category  # Adjust based on your model
        if color not in categorized:
            categorized[color] = {}
        if category not in categorized[color]:
            categorized[color][category] = []
        categorized[color][category].append(item)
    return categorized

def add_clothes(request):
     if request.method == 'POST':
        form = forms.WardrobeItemForm(request.POST, request.FILES)  # Handle file uploads
        if form.is_valid():
            wardrobe_item = form.save(commit=False)
            wardrobe_item.user = request.user  # Associate the item with the logged-in user
            wardrobe_item.save()
            return redirect('wardrobe')  # Redirect to a wardrobe page or any other page
     else:
        form = forms.WardrobeItemForm()
    
     
    
     return render(request,'try_on/add.html',{'form' : form})


@login_required
def user_quiz(request):
    profile = UserInfo.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = forms.UserInfoForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()  # Save the updated profile information
            return redirect('profile')  # Redirect to profile view after saving
    else:
        form = forms.UserInfoForm(instance=profile)  # Pre-fill form with existing data

    return render(request, 'try_on/quiz.html', {'form': form})
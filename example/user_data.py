from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.conf import settings
from django.contrib.auth.models import User
from .models import WardrobeItem
import os

def generate_user_pdf(user_id):
    # Retrieve user information
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        print("User not found")
        return

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

# Example: Generating a PDF for user with ID 1
generate_user_pdf(1)

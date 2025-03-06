from django.shortcuts import render, get_object_or_404, redirect
from .models import FinancialData
from .forms import FinancialDataForm
from .extractor import extract_financials, calculate_metrics
from .image_extractor import extract_text_from_image
from .pdf_extractor import extract_text_from_pdf
from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import os

def save_financial_data(extracted_text, extracted_data):
    """
    Save extracted financial data into the Django model, including raw text input.
    """

    tirada = extracted_data.get("tirada", 1)  # Default to 1
    qiimaha_soo_iibsiga = extracted_data.get("qiimaha_soo_iibsiga")
    qiimaha_iska_iibinta = extracted_data.get("qiimaha_iska_iibinta")
    kharashaadka = extracted_data.get("kharashaadka")
    dakhliga = extracted_data.get("dakhliga")
    faa_iido = extracted_data.get("faa'iido")
    faa_iidada_percent = extracted_data.get("faa'iidada %")
    khasaaro = extracted_data.get("khasaaro")
    khasaaro_percent = extracted_data.get("khasaaro_percent")
    dakhliga_hadda = extracted_data.get("dakhliga hadda")

    # Mark as incomplete if any key financial data is missing
    is_complete = all([qiimaha_soo_iibsiga, qiimaha_iska_iibinta, dakhliga])

    # Save or update financial data in the database
    financial_entry, created = FinancialData.objects.update_or_create(
        text_input=extracted_text,  # Save the raw extracted text
        defaults={
            "tirada": tirada,
            "qiimaha_soo_iibsiga": qiimaha_soo_iibsiga if qiimaha_soo_iibsiga is not None else 0,
            "qiimaha_iska_iibinta": qiimaha_iska_iibinta if qiimaha_iska_iibinta is not None else 0,
            "kharashaadka": kharashaadka if kharashaadka is not None else 0,
            "dakhliga": dakhliga if dakhliga is not None else 0,
            "faa_iido": faa_iido if faa_iido is not None else 0,
            "faa_iidada_percent": faa_iidada_percent if faa_iidada_percent is not None else 0,
            "khasaaro": khasaaro if khasaaro is not None else 0,
            "khasaaro_percent": khasaaro_percent if khasaaro_percent is not None else 0,
            "dakhliga_hadda": dakhliga_hadda if dakhliga_hadda is not None else 0,
            "is_complete": is_complete
        }
    )

    return financial_entry



def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return render(request, 'finance/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return render(request, 'finance/register.html')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Account created successfully. Please login.")
        return redirect('login')

    return render(request, 'finance/register.html')




def home(request):
    if request.method == "POST":
        extracted_text, error = None, None
        
        if "financial_text" in request.POST:
            financial_text = request.POST.get("financial_text", "").strip()
            if not financial_text:
                return render(request, "finance/home.html", {"error": "Please enter financial details to extract."})
            extracted_text = financial_text
        
        elif "pdf_upload" in request.FILES:
            pdf_file = request.FILES.get("pdf_upload")
            if not pdf_file:
                return render(request, "finance/home.html", {"error": "Please upload a PDF file."})
            
            file_path = default_storage.save(f"temp/{pdf_file.name}", pdf_file)
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
            try:
                extracted_text = extract_text_from_pdf(full_path)
            finally:
                default_storage.delete(file_path)
        
        elif "image_upload" in request.FILES:
            image_file = request.FILES.get("image_upload")
            if not image_file:
                return render(request, "finance/home.html", {"error": "Please upload an image file."})
            
            file_path = default_storage.save(f"temp/{image_file.name}", image_file)
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
            try:
                extracted_text = extract_text_from_image(full_path)
            finally:
                default_storage.delete(file_path)
        
        if extracted_text:
            return result(request, extracted_text)
    
    return render(request, "finance/home.html")


@login_required(login_url='login') 
def result(request, extracted_text):
    financials = extract_financials(extracted_text)
    metrics = calculate_metrics(financials)
    
    if not any(financials.values()) or all(value == 1 or value is None for value in financials.values()):
        return render(request, "finance/home.html", {"error": "This is not financial data. Please enter financial details."})
    
    saved_financial = save_financial_data(extracted_text, metrics)
    
    return render(request, "finance/results.html", {
        "metrics": metrics,
        "saved_financial_id": saved_financial.id
    })



# About view
def about(request):
    return render(request, 'finance/about.html')  # Ensure this template exists


# Contact view
def contact(request):
    return render(request, 'finance/contact.html')




def incomplete_financial_data(request):
    """
    Show a list of incomplete financial data entries.
    """
    incomplete_data = FinancialData.objects.filter(is_complete=False)
    return render(request, "finance/incomplete_financial_data.html", {"incomplete_data": incomplete_data})


def edit_financial_data(request, pk):
    """
    Allow users to edit and update financial data with re-extraction and recalculation.
    """
    data = get_object_or_404(FinancialData, pk=pk)

    if request.method == "POST":
        form = FinancialDataForm(request.POST, instance=data)
        
        if form.is_valid():
            financial_data = form.save(commit=False)  # Don't save immediately
            
            # Extract updated financial data
            extracted_financials = extract_financials(financial_data.text_input)
            calculated_metrics = calculate_metrics(extracted_financials)

            # Update relevant fields with new extracted values
            financial_data.tirada = calculated_metrics.get("tirada", 1)
            financial_data.qiimaha_soo_iibsiga = calculated_metrics.get("qiimaha_soo_iibsiga", 0)
            financial_data.qiimaha_iska_iibinta = calculated_metrics.get("qiimaha_iska_iibinta", 0)
            financial_data.kharashaadka = calculated_metrics.get("kharashaadka", 0)
            financial_data.dakhliga = calculated_metrics.get("dakhliga", 0)
            financial_data.faa_iido = calculated_metrics.get("faa'iido", 0)
            financial_data.faa_iidada_percent = calculated_metrics.get("faa'iidada %", 0)
            financial_data.khasaaro = calculated_metrics.get("khasaaro", 0)
            financial_data.khasaaro_percent = calculated_metrics.get("khasaaro_percent", 0)
            financial_data.dakhliga_hadda = calculated_metrics.get("dakhliga hadda", 0)

            # Determine completeness based on required fields
            financial_data.is_complete = all([
                financial_data.qiimaha_soo_iibsiga, 
                financial_data.qiimaha_iska_iibinta, 
                financial_data.dakhliga
            ])

            financial_data.save()  # Save after updating fields

            messages.success(request, "Financial data updated successfully.")
            return redirect("financial_data_list")

    else:
        form = FinancialDataForm(instance=data)

    return render(request, "finance/edit_financial_data.html", {"form": form})




def delete_financial_data(request, pk):
    """
    Delete a financial data entry.
    """
    data = get_object_or_404(FinancialData, pk=pk)
    data.delete()
    messages.success(request, "Financial data deleted successfully.")
    return redirect("financial_data_list")  # Redirect back to the list page


def financial_data_list(request):
    financial_data = FinancialData.objects.all()
    return render(request, "finance/financial_data_list.html", {"financial_data": financial_data})

from django.shortcuts import render
from .models import FinancialData

def dashboard(request):
    """
    Display the main dashboard with financial summaries.
    """
    financial_data = FinancialData.objects.all()

    # Calculate totals
    total_income = sum(data.dakhliga for data in financial_data)
    total_expense = sum(data.kharashaadka for data in financial_data)
    total_profit = total_income - total_expense

    # Fetch recent financial data
    recent_financial_data = financial_data.order_by('-id')[:5]  # Show last 5 entries

    return render(request, 'finance/dashboard.html', {
        'total_income': total_income,
        'total_expense': total_expense,
        'total_profit': total_profit,
        'recent_financial_data': recent_financial_data
    })

from django.shortcuts import render, get_object_or_404, redirect
from .models import FinancialData
from .forms import FinancialDataForm
from .extractor import extract_financials, calculate_metrics
from .image_extractor import extract_text_from_image
from .pdf_extractor import extract_text_from_pdf
from django.core.files.storage import default_storage
from django.conf import settings
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
    khasaaro_percent = extracted_data.get("khasaaro %")
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


def home(request):
    if request.method == "POST":
        extracted_text = None

        # Handle Text Input
        if "financial_text" in request.POST:
            financial_text = request.POST.get("financial_text", "").strip()
            if not financial_text:
                return render(request, "finance/home.html", {"error": "Please enter financial details to extract."})
            extracted_text = financial_text

        # Handle PDF Upload
        elif "pdf_upload" in request.FILES:
            pdf_file = request.FILES["pdf_upload"]
            if not pdf_file:
                return render(request, "finance/home.html", {"error": "Please upload a PDF file."})

            file_path = default_storage.save(f"temp/{pdf_file.name}", pdf_file)
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)

            try:
                extracted_text = extract_text_from_pdf(full_path)
            finally:
                default_storage.delete(file_path)

        # Handle Image Upload
        elif "image_upload" in request.FILES:
            image_file = request.FILES["image_upload"]
            if not image_file:
                return render(request, "finance/home.html", {"error": "Please upload an image file."})

            file_path = default_storage.save(f"temp/{image_file.name}", image_file)
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)

            try:
                extracted_text = extract_text_from_image(full_path)
            finally:
                default_storage.delete(file_path)

        if extracted_text:
            # Extract financials & calculate metrics
            financials = extract_financials(extracted_text)
            metrics = calculate_metrics(financials)

            # 🔥 Check if extracted financial data is empty or contains no financial values
            if not any(financials.values()) or all(value == 1 or value is None for value in financials.values()):
                return render(request, "finance/home.html", {"error": "This is not financial data. Please enter financial details."})

            # Save extracted text and financial data in database
            saved_financial = save_financial_data(extracted_text, financials)

            return render(request, "finance/results.html", {
                "financials": financials,
                "metrics": metrics,
                "saved_financial_id": saved_financial.id  # Pass saved record ID for editing
            })

    return render(request, "finance/home.html")


def incomplete_financial_data(request):
    """
    Show a list of incomplete financial data entries.
    """
    incomplete_data = FinancialData.objects.filter(is_complete=False)
    return render(request, "finance/incomplete_financial_data.html", {"incomplete_data": incomplete_data})


def edit_financial_data(request, pk):
    """
    Allow users to edit and update financial data.
    """
    data = get_object_or_404(FinancialData, pk=pk)
    if request.method == "POST":
        form = FinancialDataForm(request.POST, instance=data)
        if form.is_valid():
            form.save()
            return redirect("financial_data_list")
    else:
        form = FinancialDataForm(instance=data)
    return render(request, "finance/edit_financial_data.html", {"form": form})


def financial_data_list(request):
    financial_data = FinancialData.objects.all()
    return render(request, "finance/financial_data_list.html", {"financial_data": financial_data})

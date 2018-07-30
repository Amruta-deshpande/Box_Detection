from django.core.files.storage import FileSystemStorage
from django.shortcuts import render

from uploads.challenge.edge_detection import process_image


def home(request):
    if request.method == 'POST' and request.FILES['inputFile']:
        myfile = request.FILES['inputFile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        output_filename = filename.replace("input", "output")
        process_image(fs.path(filename))
        return render(request, 'challenge/home.html', {
            'output_file_url': fs.url(output_filename)
        })
    return render(request, 'challenge/home.html')

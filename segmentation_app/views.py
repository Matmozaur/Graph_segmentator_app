from PIL import Image
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render

from segmentator import main_api as seg


# Create your views here.
from django.views.decorators.csrf import ensure_csrf_cookie

from segmentator.mst_algorithms import threshold_mst_1, threshold_mst_2, threshold_mst_3

context = {}


def home(request):
    context.clear()
    return render(request, 'home.html')


def segmentation(request):
    if request.method == 'POST':
        context.clear()
        #context={}
        uploaded_file = request.FILES['image']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        context['image'] = fs.url(name)
    return render(request, 'segmentation.html', context)


def tracking(request):
    return render(request, 'home.html')



def mst(request):
    print(context)
    if request.method == 'POST':
        edges8=request.POST.get("Edges")
        const=float(request.POST.get("Const"))
        min_size=int(request.POST.get("Min_size"))
        threshold=int(request.POST.get("Threshold"))
        if threshold==1:
            result= seg.mst_1const(Image.open(context['image']), edges_8=edges8,
                                            threshold=threshold_mst_1,
                                            const=const,min_size=min_size)
        elif threshold==2:
            result= seg.mst_1const(Image.open(context['image']), edges_8=edges8,
                                            threshold=threshold_mst_2,
                                            const=const,min_size=min_size)
        elif threshold==3:
            result= seg.mst_1const(Image.open(context['image']), edges_8=edges8,
                                            threshold=threshold_mst_3,
                                            const=const,min_size=min_size)
        else:
            print("Problem");
        result[0].save('static/media/temporary.png')
        context['segmented_image'] = "/static/media/temporary.png"
        context['counter'] = result[1]
    return render(request, 'mst.html', context)


def two_cc(request):
    print(context)
    if request.method == 'POST':
        channel=int(request.POST.get("Channel"))
        const=float(request.POST.get("Const"))
        threshold=int(request.POST.get("Threshold"))
        fill_in=int(request.POST.get("Fill_in"))
        if threshold==1:
            const=None
        if channel==1:
            result = seg.two_connected_components(Image.open(context['image']), fill_in=fill_in, thresh=const)
        elif channel==2:
            result= seg.two_connected_components(Image.open(context['image']),channel="red",  fill_in=fill_in, thresh=const)
        elif channel==3:
            result= seg.two_connected_components(Image.open(context['image']),channel="green",  fill_in=fill_in, thresh=const)
        elif channel==4:
            result= seg.two_connected_components(Image.open(context['image']),channel="blue",  fill_in=fill_in, thresh=const)
        else:
            print("Problem");
        result[0].save('static/media/temporary.png')
        context['segmented_image'] = "/static/media/temporary.png"
        context['counter'] = result[1]
    return render(request, 'two_cc.html', context)


@ensure_csrf_cookie
def choose_alg(request):
    if request.method == 'POST':
        name = request.POST.get("algos")
        if(name == "mst"):
            return render(request, 'mst.html', context)
        if(name == "two_cc"):
            return render(request, 'two_cc.html', context)
        else:
            return HttpResponseForbidden('Something is wrong, check if you filled all required positions!2')

    return HttpResponseForbidden('Something is wrong, check if you filled all required positions!1')





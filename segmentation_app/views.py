from PIL import Image
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render

from segmentator import main_api as seg
from segmentation_app import connector


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
        uploaded_file = request.FILES.get('image')
        fs = FileSystemStorage()
        if(uploaded_file is None):
            return render(request, 'segmentation.html', context)
        # name=uploaded_file.name
        # uploaded_file=Image.open(uploaded_file)
        # if (uploaded_file.width>=500) | (uploaded_file.height>=500):
        #     uploaded_file = uploaded_file.resize((500, 500))
        print(type(uploaded_file))
        name = fs.save(uploaded_file.name, uploaded_file)
        context['image'] = fs.url(name)
        # context['image']=Image.open(context['image'])
        # if (context['image'].width>=500) | (context['image'].height>=500):
        #     context['image'] = context['image'].resize((500, 500))
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
        context['forest'] = result[2]
        context['graph'] = result[3]

        context['edges8'] = edges8
        context['const'] = const
        context['min_size'] = min_size
        context['threshold'] = threshold
    return render(request, 'mst.html', context)


def mst_additional(request):
    print(context)
    if request.method == 'POST':

        const=float(request.POST.get("Const"))
        print(const)

        min_size=int(request.POST.get("Min_size"))
        threshold=int(request.POST.get("Threshold"))
        max_size=int(request.POST.get("Max_size"))
        forest=context['forest']
        G=context['graph']
        if threshold==1:
            result= seg.mst_1const_additional(G, forest,
                                            threshold=threshold_mst_1,
                                            const=const,min_size=min_size,max_size=max_size)
        elif threshold==2:
            result= seg.mst_1const_additional(G, forest,
                                            threshold=threshold_mst_2,
                                            const=const,min_size=min_size,max_size=max_size)
        elif threshold==3:
            result= seg.mst_1const_additional(G, forest,
                                            threshold=threshold_mst_3,
                                            const=const,min_size=min_size,max_size=max_size)
        else:
            print("Problem");
        result[0].save('static/media/temporary.png')
        context['segmented_image'] = "/static/media/temporary.png"
        context['counter'] = result[1]

        context['const2'] = const
        context['min_size2'] = min_size
        context['max_size2'] = max_size
        context['threshold2'] = threshold
    return render(request, 'mst.html', context)


def save_mst(request):
    img_base=context['image']
    img_segmented=context['segmented_image']
    name=request.POST.get("Name")
    description=request.POST.get("Description")
    counter=context['counter']

    edges=context['edges8']
    threshold=context['threshold']
    const=context['const']
    min_size=context['min_size']
    if('threshold2' in context.keys()):
        threshold2=context['threshold2']
        const2=context['const2']
        min_size2=context['min_size2']
        max_size2=context['max_size2']
    else:
        threshold2=None
        const2=None
        min_size2=None
        max_size2=None

    connector.save_mst(img_base,img_segmented,name,description,edges,threshold,const,min_size,threshold2,
             const2,min_size2,max_size2,counter)
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
            result = seg.two_connected_components(Image.open(context['image']),channel="all", fill_in=fill_in, thresh=const)
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

        context['channel'] = channel
        context['const'] = const
        context['threshold'] = threshold
        context['fill_in'] = fill_in
    return render(request, 'two_cc.html', context)


def save_two_cc(request):
    img_base=context['image']
    img_segmented=context['segmented_image']
    name=request.POST.get("Name")
    description=request.POST.get("Description")
    counter=context['counter']

    channel=context['channel']
    threshold=context['threshold']
    filling=context['fill_in']
    const=context['const']

    connector.save_two_cc(img_base,img_segmented,name,description,channel,threshold,filling,const,counter)

    return render(request, 'two_cc.html', context)


def ngc(request):
    print(context)
    if request.method == 'POST':
        Decision=int(request.POST.get("Algorithm_type"))
        I=int(request.POST.get("Intensivity"))
        X=int(request.POST.get("Distance"))
        if Decision == 1:
            result = seg.basic_ngc(context['image'], I, X)
        elif Decision == 2:
            result = seg.advanced_ngc(context['image'], I, X)
        else:
            print("Problem");
        result[0].save('static/media/temporary.png')
        context['segmented_image'] = "/static/media/temporary.png"
        context['counter'] = result[1]

        context['Decision'] = Decision
        context['I'] = I
        context['X'] = X
    return render(request, 'ngc.html', context)


def save_ngc(request):
    img_base=context['image']
    img_segmented=context['segmented_image']
    name=request.POST.get("Name")
    description=request.POST.get("Description")
    counter=context['counter']

    type=context['Decision']
    sensivity=context['I']
    sensivity_location=context['X']

    connector.save_ngc(img_base,img_segmented,name,description,type,sensivity,sensivity_location,counter)
    return render(request, 'ngc.html', context)


def interactive(request):
    print(context)
    if request.method == 'POST':
        result = seg.interactive(Image.open(context['image']))
        result[0].save('static/media/temporary.png')
        context['segmented_image'] = "/static/media/temporary.png"
        context['counter'] = result[1]
    return render(request, 'interactive.html', context)


def save_interactive(request):
    img_base=context['image']
    img_segmented=context['segmented_image']
    name=request.POST.get("Name")
    description=request.POST.get("Description")
    counter=context['counter']

    connector.save_interactive(img_base,img_segmented,name,description,counter)
    return render(request, 'interactive.html', context)


@ensure_csrf_cookie
def choose_alg(request):
    if request.method == 'POST':
        name = request.POST.get("algos")
        if name == "mst":
            return render(request, 'mst.html', context)
        elif name == "two_cc":
            return render(request, 'two_cc.html', context)
        elif name == "ngc":
            return render(request, 'ngc.html', context)
        if name == "interactive":
            return render(request, 'interactive.html', context)
        else:
            return HttpResponseForbidden('Something is wrong, check if you filled all required positions!2')

    return HttpResponseForbidden('Something is wrong, check if you filled all required positions!1')


def algorithms_desc(request):
    return render(request, 'algorithms_desc.html')


def mst_desc(request):
    return render(request, 'mst_desc.html')


def ngc_desc(request):
    return render(request, 'ngc_desc.html')


def two_cc_desc(request):
    return render(request, 'two_cc_desc.html')


def interactive_desc(request):
    return render(request, 'interactive_desc.html')



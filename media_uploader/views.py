from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

from media_uploader.forms import StaticMediaForm

@staff_member_required
def upload_static_media(request):
    if request.method == 'POST':
        form = StaticMediaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Successfully uploaded!')
        else:
            messages.warning(request, f'Failed to upload.')
        return redirect('/media-uploader')
    else:
        form = StaticMediaForm()
    params = {
        'form': form,
    }
    return render(request, 'media_uploader/index.html', params)
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from .models import Team
from .forms import SignupForm, TeamForm



class SignupView(CreateView):
    """ form_validがない場合は、ユーザー登録後は、ログイン画面にリダイレクトさせ、ユーザーに手動でログインさせることになる """
    template_name = 'accounts/signup.html'
    form_class = SignupForm
    success_url = '/'

    def form_valid(self, form):
        """ ユーザー登録後に自動でログインさせる """

        # self.objectにsave()されたUserオブジェクトが入る
        valid = super().form_valid(form)
        self.object.backend = 'django.contrib.auth.backends.ModelBackend'
        login(self.request, self.object)
        return valid

# Team新規作成のエンドポイント
@login_required
def createteam(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.owner = request.user
            team.save()
            print('successfully created a new team.')
    return redirect('/accounts/team')
    
    
# 所属Team一覧ページのView
@login_required
def team(request):
    login_user = request.user
    params = {
        'login_user': login_user,
        'items': Team.objects.filter(Q(owner=login_user)|Q(members=login_user)).distinct(),
        'form': TeamForm()
    }
    return render(request, 'accounts/team.html', params)
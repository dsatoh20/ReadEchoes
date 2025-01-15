from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from .models import InviteTeam, Team, User
from .forms import SignupForm, TeamForm, SearchUserForm



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
            messages.success(request, 'Successfully created a new team!')
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

# Userを検索するView
@login_required
def searchuser(request, team_id):
    login_user = request.user
    team = Team.objects.get(id=team_id)
    members = team.members.all()
    if login_user not in members and login_user != team.owner: # memberでない場合、閲覧できない
        messages.warning(request, 'No permission to access.')
        redirect('/team')
    belonged_teams = None # 検索したuserが所属するチーム
    hit = None
    hit_id = 0
    if request.method == 'POST':
        form = SearchUserForm(request.POST)
        if form.is_valid():            
            form_input = form.cleaned_data['search']
            hit = User.objects.filter(username=form_input).first()
            if hit:
                belonged_teams = hit.team_members.all()
                hit_id = hit.id
    else:
        form = SearchUserForm()

    params = {
        'login_user': login_user,
        'team': team,
        'belonged_teams': belonged_teams,
        'items': members,
        'hit': hit,
        'hit_id': hit_id,
        'form': form,
    }
    return render(request, 'accounts/searchuser.html', params)

# ヒットしたUserをグループに追加
@login_required
def adduser(request, team_id, user_id):
    print('adduserにいきました！！')
    team = Team.objects.get(id=team_id) # 追加対象のTeam
    user = User.objects.get(id=user_id) # 追加対象のUser
    if request.user != team.owner: # owner出ない場合、操作できない
        messages.warning(request, 'You have no permission for this request.')
        redirect(f'/accounts/searchuser/{team_id}')
    invite_team = InviteTeam.objects.filter(team=team).filter(owner=user).first()
    if invite_team:
        team.members.remove(user)
        invite_team.delete()
        messages.warning(request, f'Removed {user.username} from {team.title}')
    else:
        team.members.add(user)
        invite_team = InviteTeam()
        invite_team.owner = user
        invite_team.team = team
        invite_team.save()
        messages.success(request, f'{user.username} joined {team.title}')
    return redirect(f'/accounts/searchuser/{team_id}')

def contact(request):
    login_user = request.user
    params = {
        'login_user': login_user,
    }
    return render(request, 'contact.html', params)
def about(request):
    login_user = request.user
    params = {
        'login_user': login_user,
    }
    return render(request, 'about.html', params)
def terms(request):
    login_user = request.user
    params = {
        'login_user': login_user,
    }
    return render(request, 'terms.html', params)
def policy(request):
    login_user = request.user
    params = {
        'login_user': login_user,
    }
    return render(request, 'policy.html', params)

@login_required
def profile(request):
    login_user = request.user
    params = {
        'login_user': login_user,
    }
    return render(request, 'accounts/profile.html', params)
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from media_uploader.models import StaticMedia
from records.forms import BookForm, BookUpdateForm, CommentForm, TeamSelectForm, MediumSelectForm
from .models import Book, Like, Comment
from accounts.models import User, Team


# Create your views here.
def index(request):
    login_user = request.user
    public_team = Team.objects.filter(public=True)
    items = get_available_items(login_user) if login_user.username != '' else Book.objects.filter(team__in=public_team).distinct()
    if str(items) == str(Book.objects.none()):
            public_teams = Team.objects.filter(public=True).distinct()
            items = Book.objects.filter(team__in=public_teams).distinct()
            messages.info(request, 'No items. Public items are displayed.')
    if request.method == 'POST':
        form = TeamSelectForm(login_user, request.POST)
        if form.is_valid():
            selected = form.cleaned_data['team']
            print(selected)
            if selected == 'Public':
                public_teams = Team.objects.filter(public=True).distinct()
                items = Book.objects.filter(team__in=public_teams).distinct()
            elif selected != 'All':
                items = Book.objects.filter(team=Team.objects.get(id=selected))
        else:
            print(form.errors)
        
            
    else:
        form = TeamSelectForm(user=login_user)
    params = {
        'login_user' : login_user,
        'items': items,
        'liked_items': get_liked_items(login_user),
        'form': TeamSelectForm(login_user),
    }
    return render(request, 'index.html', params)

@login_required
def post(request):
    login_user = request.user
    if login_user.team_members.all() or login_user.team_owner.all():
        pass
    else:
        messages.warning(request, 'Create or join a team first.')
        return redirect('/accounts/team')
    if request.method == 'POST':
        form = BookForm(request.POST, login_user)
        if form.is_valid():
            book = form.save(commit=False)
            info_medium = book.info_medium
            if info_medium == 1: # 1:Book
                try:
                    book.auto_fill()
                    print('successfully complemented!')
                except Exception as e:
                    print(f'failed to auto_fill...Err: {e}')
                    messages.warning(request, 'Failed to get book information...please edit it manually.')
            elif info_medium == 2: # 2:Movie
                try:
                    book.auto_fill_mov()
                    print('successfully complemented!')
                except Exception as e:
                    print(f'failed to auto_fill...Err: {e}')
                    messages.warning(request, 'Failed to get movie information...please edit it manually.')
            elif info_medium == 3: # 3:Music
                pass
            elif info_medium == 4: # 4:Thesis
                pass
            else: # 0:Others
                pass
            
            print(f'img_pathは{book.img_path}')
            if book.img_path == '' or book.img_path == None: # img_pathが空欄なら、ロゴを埋めておく
                logo120 = StaticMedia.objects.filter(name='logo120').first()
                book.img_path = logo120.image.url if logo120 else ''
                messages.debug(request, 'set logo as image_path.')
            book.owner = login_user
            book.save()    
            messages.success(request, 'Successfully posted a new record!')
            return redirect('/')
        else:
            print(form.errors)
    else:
        form = BookForm(user=login_user)
    params = {
        'login_user': login_user,
        'form': form,
    }
    return render(request, 'records/post.html', params)

@login_required
def like(request, book_id):
    # likeボタン押下で作動
    login_user = request.user
    book = Book.objects.get(id=book_id)
    like = Like.objects.filter(owner=login_user).filter(book=book).first()
    if like:
        like.delete() # likeオブジェクトを削除
        book.good_count -= 1 # イイネ数を-1
        messages.debug(request, f'Removed like to {book}.')
    else:
        like = Like() # 新たにlikeオブジェクトを登録
        like.owner = login_user
        like.book = book
        like.save()
        book.good_count += 1 # イイネ数を+1
        messages.debug(request, f'Liked {book}.')
    book.save()
    referer_url = request.META.get('HTTP_REFERER', '/')
    if 'accounts/login' in referer_url: # 未ログイン状態でいいねした場合
        print('redirect to home...')
        return redirect('/')
    else:
        return HttpResponseRedirect(referer_url)

def record(request, book_id):
    login_user = request.user
    record = Book.objects.get(id=book_id)
    if login_user in record.team.members.all() or login_user == record.team.owner:
        # クライアントがチームメンバーなら、Okay.
        pass
    else:
        if record.team.public == True:
            # 投稿先チームがpublicなら、Okay.
            pass
        else:
            # それ以外はアクセス許可なし
            messages.warning(request, 'No permission to access this record.')
            return redirect('/')
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.owner = login_user
            comment.book = record
            comment.save()
            messages.success(request, 'Successfully commented.')
            return redirect(f'/record/{book_id}')
        else:
            messages.debug(form.errors)
            print(form.errors)
    else:
        form = CommentForm()
    params = {
        'login_user': login_user,
        'item': record,
        'liked_items': get_liked_items(login_user),
        'form': form,
        'comments': Comment.objects.filter(book=record).filter(reply_id=-1).distinct(),
    }
    return render(request, 'records/record.html', params)

@login_required
def portfolio(request):
    login_user = request.user
    items = Book.objects.filter(owner=login_user) if login_user.username != '' else Book.objects.none()
    if request.method=='POST':
        form = MediumSelectForm(request.POST)
        if form.is_valid():
            selected = form.cleaned_data['info_medium']
            if selected != 'All':
                items = Book.objects.filter(owner=login_user).filter(info_medium=selected)
        else:
            print(form.errors)
    else:
        form = MediumSelectForm()
    params = {
        'login_user': login_user,
        'items': items,
        'liked_items': get_liked_items(login_user),
        'form': form,
    }
    return render(request, 'records/portfolio.html', params)

@login_required
def reply(request, book_id, comment_id):
    login_user = request.user
    record = Book.objects.get(id=book_id)
    if login_user in record.team.members.all() or login_user == record.team.owner:
        # クライアントがチームメンバーなら、Okay.
        pass
    else:
        messages.warning(request, 'No permission to access.')
        return redirect(f'/records/{book_id}')
    comment = Comment.objects.get(id=comment_id)
    replies = Comment.objects.filter(reply_id=comment_id).distinct()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.owner = login_user
            reply.book = record
            reply.reply_id = comment_id # 返信先コメントと紐づけ
            reply.save()
            messages.success(request, 'Successfully replied.')
            return redirect(f'/record/{book_id}/reply/{comment_id}')
        else:
            messages.debug(request, form.errors)
            print(form.errors)
    else:
        form = CommentForm()
    params = {
        'login_user': login_user,
        'item': record,
        'comment': comment,
        'replies': replies,
        'form': form,
    }
    return render(request, 'records/reply.html', params)

@login_required
def edit(request, book_id):
    login_user = request.user
    record = Book.objects.get(id=book_id)
    if record.owner != login_user:
        # ownerだけが編集できる
        messages.warning(request, 'No permission to edit this record.')
        return redirect(f'/record/{book_id}')
    if request.method == 'POST':
        form = BookUpdateForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated!')
            return redirect(f'/record/{book_id}')
        else:
            print(form.errors)
    else:
        form = BookUpdateForm(instance=record)
    params = {
        'login_user': login_user,
        'item': record,
        'form': form,
    }
    return render(request, 'records/edit.html', params)

"""
ただの関数below
"""
def get_available_items(user):
    if user.username != '':
        available_teams = Team.objects.filter(members=user).distinct()
        available_items = Book.objects.filter(Q(owner=user)|Q(team__in=available_teams)).distinct()
    else:
        available_items = Book.objects.none()
    return available_items

def get_liked_items(user):
    if user.username != '':
        likes = user.like_owner.all()
        liked_items = Book.objects.filter(like_book__in=likes).distinct()
    else:
        liked_items = Book.objects.none()
    return liked_items
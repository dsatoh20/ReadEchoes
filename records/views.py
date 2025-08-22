import os
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import send_mail

from media_uploader.models import StaticMedia
from records.forms import BookForm, BookUpdateForm, CommentForm, TeamSelectForm, MediumSelectForm
from .models import Book, Like, Comment
from accounts.models import User, Team

page_contents_num = int(os.getenv('PAGE_CONTENTS_NUM', 2))
CANONICAL_HOSTNAME = os.getenv('CANONICAL_HOSTNAME', 'localhost:8000')


# Create your views here.
def index(request):
    login_user = request.user
    public_team = Team.objects.filter(public=True)
    items = get_available_items(login_user) if login_user.username != '' else Book.objects.filter(team__in=public_team).distinct()
    
    selected_team = request.GET.get('team', None) # team idが格納される

    if str(items) == str(Book.objects.none()) or selected_team == '-' or selected_team == None:
            public_teams = Team.objects.filter(public=True).distinct()
            items = Book.objects.filter(team__in=public_teams).distinct()
            messages.info(request, 'No items. Public items are displayed.')
    else:

        if selected_team == 'Public':
            public_teams = Team.objects.filter(public=True).distinct()
            items = Book.objects.filter(team__in=public_teams).distinct()
        elif selected_team != 'All':
            items = Book.objects.filter(team_id=selected_team)

    form = TeamSelectForm(user=login_user, initial=request.GET)

    # pagination
    paginator = Paginator(items.order_by('-id'), page_contents_num)
    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)

    params = {
        'login_user' : login_user,
        'page_obj': page_obj,
        'liked_items': get_liked_items(login_user),
        'form': form,
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
            try:
                # メール送信
                send_mail(
                    f"<ReadEchoes>{book.owner.username} is waiting for your feedback!",
                    f"A new record has been posted by {book.owner.username} ({book.team.title}).\n\n\
                    Record owner: {book.owner.username}\n\
                    Record: {book.first_author}. {book.title}. {book.pub_year}.\n\
                    Click the link below to leave a comment: \n\n\
                    https://{CANONICAL_HOSTNAME}/record/{book.id}",
                    "support@readechoes.com",
                    [book.team.owner.email] + [member.email for member in book.team.members.all()],
                    fail_silently=False,
                )
            except Exception as e:
                print(f'Failed to send email...Err: {e}')
                # messages.warning(request, 'Failed to send email notification.')
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
            try:
                # メール送信
                send_mail(
                    f"<ReadEchoes>{comment.owner.username} left a comment!",
                    f"A new comment has been posted by {comment.owner.username} ({record.team.title}).\n\n\
                    Record owner: {record.owner.username}\n\
                    Record: {record.first_author}. {record.title}. {record.pub_year}.\n\
                    Comment owner: {comment.owner.username}\n\
                    Comment: {comment.content}\n\n\
                    Click the link below to join the discussion: \n\
                    https://{CANONICAL_HOSTNAME}/record/{record.id}",
                    "support@readechoes.com",
                    [record.team.owner.email] + [member.email for member in record.team.members.all()],
                    fail_silently=False,
                )
            except Exception as e:
                print(f'Failed to send email...Err: {e}')
                # messages.warning(request, 'Failed to send email notification.')
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

    selected_media = request.GET.get('info_medium', 'All')

    if selected_media != 'All':
            items = Book.objects.filter(owner=login_user).filter(info_medium=selected_media)

    # pagination
    paginator = Paginator(items.order_by('-id'), page_contents_num)
    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)

    form = MediumSelectForm(initial=request.GET)

    params = {
        'login_user': login_user,
        'page_obj': page_obj,
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
            try:
                # メール送信
                send_mail(
                    f"<ReadEchoes>{reply.owner.username} left a comment!",
                    f"A new comment has been posted by {reply.owner.username} in {record.team.title}.\n\n\
                    Record owner: {record.owner.username}\n\
                    Record: {record.first_author}. {record.title}. {record.pub_year}.\n\
                    Comment owner: {reply.owner.username}\n\
                    Comment: {reply.content}\n\n\
                    Click the link below to join the discussion: \n\
                    https://{CANONICAL_HOSTNAME}/record/{record.id}",
                    "support@readechoes.com",
                    [record.team.owner.email] + [member.email for member in record.team.members.all()],
                    fail_silently=False,
                )
            except Exception as e:
                print(f'Failed to send email...Err: {e}')
                # messages.warning(request, 'Failed to send email notification.')
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

@login_required
def delete(request, book_id):
    login_user = request.user
    record = Book.objects.get(id=book_id)
    if record.owner != login_user:
        # ownerだけが削除できる
        messages.warning(request, 'No permission to delete this record.')
        return redirect(f'/record/{book_id}')
    else:
        record.delete()
        messages.success(request, 'Successfully deleted!')
        return redirect('/portfolio')
    

"""
ただの関数below
"""
def get_available_items(user):
    if user.username != '':
        available_teams = Team.objects.filter(Q(members=user)|Q(owner=user)).distinct()
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
from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect , get_list_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.models import User
from django.contrib import auth
from django.core.paginator import Paginator
from .forms import PostForm,CommentForm
from .models import Post,Category,Comment
from django.template.defaultfilters import slugify
import datetime
try:
    from django.utils import simplejson as json
except ImportError:
    import json
# Create your views here.

def index(request):
    return render(request,'index.html')

def posts_home(request):
    category_list = Category.objects.all()
    return render(request,"posts_categories.html",{'categories':category_list,'user':request.user})

def posts_list(request,name,slug):
    categories = Category.objects.all()
    if name == 'open':
        open_category = get_object_or_404(Category,slug=slug)
        for x in categories:
            if x.name=='pro' and x.parent == open_category.parent:
                pro_category = get_object_or_404(Category,slug=x.slug)
        posts_list = Post.objects.filter(category=open_category)
        paginator = Paginator(posts_list,10)
        page = request.GET.get('page')
        posts = paginator.get_page(page)
    if name == 'pro':
        pro_category = get_object_or_404(Category,slug=slug)
        for x in categories:
            if x.name =='open' and x.parent == pro_category.parent:
                open_category = get_object_or_404(Category,slug=x.slug)
        posts_list = Post.objects.filter(category=pro_category)
        paginator = Paginator(posts_list,10)
        page = request.GET.get('page')
        posts = paginator.get_page(page)
    return render(request,'posts_list.html',{'posts':posts,'opencategory':open_category,'procategory':pro_category,'categories':categories})

def posts_search(request):
    #모든 카테고리 가져오기
    categories = Category.objects.all()
    # 검색할 분야 찾기
    slug = request.GET['categoryslug']
    category = get_object_or_404(Category,slug=slug)

    #openboard 검색
    if category.name == 'open':
        open_category = get_object_or_404(Category,slug=slug)
        for x in categories:
            if x.name=='pro' and x.parent == open_category.parent:
                pro_category = get_object_or_404(Category,slug=x.slug)
        # 검색 쿼리셋 가져오기
        qs = Post.objects.filter(category=open_category)
        ps=''
        rs=''
        q = request.GET.get('q','')
        

        if q: # q가 있으면
            ps = qs.filter(title__icontains=q) # 제목에 q가 포함되어 있는 레코드만 필터링
            rs = qs.filter(body__icontains=q) # 내용에 q가 포함되어 있는 레코드만 필터링 
            qs = ps | rs  # 쿼리셋 합치기 
        paginator = Paginator(qs,10)
        page = request.GET.get('page')
        posts = paginator.get_page(page)
    
    #professional board 검색
    if category.name == 'pro':
        pro_category = get_object_or_404(Category,slug=slug)
        for x in categories:
            if x.name =='open' and x.parent == pro_category.parent:
                open_category = get_object_or_404(Category,slug=x.slug)
        # 검색 쿼리셋 가져오기
        qs = Post.objects.filter(category=pro_category)
        ps=''
        rs=''
        q = request.GET.get('q','')

        if q: # q가 있으면
            ps = qs.filter(title__icontains=q) # 제목에 q가 포함되어 있는 레코드만 필터링
            rs = qs.filter(body__icontains=q) # 내용에 q가 포함되어 있는 레코드만 필터링 
            qs = ps | rs  # 쿼리셋 합치기 

        paginator = Paginator(qs,10)
        page = request.GET.get('page')
        posts = paginator.get_page(page)
    return render(request,'posts_list.html',{'posts':posts,'opencategory':open_category,'procategory':pro_category,'categories':categories})

def posts_new(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = PostForm(request.POST,request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.ip = request.META['REMOTE_ADDR']
            post.creator = request.user
            post.save()
            return redirect('/posts/'+str(post.id), {'categories':categories})
    else:
        form = PostForm()
    return render(request,'posts_new.html',{'form':form, 'categories':categories})

def posts_edit(request,post_id):
    categories = Category.objects.all()
    post = get_object_or_404(Post,pk=post_id)
    if request.method =='POST':
        form = PostForm(request.POST,request.FILES,instance=post)
        if form.is_valid():
            post = form.save()
            return redirect('/posts/'+str(post.id))
    else:
        form = PostForm(instance=post)
    return render(request,'posts_new.html',{'form':form, 'categories':categories})

def posts_detail(request,post_id):
    categories = Category.objects.all()
    post_detail = get_object_or_404(Post,pk=post_id)
    request_user = request.user
    return render(request,'posts_detail.html',{'post':post_detail,'user':request_user, 'categories':categories})

@login_required
@require_POST
def posts_like(request):
    if request.method == 'POST':
        user = request.user # 로그인한 유저를 가져온다.
        post_id = request.POST.get('pk', None)
        post = Post.objects.get(pk = post_id) #해당 메모 오브젝트를 가져온다.

        if post.likes.filter(id = user.id).exists(): #이미 해당 유저가 likes컬럼에 존재하면
            post.likes.remove(user) #likes 컬럼에서 해당 유저를 지운다.
            message = '좋아요를 취소했습니다.'
        else:
            post.likes.add(user)
            message = '좋아요를 추가했습니다.'

    context = {'likes_count' : post.total_likes, 'message' : message}
    return HttpResponse(json.dumps(context), content_type='application/json')

def posts_add_comment(request, post_id):
    categories = Category.objects.all()
    post = get_object_or_404(Post, pk=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.creator = request.user
            comment.save()
            return redirect('/posts/'+str(post.id))
    else:
        form = CommentForm()
    return render(request, 'posts_add_comment.html', {'form': form,'post':post, 'categories':categories})

@login_required
def posts_edit_comment(request,comment_id):
    categories = Category.objects.all()
    comment = get_object_or_404(Comment,pk=comment_id)
    if request.method == 'POST':
        form = CommentForm(request.POST,instance=comment)
        if form.is_valid():
            comment = form.save()
            return redirect('/posts/'+str(comment.post.id))
    else:
        form = CommentForm(instance=comment)
    return render(request,'posts_add_comment.html',{'form':form,'post':comment.post, 'categories':categories})

#@login_required
#def posts_approve_comment(request, comment_id):
#    comment = get_object_or_404(Comment, pk=comment_id)
#    comment.approve()
#    return redirect('/posts/'+str(comment.post.id))

@login_required
def posts_remove_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.delete()
    return redirect('/posts/'+str(comment.post.id))

@login_required
def posts_delete(request,post_id):
    post = get_object_or_404(Post,pk=post_id)
    post.delete()
    return redirect('/posts/')

#@login_required
#@require_POST
#def comment_like(request):
#    if request.method == 'POST':
#        user = request.user # 로그인한 유저를 가져온다.
#        comment_id = request.POST.get('pk', None)
#        comment = Comment.objects.get(pk = comment_id) #해당 메모 오브젝트를 가져온다.

#        if comment.commentlikes.filter(id = user.id).exists(): #이미 해당 유저가 likes컬럼에 존재하면
#            comment.commentlikes.remove(user) #likes 컬럼에서 해당 유저를 지운다.
#            message = '좋아요를 취소했습니다.'
#        else:
#            comment.commentlikes.add(user)
#            message = '좋아요를 추가했습니다.'

#    context = {'likes_count' : comment.total_likes, 'message' : message}
#    return HttpResponse(json.dumps(context), content_type='application/json')

def show_category(request,hierarchy= None):
    category_slug = hierarchy.split('/')
    category_queryset = list(Category.objects.all())
    all_slugs = [ x.slug for x in category_queryset ]
    parent = None
    for slug in category_slug:
        if slug in all_slugs:
            parent = get_object_or_404(Category,slug=slug,parent=parent)
        else:
            instance = get_object_or_404(Post, slug=slug)
            breadcrumbs_link = instance.get_cat_list()
            category_name = [' '.join(i.split('/')[-1].split('-')) for i in breadcrumbs_link]
            breadcrumbs = zip(breadcrumbs_link, category_name)
            return render(request, "posts_detail.html", {'instance':instance,'breadcrumbs':breadcrumbs})

    return render(request,"posts_categories.html",{'post_set':parent.post_set.all(),'sub_categories':parent.children.all()})

def posts_my(request):
    categories = Category.objects.all()
    user = request.user #로그인한 유저
    posts_list = Post.objects.filter(creator = user)

    paginator = Paginator(posts_list,10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    return render(request,'posts_my.html', {'posts' : posts ,'posts_list' : posts_list, 'categories':categories})

def posts_mycomment(request):
    categories = Category.objects.all()
    user = request.user #로그인한 유저
    comments_list = Comment.objects.filter(creator = user)


    paginator = Paginator(comments_list,10)
    page = request.GET.get('page')
    comments = paginator.get_page(page)

    return render(request,'posts_mycomment.html', {'comments' : comments ,'comments_list' : comments_list, 'categories':categories})

def posts_mylike(request):
    categories = Category.objects.all()
    user = request.user
    posts = Post.objects.all()
    posts_list = []
    for post in posts:
        if post.likes.filter(id = user.id).exists():
            posts_list.append(post)
    
    paginator = Paginator(posts_list,10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    return render(request, 'posts_mylike.html', {'posts':posts, 'categories':categories})
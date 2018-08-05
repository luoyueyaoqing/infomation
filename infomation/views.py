from django.shortcuts import render, HttpResponseRedirect, redirect
from .models import User, Article, Comment, ArticleColumn
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def index_register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if not User.objects.filter(username=username).exists():
            if password1 == password2:
                # user = User(username=username)
                # user.set_password(password1)
                # user.save()
                User.objects.create_user(username=username, password=password1)
                messages.success(request, '注册成功')
                return redirect(to='login')
            else:
                messages.warning(request, '两次密码输入不一致')
        else:
            messages.warning(request, "账号已存在")
    return render(request, 'infosite_register.html')


def index_login(request):
    # request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
    next_url = request.GET.get('next')
    if request.method == "POST":
        # username = request.POST.get('username')
        # password = request.POST.get('password')
        # user = authenticate(username=username, password=password)
        # if user:
        #     login(request, user)
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if next_url:
                return redirect(next_url)
            return redirect('index')
        return HttpResponseRedirect(request.get_full_path())
    return render(request, 'infosite_login.html', {'next_url': next_url})


def index_logout(request):
    logout(request)
    return redirect(to=index)


def index(request):
    article_by_read = Article.objects.order_by('-read_num')[:5]
    article_by_support = Article.objects.order_by('-support_num')[:5]
    article_by_grade = Article.objects.order_by('-garde_num')[:5]
    context = {
        'article_by_read': article_by_read,
        'article_by_support': article_by_support,
        'article_by_grade': article_by_grade,
    }
    return render(request, 'infosite_index.html', context)


def detail(request, id):
    article = Article.objects.get(id=id)
    article.read_num += 1
    article.save()
    article_by_grade = Article.objects.order_by('-garde_num')[:5]
    return render(request, 'infosite_article.html', {'article': article, 'article_by_grade': article_by_grade})


@login_required
def comment(request, id):
    article = Article.objects.get(id=id)
    content = request.GET.get('content')
    article.comment_this(request.user, content)
    return redirect(to=detail, id=id)


@login_required
def delete_article(request, id):
    if request.user.identity != 'Redact':
        return redirect(to=index)
    article = Article.objects.filter(id=id).first()
    if article is not None:
        article.delete()
        messages.success(request, '删除成功')
    else:
        messages.warning(request, '没有这篇文章')
    return redirect(to='redact', id=None)


@login_required
def index_redact(request, id=None):
    if request.user.identity != 'Redact':
        return redirect(to=index)
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        column = request.POST.get('column')
        articlecolumn = ArticleColumn.objects.filter(title=column)
        if articlecolumn.exists():
            article = Article(title=title, content=content, column=articlecolumn.first(), author=request.user)
            article.save()
            messages.success(request, '添加文章成功')
        else:
            messages.warning(request, "栏目不存在")
        return redirect("redact", id=None)
    if request.method == "GET":
        articles = Article.objects.all().order_by('-create_time')
        columns = ArticleColumn.objects.all()
        # 生成paginator对象,定义每页显示5条记录
        paginator = Paginator(articles, 5)
        # 从前端获取当前的页码数,默认为1
        page = request.GET.get('page', 1)
        currentPage = int(page)
        try:
            article_list = paginator.page(page)  # 获取当前页码的记录
        except PageNotAnInteger:
            article_list = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
        except EmptyPage:
            article_list = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容

        if id:
            current_article = Article.objects.filter(id=id).first()
        else:
            current_article = None
        return render(request, 'infosite_redact.html',
locals())
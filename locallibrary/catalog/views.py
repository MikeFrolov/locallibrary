from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView
from django.urls import reverse_lazy
from .models import Author, Book, BookInstance, Genre
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


def redirect_to_next(request):
    next = request.GET.get('next', '/')
    return redirect(next)


@login_required
def index(request):
    """
    Функция отображения для домашней страницы сайта.
    """
    # Генерация "количеств" некоторых главных объектов
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Доступные книги (статус = 'a')
    num_authors = Author.objects.count()  # Метод 'all()' применён по умолчанию.
    num_genres = Genre.objects.all().count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # Отрисовка HTML-шаблона index.html с данными внутри
    # переменной контекста context
    return render(
        request,
        'index.html',
        context={
            'num_books': num_books,
            'num_instances': num_instances,
            'num_authors': num_authors,
            'num_genres': num_genres,
            'num_visits': num_visits
        },
    )


class BookListView(LoginRequiredMixin, ListView):
    model = Book
    paginate_by = 20

    def get_queryset(self):
        return Book.objects.all()


class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book

    def get_context_data(self, **kwargs):
        context = super(BookDetailView, self).get_context_data(**kwargs)
        book = Book.objects.get(id=self.kwargs['pk'])
        num_copies = book.bookinstance_set.all().count()
        context['num_copies'] = num_copies
        return context


class AuthorListView(LoginRequiredMixin, ListView):
    model = Author
    paginate_by = 20


class AuthorDetailView(LoginRequiredMixin, DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, ListView):
    """
    Generic class-based view listing books on loan to current user.
    """
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

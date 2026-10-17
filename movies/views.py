# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()


    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    stats = reviews.aggregate(avg=Avg('rating'), count=Count('id'))
    avg = stats['avg'] or 0
    rounded = round(avg * 2) / 2
    full = int(rounded)
    half = 1 if rounded - full == 0.5 else 0
    empty = 5 - full - half

    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    template_data['avg_rating'] = avg
    template_data['rating_count'] = stats['count']
    template_data['full_stars'] = range(full)
    template_data['half_stars'] = half
    template_data['empty_stars'] = range(empty)
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST.get('rating') in ['1', '2', '3', '4', '5']:
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST.get('comment', ' ')
        review.rating = int(request.POST['rating'])
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)

    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

### new user story
@login_required
def report_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    ## review.flag = True
    review.delete() #test this function
    return redirect('movies.show', id=id)
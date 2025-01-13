from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.validators import MinLengthValidator
from .bookinfo import get_book_info
from accounts.models import User, Team

class Book(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_owner')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='book_team')
    img_path = models.TextField(max_length=300, blank=True, null=True)
    title = models.TextField(max_length=100)
    first_author =models.TextField(max_length=100, blank=True, null=True)
    pub_year = models.IntegerField(default=0)
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    summary = models.TextField(max_length=1000, blank=True, null=True)
    report = models.TextField(max_length=5000)
    good_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    pub_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)
    # edit_count = models.IntegerField(default=0)
    
    def __str__(self):
        return str(self.title) + '/' + str(self.first_author)
    def auto_fill(self): # title, first_authorでGoogleBooks検索、img_path, pub_year, summaryを取得
        info = get_book_info(self.title, self.first_author)
        items = {"first_author": self.first_author, "img_path":self.img_path, "pub_year":self.pub_year, "summary":self.summary}
        for label, item in items.items():
            if item == None or item == "" or item == 0:
                items[label] = info[label]
        self.first_author, self.img_path, self.pub_year, self.summary = items["first_author"], items["img_path"], int(items["pub_year"]), items["summary"]
    class Meta:
        ordering = ('-pub_date',)
        

class Like(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='like_owner')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='like_book')
    
    def __str__(self):
        return str(self.owner) + 'liked' + str(self.book)
    
class Comment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_owner')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='comment_book')
    content = models.TextField(max_length=140)
    date = models.DateTimeField(auto_now_add=True)
    reply_id = models.IntegerField(default=-1)
    
    def __str__(self):
        return str(self.owner) + 'commented to' + str(self.book)
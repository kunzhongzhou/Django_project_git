from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.utils import timezone
from taggit.managers import TaggableManager
from PIL import Image
from django.urls import reverse


class ArticleColumn(models.Model):
    """
    栏目的 Model
    """
    # 栏目标题
    title = models.CharField(max_length=100, blank=True)
    # 创建时间
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class ArticlePost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    column = models.ForeignKey(
        ArticleColumn,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='article'
    )
    tags = TaggableManager(blank=True)
    avatar = models.ImageField(upload_to='article/%Y%m%d/', blank=True)
    # 保存时处理图片
    def save(self, *args, **kwargs):
        # 调用原有的 save() 的功能
        article = super(ArticlePost, self).save(*args, **kwargs)

        # 固定宽度缩放图片大小
        if self.avatar and not kwargs.get('update_fields'):
            image = Image.open(self.avatar)
            (x, y) = image.size
            new_x = 300
            new_y = int(new_x * (y / x))
            resized_image = image.resize((new_x, new_y), Image.ANTIALIAS)
            resized_image.save(self.avatar.path)

        return article

    body = models.TextField()
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    total_views = models.PositiveIntegerField(default=0)

    def was_created_recently(self):
        diff = timezone.now() - self.created

        # if diff.days <= 0 and diff.seconds < 60:
        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            return True
        else:
            return False

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.title

    # 获取文章地址
    def get_absolute_url(self):
        return reverse('article:article_detail', args=[self.id])
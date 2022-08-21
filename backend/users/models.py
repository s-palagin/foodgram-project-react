from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    ROLES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    password = models.CharField(max_length=128, blank=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=ROLES, default='user')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username', 'first_name', 'last_name', 'password',
    ]

    class Meta(AbstractUser.Meta):
        ordering = ('-date_joined',)

    @property
    def is_admin(self):
        return self.role == 'admin'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name=_('Подписчик'),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name=_('Автор рецепта'),
    )

    class Meta:
        ordering = ['-id']
        verbose_name = _('Подписка')
        verbose_name_plural = _('Подписки')
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow',
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='following_me',
            ),
        )

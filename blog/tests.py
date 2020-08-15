from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category
from django.utils import timezone
from django.contrib.auth.models import User


def create_category(name='life', description=''):
    category, is_created = Category.objects.get_or_create(
        name=name,
        description=description,
    )

    return category


def create_post(title, content, author, category=None):
    blog_post = Post.objects.create(
            title = title,
            content = content,
            created = timezone.now(),
            author = author,
            category = category,
        )

    return blog_post


class TestModel(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create(username='smith', password='nopassword')

    def test_category(self):
        category = create_category()
        post_000 = create_post(
            title='first post', 
            content='we are the world', 
            author=self.author_000,
            category=create_category(),
        )

        self.assertEqual(category.post_set.count(), 1) # category.post_set : category에 연결된 post들 불러오기

    def test_post(self):
        category = create_category()
        post_000 = create_post(
            title='first post', 
            content='we are the world', 
            author=self.author_000,
            category=create_category(),
        )

        
class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create(username='smith', password='nopassword')

    def check_navbar(self, soup):
        navbar = soup.find('div', id='navbar')
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)    

    def test_post_list_no_post(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual(soup.title.text, 'blog')

        self.check_navbar(soup)

        self.assertEqual(Post.objects.count(), 0) # 실제 db는 고려하지 않음
        self.assertIn('아직 게시물이 없습니다', soup.body.text)

    def test_post_list_with_post(self):
        #post.objects.all, get, count, create, order_by ..
        post_000 = create_post(
            title='first post', 
            content='we are the world', 
            author=self.author_000,
        )
        post_001 = create_post(
            title='second post', 
            content='second second seoncd', 
            author=self.author_000,
            category=create_category(name='정치/사회')
        )
        self.assertGreater(Post.objects.count(), 0)
        
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        #body = soup.body
        self.assertNotIn('아직 게시물이 없습니다', soup.body.text)
        self.assertIn(post_000.title, soup.body.text)

        soup = BeautifulSoup(response.content, 'html.parser')
        post_000_read_more_btn = soup.body.find('a', id='read-more-post-{}'.format(post_000.pk))
        self.assertEqual(post_000_read_more_btn['href'], post_000.get_absolute_url())

        #category card 에서
        category_card = soup.body.find('div', id='category-card')
        self.assertIn('미분류 (1)', category_card.text) # 미분류 (1) 있어야 함
        self.assertIn('정치/사회 (1)', category_card.text) # 정치/사회 (1) 있어야 함

        #main_div에서
        main_div = soup.body.find('div', id='main_div')
        self.assertIn('정치/사회', main_div.text) # 첫번째 포스트 - 정치/사회 있어야 함
        self.assertIn('미분류', main_div.text) # 두번째 포스트 - 미분류 있어야 함
    
    def test_post_detail(self): # 새 함수 시작마다 새로운 db
        post_000 = create_post(
            title='first post', 
            content='we are the world', 
            author=self.author_000,
            category=create_category(),
        )
        self.assertGreater(Post.objects.count(), 0)
        self.assertEqual(post_000.get_absolute_url(), '/blog/{}/'.format(post_000.pk))
        
        response = self.client.get(post_000.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        self.assertEqual(soup.title.text, '{} - blog'.format(post_000.title))

        self.check_navbar(soup)

        main_div = soup.body.find('div', id='main_div')
        self.assertIn(post_000.title, main_div.text)
        self.assertIn(post_000.author.username, main_div.text)
        self.assertIn(post_000.content, main_div.text)
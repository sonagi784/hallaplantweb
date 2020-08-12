from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post
from django.utils import timezone
from django.contrib.auth.models import User

def create_post(title, content, author):
    blog_post = Post.objects.create(
            title = title,
            content = content,
            created = timezone.now(),
            author = author,
        )
    return blog_post


class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create(username='smith', password='nopassword')

    def check_navbar(self, soup):
        navbar = soup.find('div', id='navbar')
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)    

    def test_post_list(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual(soup.title.text, 'blog')

        self.check_navbar(soup)

        self.assertEqual(Post.objects.count(), 0) # 실제 db는 고려하지 않음
        self.assertIn('아직 게시물이 없습니다', soup.body.text)

        #post.objects.all, get, count, create, order_by ..
        post_000 = create_post(
            'first post', 
            'we are the world', 
            self.author_000,
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
    
    def test_post_detail(self): # 새 함수 시작마다 새로운 db
        post_000 = create_post(
            'first post', 
            'we are the world', 
            self.author_000,
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
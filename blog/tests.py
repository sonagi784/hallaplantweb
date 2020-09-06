from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category, Tag, Comment
from django.utils import timezone
from django.contrib.auth.models import User


def create_category(name='life', description=''):
    category, is_created = Category.objects.get_or_create(
        name=name,
        description=description,
    )
    # test.py는 admin을 거치지 않아 slug가 자동생성되지 않음
    category.slug = category.name.replace(' ', '-').replace('/', '')
    category.save()

    return category

def create_tag(name='some_tag'):
    tag, is_created = Tag.objects.get_or_create(
        name=name,
    )
    tag.slug = tag.name.replace(' ', '-').replace('/', '')
    tag.save()

    return tag

def create_post(title, content, author, category=None):
    blog_post = Post.objects.create(
            title = title,
            content = content,
            created = timezone.now(),
            author = author,
            category = category,
        )

    return blog_post

def create_comment(post, text='default comment', author=None):
    if author is None:
        author, is_created = User.objects.get_or_create(
            username='guest',	
            password='guestpassword'
        )
    comment = Comment.objects.create(
        post=post,	
        text=text,	
        author=author
    )
    return comment

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

    def test_tag(self):
        tag_000 = create_tag(name='bad_guy')
        tag_001 = create_tag(name='america')

        post_000 = create_post(
            title='first post', 
            content='we are the world', 
            author=self.author_000,
        )
        post_000.tags.add(tag_000)
        post_000.tags.add(tag_001)
        post_000.save()
        
        post_001 = create_post(
            title='stay fool, stay hungry',
            content='story about Steve Jobs',
            author = self.author_000,
        )
        post_001.tags.add(tag_001)
        post_001.save()


        self.assertEqual(post_000.tags.count(), 2) # post는 여러개의 tag를 가질수있다
        self.assertEqual(tag_001.post_set.count(), 2) # tag는 여러개의 post에 붙을수있다
        self.assertEqual(tag_001.post_set.first(), post_000) # tag는 자신을 가진 여러개의 post를 가져올수있다
        self.assertEqual(tag_001.post_set.last(), post_001) # tag는 자신을 가진 여러개의 post를 가져올수있다

    def test_post(self):
        category = create_category()
        post_000 = create_post(
            title='first post', 
            content='we are the world', 
            author=self.author_000,
            category=category,
        )

    def test_comment(self):
        post_000 = create_post(
            title='first post', 
            content='we are the world', 
            author=self.author_000,
        )
        self.assertEqual(Comment.objects.count(), 0)
        comment_000 = create_comment(
            post = post_000,
        )
        comment_001 = create_comment(
            post = post_000,
            text = 'second text',
        )

        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(post_000.comment_set.count(), 2)


class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create_user(username='smith', password='nopassword')
        self.user_obama = User.objects.create_user(username='obama', password='nopassword')

    def check_navbar(self, soup):
        navbar = soup.find('div', id='navbar')
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)    

    def check_right_side(self, soup):
        category_card = soup.find('div', id='category-card')
        #category card 에서
        self.assertIn('미분류 (1)', category_card.text) # 미분류 (1) 있어야 함
        self.assertIn('정치/사회 (1)', category_card.text) # 정치/사회 (1) 있어야 함

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
        tag_america = create_tag(name='america')
        post_000.tags.add(tag_america)
        post_000.save()

        post_001 = create_post(
            title='second post', 
            content='second second seoncd', 
            author=self.author_000,
            category=create_category(name='정치/사회'),
        )
        post_001.tags.add(tag_america)
        post_001.save()

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

        self.check_right_side(soup)
        
        #main_div에서
        main_div = soup.find('div', id='main-div')
        self.assertIn('정치/사회', main_div.text) # 첫번째 포스트 - 정치/사회 있어야 함
        self.assertIn('미분류', main_div.text) # 두번째 포스트 - 미분류 있어야 함

        #tag
        post_card_000 = main_div.find('div', id='post-card-{}'.format(post_000.pk))
        self.assertIn('#america', post_card_000.text) # tag가 해당 post 카드마다 있다


    def test_post_detail(self): # 새 함수 시작마다 새로운 db
        category_politics = create_category(name='정치/사회')
        post_000 = create_post(
            title='first post', 
            content='we are the world', 
            author=self.author_000,
            category=category_politics,
        )
        comment_000 = create_comment(post_000, text='test comment', author=self.user_obama)
        comment_001 = create_comment(post_000, text='test comment', author=self.author_000)

        tag_america = create_tag(name='america')
        post_000.tags.add(tag_america)
        post_000.save()

        post_001 = create_post(
            title='second post', 
            content='second second seoncd', 
            author=self.author_000,
        )
        
        self.assertGreater(Post.objects.count(), 0)
        self.assertEqual(post_000.get_absolute_url(), '/blog/{}/'.format(post_000.pk))
        
        response = self.client.get(post_000.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        self.assertEqual(soup.title.text, '{} - blog'.format(post_000.title))

        self.check_navbar(soup)

        main_div = soup.body.find('div', id='main-div')
        self.assertIn(post_000.title, main_div.text)
        self.assertIn(post_000.author.username, main_div.text)
        self.assertIn(post_000.content, main_div.text)

        self.check_right_side(soup)

        # comment
        comment_div = main_div.find('div', id='comment-list')
        self.assertIn(comment_000.author.username, comment_div.text)
        self.assertIn(comment_000.text, comment_div.text)

        # tag
        self.assertIn('#america', main_div.text)

        #category
        self.assertIn(category_politics.name, main_div.text)
        #edit x (로그인x)
        self.assertNotIn('EDIT', main_div.text)
        
        #로그인
        #edit > post.author == 로그인 사용자
        login_success = self.client.login(username='smith', password='nopassword')
        self.assertTrue(login_success)
        response = self.client.get(post_000.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')

        self.assertEqual(post_000.author, self.author_000)
        self.assertIn('EDIT', main_div.text)

        #edit x > post.author != 로그인 사용자
        login_success = self.client.login(username='obama', password='nopassword')
        self.assertTrue(login_success)
        response = self.client.get(post_000.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')

        self.assertNotEqual(post_000.author, self.user_obama)
        self.assertNotIn('EDIT', main_div.text)

        comments_div = main_div.find('div', id='comment-list')
        comment_000_div = comments_div.find('div', id='comment-id-{}'.format(comment_000.pk))
        self.assertIn('edit', comment_000_div.text)
        self.assertIn('delete', comment_000_div.text)

        comment_001_div = comments_div.find('div', id='comment-id-{}'.format(comment_001.pk))
        self.assertNotIn('edit', comment_001_div.text)
        self.assertNotIn('delete', comment_001_div.text)

    def test_post_list_by_category(self):
        category_politics = create_category(name='정치/사회')

        post_000 = create_post(
            title='first post', 
            content='we are the world', 
            author=self.author_000,
        )
        post_001 = create_post(
            title='second post', 
            content='second second seoncd', 
            author=self.author_000,
            category=category_politics,
        )

        response = self.client.get(category_politics.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        main_div = soup.find('div', id='main-div')
        self.assertNotIn('미분류', main_div.text)
        self.assertIn(category_politics.name, main_div.text)


    def test_post_list_no_category(self):
        category_politics = create_category(name='정치/사회')

        post_000 = create_post(
            title='first post', 
            content='we are the world', 
            author=self.author_000,
        )
        post_001 = create_post(
            title='second post', 
            content='second second seoncd', 
            author=self.author_000,
            category=category_politics,
        )
        
        response = self.client.get('/blog/category/_none/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        main_div = soup.find('div', id='main-div')
        self.assertIn('미분류', main_div.text)
        self.assertNotIn(category_politics.name, main_div.text)


    def test_tag_page(self):
        tag_000 = create_tag(name='bad_guy')
        tag_001 = create_tag(name='america')

        post_000 = create_post(
            title='first post', 
            content='we are the world', 
            author=self.author_000,
        )
        post_000.tags.add(tag_000)
        post_000.tags.add(tag_001)
        post_000.save()
        
        post_001 = create_post(
            title='stay fool, stay hungry',
            content='story about Steve Jobs',
            author = self.author_000,
        )
        post_001.tags.add(tag_001)
        post_001.save()

        response = self.client.get(tag_000.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        main_div = soup.find('div', id='main-div')
        blog_h1 = main_div.find('h1', id='post-list-title')
        self.assertIn('#{}'.format(tag_000.name), blog_h1.text)
        self.assertIn(post_000.title, main_div.text)
        self.assertNotIn(post_001.title, main_div.text)


    def test_post_update(self):
        post_000 = create_post(
            title='first post', 
            content='we are the world', 
            author=self.author_000,
        )
        
        self.assertEqual(post_000.get_update_url(), post_000.get_absolute_url() + 'update/')
        
        response = self.client.get(post_000.get_update_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        main_div = soup.find('div', id='main-div')
        
        self.assertNotIn('Created', main_div.text)
        self.assertNotIn('Author', main_div.text)


    def test_post_create(self):
        response = self.client.get('/blog/create/')
        self.assertNotEqual(response.status_code, 200)

        self.client.login(username='smith', password='nopassword')
        response = self.client.get('/blog/create/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')


    def test_new_comment(self):
        post_000 = create_post(
            title='first post', 
            content='we are the world', 
            author=self.author_000,
        )

        self.client.login(username='smith', password='nopassword')
        response = self.client.post(
            post_000.get_absolute_url() + 'new_comment/', 
            {'text': 'A first Test'},
            follow=True,
        )

        
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')
        self.assertIn(post_000.title, main_div.text)
        self.assertIn('A first Test', main_div.text)
